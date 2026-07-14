
from __future__ import annotations

import numpy as np

from inputs.audio import AudioInput


class MusicAnalyzer(AudioInput):
    """
    Everything Mode 1-4 previously got from here was "loudness in five
    buckets": five FFT bands, smoothed, plus a same-band onset test.
    That's the Winamp/AVS-era toolkit, and it's why the geometry on top
    of it - however elaborate - still reads as a skinned visualizer.

    This adds four things a "visualizer" doesn't have:

    1. Tempo/beat tracking (bpm, beat_phase, on_beat, beat_confidence)
       - an actual estimated tempo with a phase-locked pulse, instead of
       a threshold that fires identically on a 90 BPM kick and a 174 BPM
       kick.

    2. Percussive / harmonic separation (percussive, harmonic, attack,
       attack_hit) - a lightweight real-time HPSS (median-filter based,
       Fitzgerald-style) so a kick drum and a sustained bass note, which
       used to live in the same "bass" bucket, now drive visibly
       different things: sharp geometry snaps vs. smooth continuous
       motion.

    3. A structural energy arc (section_energy, energy_trend, build_up,
       drop) - a short-term vs. long-term loudness comparison so the
       system has *some* notion of "this is a quiet section" vs. "this
       is the loudest part of the track" and can tell a build-up from a
       drop, instead of being purely frame-to-frame reactive.

    4. A cheap 12-bin chroma vector + harmonic_change novelty - not a
       real key/chord detector, just pitch-class energy, but enough to
       give a "the harmony just moved" signal for color/shape choices
       that isn't just spectral brightness.

    None of this is state-of-the-art MIR - there's no HMM/dynamic
    programming beat tracker and no real chord recognition, both of
    which need more history and CPU than a Raspberry Pi 3B audio
    callback running at ~43 Hz can spend. What's here is the cheap end
    of each of those techniques, chosen to actually change what the
    geometry does, not just to add more numbers to log.

    `bass` / `low_mid` / `mid` / `high_mid` / `high`, and the matching
    `bass_hit` / `mid_hit` / `high_hit`, are unchanged and still mean
    exactly what they meant before - band energy and same-band onset.
    `beat` used to just alias `bass_hit`; it now means "the tempo
    tracker's phase-locked pulse fired," which is a real behavior
    change for anything that was reading `.beat` expecting a raw bass
    transient (nothing in mode1-4 was, as of this change).
    """

    _BAND_SMOOTHING = (
        (0.55, 0.10),   # bass
        (0.60, 0.12),   # low_mid
        (0.65, 0.15),   # mid
        (0.75, 0.20),   # high_mid
        (0.85, 0.28),   # high
    )

    _BASS_ONSET = (0.05, 1.5, 0.05)
    _MID_ONSET = (0.10, 1.35, 0.06)
    _HIGH_ONSET = (0.15, 1.7, 0.05)
    _ATTACK_ONSET = (0.12, 1.6, 0.05)

    # --- percussive / harmonic separation ---
    _HPSS_TIME_FRAMES = 17      # ~0.4s of history, median along time -> harmonic
    _HPSS_FREQ_WINDOW = 17      # bins, median along frequency -> percussive

    # --- tempo tracking ---
    _TEMPO_HISTORY_SECONDS = 8.0
    _TEMPO_MIN_BPM = 70.0
    _TEMPO_MAX_BPM = 190.0
    _TEMPO_UPDATE_EVERY = 12    # recompute autocorrelation every N callbacks
    _TEMPO_MIN_CONFIDENCE = 0.15
    _PHASE_LOCK_RANGE = 0.3      # only correct phase if an attack lands within +/-30%
    _PHASE_LOCK_STRENGTH = 0.35  # how hard to pull phase toward that attack

    # --- structural arc ---
    _SECTION_SHORT_SECONDS = 2.0
    _SECTION_LONG_SECONDS = 24.0

    def __init__(
        self,
        device=None,
        samplerate: int = 44100,
        block_size: int = 1024,
        spectrum_resolution: int = 64,
        input_gain: float = 1.0,
        channel: int = 0,
        channels: int = 1,
        latency=None,
        muted: bool = False,
    ):

        super().__init__(
            device=device,
            samplerate=samplerate,
            block_size=block_size,
            band_count=5,
            spectrum_resolution=spectrum_resolution,
            input_gain=input_gain,
            channel=channel,
            channels=channels,
            latency=latency,
            muted=muted,
        )

        self.bass: float = 0.0
        self.low_mid: float = 0.0
        self.mid: float = 0.0
        self.high_mid: float = 0.0
        self.high: float = 0.0

        self.centroid: float = 0.0
        self.flux: float = 0.0

        self.bass_hit: bool = False
        self.mid_hit: bool = False
        self.high_hit: bool = False

        # --- percussive / harmonic separation ---
        self.percussive: float = 0.0
        self.harmonic: float = 0.0
        self.attack: float = 0.0
        self.attack_hit: bool = False

        # --- tempo / beat tracking ---
        self.bpm: float = 0.0
        self.beat_phase: float = 0.0
        self.beat_confidence: float = 0.0
        self.on_beat: bool = False

        # --- structural arc ---
        self.section_energy: float = 0.0
        self.energy_trend: float = 0.0
        self.build_up: bool = False
        self.drop: bool = False

        # --- lightweight harmony ---
        self.chroma = np.zeros(12, dtype=np.float32)
        self.harmonic_change: float = 0.0

        nyquist = samplerate * 0.5

        self._log_lo = np.log(40.0)
        self._log_span = np.log(nyquist) - self._log_lo

        self._prev_magnitude = None
        self._flux_peak = 1e-4

        self._bass_avg = 1e-4
        self._mid_avg = 1e-4
        self._high_avg = 1e-4
        self._attack_avg = 1e-4

        #
        # Percussive/harmonic separation buffers.
        #

        num_bins = block_size // 2 + 1

        self._mag_history = np.zeros(
            (self._HPSS_TIME_FRAMES, num_bins), dtype=np.float32
        )
        self._mag_history_index = 0
        self._mag_history_filled = 0

        self._percussive_peak = 1e-4
        self._harmonic_peak = 1e-4
        self._prev_percussive = None

        #
        # Tempo tracking buffers.
        #

        self._tempo_frame_rate = samplerate / block_size

        tempo_frames = max(
            8, int(self._TEMPO_HISTORY_SECONDS * self._tempo_frame_rate)
        )

        self._onset_history = np.zeros(tempo_frames, dtype=np.float32)
        self._onset_write = 0
        self._onset_filled = 0
        self._tempo_counter = 0

        self._beat_period_frames = None
        self._beat_phase_counter = 0.0

        #
        # Structural arc state.
        #

        self._short_energy_avg = 1e-4
        self._long_energy_avg = 1e-4
        self._long_energy_peak = 1e-4
        self._section_state_low = True

        #
        # Chroma: map each FFT bin to a pitch class (0-11), ignoring
        # sub-40Hz bins (too close to DC / rumble to be tonal).
        #

        with np.errstate(divide="ignore"):
            midi = 69.0 + 12.0 * np.log2(np.maximum(self._freqs, 1e-6) / 440.0)

        pitch_class = np.mod(np.round(midi), 12.0).astype(np.int64)

        self._pitch_valid = self._freqs >= 40.0
        self._pitch_classes_valid = pitch_class[self._pitch_valid]

        self._chroma_smooth = np.zeros(12, dtype=np.float32)

    # ---------------------------------------------------------
    # Audio thread callback
    # ---------------------------------------------------------

    def _callback(self, indata, frames, time_info, status):

        samples = indata[:, 0].astype(np.float32)

        rms = float(
            np.sqrt(np.mean(samples * samples)) + 1e-9
        )

        self._level_peak = max(
            rms,
            self._level_peak * 0.999,
        )

        level = min(rms / self._level_peak, 1.0)

        attack = 0.6 if level > self.level else 0.15

        self.level += (level - self.level) * attack

        windowed = samples * self._window

        magnitude = np.abs(np.fft.rfft(windowed))

        new_bands = self._bucket(
            magnitude,
            self._band_edges,
            self._band_peaks,
        )

        self.bands = self._smooth_bands(self.bands, new_bands)

        (
            self.bass,
            self.low_mid,
            self.mid,
            self.high_mid,
            self.high,
        ) = self.bands.tolist()

        new_spectrum = self._bucket(
            magnitude,
            self._spectrum_edges,
            self._spectrum_peaks,
        )

        self.spectrum = self._smooth(
            self.spectrum,
            new_spectrum,
            attack=0.8,
            release=0.2,
        )

        total = float(magnitude.sum()) + 1e-9

        centroid_hz = float((self._freqs * magnitude).sum()) / total

        centroid_hz = max(centroid_hz, 40.0)

        centroid = (
            (np.log(centroid_hz) - self._log_lo) / self._log_span
        )

        centroid = float(np.clip(centroid, 0.0, 1.0))

        self.centroid += (centroid - self.centroid) * 0.2

        if self._prev_magnitude is not None:

            rise = magnitude - self._prev_magnitude

            flux = float(np.maximum(rise, 0.0).sum())

        else:

            flux = 0.0

        self._prev_magnitude = magnitude

        self._flux_peak = max(flux, self._flux_peak * 0.995)

        flux_norm = min(flux / self._flux_peak, 1.0)

        flux_attack = 0.7 if flux_norm > self.flux else 0.2

        self.flux += (flux_norm - self.flux) * flux_attack

        self.bass_hit, self._bass_avg = self._onset(
            self.bass, self._bass_avg, *self._BASS_ONSET
        )

        self.mid_hit, self._mid_avg = self._onset(
            self.mid, self._mid_avg, *self._MID_ONSET
        )

        self.high_hit, self._high_avg = self._onset(
            self.high, self._high_avg, *self._HIGH_ONSET
        )

        #
        # Percussive / harmonic separation.
        #

        self._mag_history[self._mag_history_index] = magnitude
        self._mag_history_index = (
            self._mag_history_index + 1
        ) % self._HPSS_TIME_FRAMES
        self._mag_history_filled = min(
            self._mag_history_filled + 1, self._HPSS_TIME_FRAMES
        )

        if self._mag_history_filled >= 3:

            history = self._mag_history[: self._mag_history_filled]

            harmonic_spectrum = np.median(history, axis=0)

        else:

            harmonic_spectrum = magnitude

        percussive_spectrum = self._frequency_median(
            magnitude, self._HPSS_FREQ_WINDOW
        )

        h_sq = harmonic_spectrum * harmonic_spectrum
        p_sq = percussive_spectrum * percussive_spectrum

        denom = h_sq + p_sq + 1e-9

        percussive_component = magnitude * (p_sq / denom)
        harmonic_component = magnitude * (h_sq / denom)

        percussive_energy = float(percussive_component.sum())
        harmonic_energy = float(harmonic_component.sum())

        self._percussive_peak = max(
            percussive_energy, self._percussive_peak * 0.995
        )

        perc_norm = min(percussive_energy / self._percussive_peak, 1.0)

        p_attack = 0.75 if perc_norm > self.percussive else 0.2

        self.percussive += (perc_norm - self.percussive) * p_attack

        self._harmonic_peak = max(
            harmonic_energy, self._harmonic_peak * 0.995
        )

        harm_norm = min(harmonic_energy / self._harmonic_peak, 1.0)

        h_attack = 0.5 if harm_norm > self.harmonic else 0.15

        self.harmonic += (harm_norm - self.harmonic) * h_attack

        self.attack_hit, self._attack_avg = self._onset(
            self.percussive, self._attack_avg, *self._ATTACK_ONSET
        )

        self.attack = self.percussive

        #
        # Tempo tracking: build an onset envelope from *percussive*
        # energy specifically, so a sustained bassline or pad doesn't
        # get mistaken for a beat the way raw broadband flux would.
        #

        if self._prev_percussive is not None:

            onset_strength = max(0.0, percussive_energy - self._prev_percussive)

        else:

            onset_strength = 0.0

        self._prev_percussive = percussive_energy

        self._onset_history[self._onset_write] = onset_strength

        self._onset_write = (
            self._onset_write + 1
        ) % len(self._onset_history)

        self._onset_filled = min(
            self._onset_filled + 1, len(self._onset_history)
        )

        self._tempo_counter += 1

        if (
            self._tempo_counter >= self._TEMPO_UPDATE_EVERY
            and self._onset_filled >= len(self._onset_history) // 2
        ):

            self._tempo_counter = 0

            self._update_tempo_estimate()

        self._advance_beat_phase()

        self.beat = self.on_beat

        #
        # Structural energy arc: short-term loudness vs. a slow,
        # long-term baseline. Not "verse/chorus" detection - just
        # enough to tell a quiet section from a loud one and notice
        # when the track jumps from one to the other.
        #

        short_rate = 1.0 / (self._SECTION_SHORT_SECONDS * self._tempo_frame_rate)
        long_rate = 1.0 / (self._SECTION_LONG_SECONDS * self._tempo_frame_rate)

        self._short_energy_avg += (rms - self._short_energy_avg) * short_rate
        self._long_energy_avg += (rms - self._long_energy_avg) * long_rate

        self._long_energy_peak = max(
            self._long_energy_avg, self._long_energy_peak * 0.9999
        )

        self.section_energy = float(
            np.clip(
                self._long_energy_avg / (self._long_energy_peak + 1e-9),
                0.0,
                1.0,
            )
        )

        trend = (
            (self._short_energy_avg - self._long_energy_avg)
            / (self._long_energy_avg + 1e-6)
        )

        self.energy_trend = float(np.clip(trend, -1.0, 1.0))

        self.build_up = self.energy_trend > 0.25

        was_low = self._section_state_low

        self._section_state_low = self.energy_trend < 0.1

        self.drop = was_low and self.energy_trend > 0.6

        #
        # Lightweight chroma + harmonic-change novelty.
        #

        chroma = np.bincount(
            self._pitch_classes_valid,
            weights=magnitude[self._pitch_valid],
            minlength=12,
        ).astype(np.float32)

        chroma_total = float(chroma.sum()) + 1e-9

        chroma /= chroma_total

        prev_chroma = self._chroma_smooth.copy()

        self._chroma_smooth += (chroma - self._chroma_smooth) * 0.15

        self.chroma = self._chroma_smooth

        prev_norm = float(np.linalg.norm(prev_chroma))
        curr_norm = float(np.linalg.norm(self._chroma_smooth))

        if prev_norm > 1e-6 and curr_norm > 1e-6:

            cosine = float(
                np.dot(prev_chroma, self._chroma_smooth) / (prev_norm * curr_norm)
            )

            change = float(np.clip(1.0 - cosine, 0.0, 1.0))

        else:

            change = 0.0

        self.harmonic_change += (change - self.harmonic_change) * 0.3

    # ---------------------------------------------------------

    def _update_tempo_estimate(self):

        n = self._onset_filled

        if n < 8:

            return

        if self._onset_filled < len(self._onset_history):

            signal = self._onset_history[:n].copy()

        else:

            signal = np.concatenate(
                (
                    self._onset_history[self._onset_write:],
                    self._onset_history[: self._onset_write],
                )
            )

        signal = signal - signal.mean()

        if not np.any(signal):

            return

        size = 1

        while size < 2 * len(signal):

            size *= 2

        spectrum = np.fft.rfft(signal, n=size)

        autocorr = np.fft.irfft(spectrum * np.conj(spectrum), n=size)[: len(signal)]

        if autocorr[0] <= 1e-9:

            return

        min_lag = max(
            1, int(round(self._tempo_frame_rate * 60.0 / self._TEMPO_MAX_BPM))
        )

        max_lag = int(
            round(self._tempo_frame_rate * 60.0 / self._TEMPO_MIN_BPM)
        )

        max_lag = min(max_lag, len(autocorr) - 1)

        if max_lag <= min_lag:

            return

        window = autocorr[min_lag : max_lag + 1]

        peak_index = int(np.argmax(window))
        peak_lag = min_lag + peak_index
        peak_value = window[peak_index]

        confidence = float(np.clip(peak_value / (autocorr[0] + 1e-9), 0.0, 1.0))

        if confidence < self._TEMPO_MIN_CONFIDENCE:

            # Too ambiguous a beat to commit to a new number - keep the
            # last stable estimate and just let confidence bleed off.
            self.beat_confidence *= 0.9

            return

        bpm = 60.0 * self._tempo_frame_rate / peak_lag

        # Autocorrelation-based tempo estimates commonly lock onto a
        # half or double of the "felt" tempo. If we already have a
        # stable estimate, prefer whichever octave is closer to it
        # instead of letting the estimate flip back and forth.
        if self.bpm > 0.0:

            for factor in (2.0, 0.5):

                candidate = bpm * factor

                if (
                    self._TEMPO_MIN_BPM <= candidate <= self._TEMPO_MAX_BPM
                    and abs(candidate - self.bpm) < abs(bpm - self.bpm)
                ):

                    bpm = candidate

                    break

        if self.bpm <= 0.0:

            self.bpm = bpm

        else:

            self.bpm += (bpm - self.bpm) * 0.25

        self._beat_period_frames = 60.0 * self._tempo_frame_rate / self.bpm

        self.beat_confidence += (confidence - self.beat_confidence) * 0.3

    # ---------------------------------------------------------

    def _advance_beat_phase(self):
        """
        Advance a phase counter at the estimated tempo, and gently pull
        it into lock with real percussive attacks - a simple PLL, not
        a state-space beat tracker. `on_beat` fires once per predicted
        beat, quantized to the tempo grid, rather than once per raw
        transient.
        """

        if not self._beat_period_frames:

            self.beat_phase = 0.0
            self.on_beat = False

            return

        period = self._beat_period_frames

        self._beat_phase_counter += 1.0

        if self._beat_phase_counter >= period:

            self._beat_phase_counter -= period

        phase = self._beat_phase_counter / period

        if self.attack_hit and self.beat_confidence > 0.3:

            distance = min(phase, 1.0 - phase)

            if distance < self._PHASE_LOCK_RANGE:

                # Signed offset from the nearest predicted beat (0 or
                # `period`), pulled toward zero rather than snapped.
                offset = (
                    self._beat_phase_counter
                    if phase <= 0.5
                    else self._beat_phase_counter - period
                )

                self._beat_phase_counter -= offset * self._PHASE_LOCK_STRENGTH

                self._beat_phase_counter %= period

                phase = self._beat_phase_counter / period

        previous_phase = self.beat_phase

        self.beat_phase = phase

        self.on_beat = phase < previous_phase

    # ---------------------------------------------------------

    def _smooth_bands(self, current, target):

        out = np.empty_like(current)

        for i, (attack, release) in enumerate(self._BAND_SMOOTHING):

            rate = attack if target[i] > current[i] else release

            out[i] = current[i] + (target[i] - current[i]) * rate

        return out

    # ---------------------------------------------------------

    @staticmethod
    def _onset(value, rolling_avg, decay, multiplier, floor):

        rolling_avg = rolling_avg + (value - rolling_avg) * decay

        hit = value > (rolling_avg * multiplier + floor)

        return bool(hit), rolling_avg

    # ---------------------------------------------------------

    @staticmethod
    def _frequency_median(spectrum, window):
        """Sliding median along the frequency axis of a single frame."""

        half = window // 2

        padded = np.pad(spectrum, (half, half), mode="edge")

        shape = (spectrum.size, window)
        strides = (padded.strides[0], padded.strides[0])

        windows = np.lib.stride_tricks.as_strided(
            padded, shape=shape, strides=strides
        )

        return np.median(windows, axis=1)

    # ---------------------------------------------------------

    @property
    def lows(self) -> float:

        return (self.bass + self.low_mid) * 0.5

    # ---------------------------------------------------------

    @property
    def highs(self) -> float:

        return (self.high_mid + self.high) * 0.5
