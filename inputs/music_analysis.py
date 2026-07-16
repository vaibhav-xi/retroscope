
from __future__ import annotations

import math

import numpy as np

from inputs.audio import AudioInput
# from time import perf_counter

try:

    from modules.audioreactive._native import _native as _hpss_native

    _HPSS_NATIVE_AVAILABLE = True

except ImportError:

    _hpss_native = None

    _HPSS_NATIVE_AVAILABLE = False

class MusicAnalyzer(AudioInput):

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
    
    _FEATURE_UPDATE_EVERY = 3
    
    _TEMPO_MIN_CONFIDENCE = 0.15
    _PHASE_LOCK_RANGE = 0.3      # only correct phase if an attack lands within +/-30%
    _PHASE_LOCK_STRENGTH = 0.35  # how hard to pull phase toward that attack

    # --- structural arc ---
    _SECTION_SHORT_SECONDS = 2.0
    _SECTION_LONG_SECONDS = 24.0

    # --- key detection (Krumhansl-Schmuckler profiles) ---
    _KEY_PROFILE_MAJOR = np.array(
        [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88],
        dtype=np.float32,
    )

    _KEY_PROFILE_MINOR = np.array(
        [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17],
        dtype=np.float32,
    )

    _KEY_CONFIDENCE_THRESHOLD = 0.55

    # --- chord detection ---
    _CHORD_THIRD_MAJOR = 4
    _CHORD_THIRD_MINOR = 3
    _CHORD_FIFTH = 7
    _CHORD_HOLD_FRAMES = 3
    _CHORD_CONFIDENCE_THRESHOLD = 0.35

    # --- pitch tracking ---
    _BASS_PITCH_MIN_HZ = 41.0    # ~E1
    _BASS_PITCH_MAX_HZ = 262.0   # ~C4
    _MELODY_PITCH_MIN_HZ = 180.0
    _MELODY_PITCH_MAX_HZ = 2000.0
    _PITCH_CONFIDENCE_FLOOR = 0.12

    _INTERVAL_CONSONANCE = (
        1.00,  # 0  unison / octave
        0.05,  # 1  minor 2nd / major 7th
        0.25,  # 2  major 2nd / minor 7th
        0.65,  # 3  minor 3rd / major 6th
        0.75,  # 4  major 3rd / minor 6th
        0.90,  # 5  perfect 4th / perfect 5th
        0.10,  # 6  tritone
    )

    _NOTE_NAMES = (
        "C", "C#", "D", "D#", "E", "F",
        "F#", "G", "G#", "A", "A#", "B",
    )

    # --- meter / bar tracking ---
    _BAR_BEATS = 4

    # --- kick / snare separation ---
    _KICK_MIN_HZ = 30.0
    _KICK_MAX_HZ = 150.0
    _SNARE_MIN_HZ = 150.0
    _SNARE_MAX_HZ = 6000.0

    _KICK_ONSET = (0.14, 1.6, 0.05)
    _SNARE_ONSET = (0.14, 1.5, 0.06)

    # --- band-limited waveform reconstruction ---
    _LOW_WAVE_MAX_HZ = 250.0
    _MID_WAVE_MAX_HZ = 2000.0

    # --- vocal presence heuristic ---
    _VOCAL_FORMANT_MIN_HZ = 300.0
    _VOCAL_FORMANT_MAX_HZ = 3400.0
    _VOCAL_PITCH_MIN_HZ = 120.0
    _VOCAL_PITCH_MAX_HZ = 1100.0
    _VOCAL_PRESENCE_FLOOR = 0.18
    _VOCAL_ONSET = (0.12, 1.5, 0.05)

    def __init__(
        self,
        device=None,
        samplerate: int = 44100,
        block_size: int = 1024,
        spectrum_resolution: int = 64,
        input_gain: float = 1.0,
        channel: int = 0,
        channels: int = 1,
        latency=0.2,
        muted: bool = False,
        stereo: bool = False,
        enable_band_waveforms: bool = True,
        enable_vocal_analysis: bool = True,
        enable_pitch_tracking: bool = True,
        enable_harmony: bool = True,
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
            stereo=stereo,
        )

        #
        # Feature gates. Chord/key detection, pitch tracking and
        # vocal-band analysis are expensive (several extra FFTs
        # and per-tone template matching per audio callback) and
        # most visual modes never read their outputs. Disable
        # whatever a given mode doesn't use.
        #

        self.enable_band_waveforms = enable_band_waveforms
        self.enable_vocal_analysis = enable_vocal_analysis
        self.enable_pitch_tracking = enable_pitch_tracking
        self.enable_harmony = enable_harmony

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

        # --- key detection ---
        self.key_tonic: int = 0
        self.key_is_major: bool = True
        self.key_confidence: float = 0.0
        self.key_name: str = "C major"

        # --- chord detection ---
        self.chord_root: int = 0
        self.chord_is_major: bool = True
        self.chord_confidence: float = 0.0
        self.chord_name: str = "C"
        self.chord_changed: bool = False

        # --- consonance / tension ---
        self.consonance: float = 1.0
        self.tension: float = 0.0

        # --- pitch tracking ---
        self.bass_note_class: int = 0
        self.bass_note_midi: float = 0.0
        self.bass_note_confidence: float = 0.0

        self.melody_note_class: int = 0
        self.melody_note_midi: float = 0.0
        self.melody_note_confidence: float = 0.0

        self.harmonic_interval: int = 0
        self.interval_consonance: float = 1.0

        # --- meter / bar tracking ---
        self.bar_beat_index: int = 0
        self.bar_phase: float = 0.0
        self.on_downbeat: bool = False

        self._beat_count: int = 0
        self._phase_energy = np.zeros(self._BAR_BEATS, dtype=np.float32)

        self._pending_chord = None
        self._pending_chord_count: int = 0

        # --- kick / snare ---
        self.kick_energy: float = 0.0
        self.snare_energy: float = 0.0
        self.kick_hit: bool = False
        self.snare_hit: bool = False

        self._kick_peak = 1e-4
        self._snare_peak = 1e-4
        self._kick_avg = 1e-4
        self._snare_avg = 1e-4

        # --- band-limited waveforms ---
        self.low_waveform = np.zeros(block_size, dtype=np.float32)
        self.mid_waveform = np.zeros(block_size, dtype=np.float32)
        self.high_waveform = np.zeros(block_size, dtype=np.float32)

        # --- vocal presence heuristic ---
        self.vocal_presence: float = 0.0
        self.vocal_activity: float = 0.0
        self.vocal_hit: bool = False
        self.vocal_brightness: float = 0.0

        self.vocal_note_class: int = 0
        self.vocal_note_midi: float = 0.0
        self.vocal_note_confidence: float = 0.0

        self.vocal_waveform = np.zeros(block_size, dtype=np.float32)

        self._formant_flux_peak = 1e-4
        self._vocal_activity_avg = 1e-4
        self._prev_formant_magnitude = None

        self._vocal_waveform_capacity = self._waveform_capacity
        self._vocal_waveform_buffer = np.zeros(
            self._vocal_waveform_capacity, dtype=np.float32
        )
        self._vocal_waveform_write = 0

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
        
        
        self._feature_counter = 0

        self._beat_period_frames = None
        self._beat_phase_counter = 0.0

        #
        # Structural arc state.
        #

        self._short_energy_avg = 1e-4
        self._long_energy_avg = 1e-4
        self._long_energy_peak = 1e-4
        self._section_state_low = True

        with np.errstate(divide="ignore"):
            midi = 69.0 + 12.0 * np.log2(np.maximum(self._freqs, 1e-6) / 440.0)

        pitch_class = np.mod(np.round(midi), 12.0).astype(np.int64)

        self._pitch_valid = self._freqs >= 40.0
        self._pitch_classes_valid = pitch_class[self._pitch_valid]

        self._chroma_smooth = np.zeros(12, dtype=np.float32)

        self._bass_pitch_mask = (
            (self._freqs >= self._BASS_PITCH_MIN_HZ)
            & (self._freqs <= self._BASS_PITCH_MAX_HZ)
        ).astype(np.float32)

        self._melody_pitch_mask = (
            (self._freqs >= self._MELODY_PITCH_MIN_HZ)
            & (self._freqs <= self._MELODY_PITCH_MAX_HZ)
        ).astype(np.float32)

        self._kick_energy_mask = (
            (self._freqs >= self._KICK_MIN_HZ)
            & (self._freqs <= self._KICK_MAX_HZ)
        ).astype(np.float32)

        self._snare_energy_mask = (
            (self._freqs >= self._SNARE_MIN_HZ)
            & (self._freqs <= self._SNARE_MAX_HZ)
        ).astype(np.float32)

        self._low_wave_mask = (
            self._freqs <= self._LOW_WAVE_MAX_HZ
        ).astype(np.float32)

        self._mid_wave_mask = (
            (self._freqs > self._LOW_WAVE_MAX_HZ)
            & (self._freqs <= self._MID_WAVE_MAX_HZ)
        ).astype(np.float32)

        self._high_wave_mask = (
            self._freqs > self._MID_WAVE_MAX_HZ
        ).astype(np.float32)

        self._vocal_formant_mask = (
            (self._freqs >= self._VOCAL_FORMANT_MIN_HZ)
            & (self._freqs <= self._VOCAL_FORMANT_MAX_HZ)
        ).astype(np.float32)

        self._vocal_pitch_mask = (
            (self._freqs >= self._VOCAL_PITCH_MIN_HZ)
            & (self._freqs <= self._VOCAL_PITCH_MAX_HZ)
        ).astype(np.float32)

        self._chord_templates = self._build_chord_templates()
        self._chord_template_norms = (
            np.linalg.norm(self._chord_templates, axis=1) + 1e-9
        )

    # ---------------------------------------------------------
    # Vocal-band waveform history
    # ---------------------------------------------------------

    def _record_vocal_waveform(self, block):

        n = len(block)

        capacity = self._vocal_waveform_capacity

        if n >= capacity:

            self._vocal_waveform_buffer[:] = block[-capacity:]
            self._vocal_waveform_write = 0

            return

        end = self._vocal_waveform_write + n

        if end <= capacity:

            self._vocal_waveform_buffer[self._vocal_waveform_write:end] = block

        else:

            first = capacity - self._vocal_waveform_write

            self._vocal_waveform_buffer[self._vocal_waveform_write:] = block[:first]

            remaining = n - first

            self._vocal_waveform_buffer[:remaining] = block[first:]

        self._vocal_waveform_write = end % capacity

    # ---------------------------------------------------------

    def recent_vocal_waveform(self, sample_count: int) -> np.ndarray:

        capacity = self._vocal_waveform_capacity

        sample_count = max(0, min(sample_count, capacity))

        if sample_count == 0:

            return np.zeros(0, dtype=np.float32)

        start = (self._vocal_waveform_write - sample_count) % capacity

        if start + sample_count <= capacity:

            return self._vocal_waveform_buffer[start:start + sample_count].copy()

        first = capacity - start

        return np.concatenate(
            (
                self._vocal_waveform_buffer[start:],
                self._vocal_waveform_buffer[: sample_count - first],
            )
        )

    # ---------------------------------------------------------
    # Audio thread callback
    # ---------------------------------------------------------

    def _callback(self, indata, frames, time_info, status):
        
        # t0_total = perf_counter()
        
        if status:
            print(f"[audio] status={status}")

        samples = indata[:, 0].astype(np.float32)

        self._record_waveform(samples)

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

        spectrum_complex = np.fft.rfft(windowed)

        magnitude = np.abs(spectrum_complex)

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

        if self.enable_band_waveforms:

            self.low_waveform = np.fft.irfft(
                spectrum_complex * self._low_wave_mask, n=self.block_size
            ).astype(np.float32)

            self.mid_waveform = np.fft.irfft(
                spectrum_complex * self._mid_wave_mask, n=self.block_size
            ).astype(np.float32)

            self.high_waveform = np.fft.irfft(
                spectrum_complex * self._high_wave_mask, n=self.block_size
            ).astype(np.float32)

        if self.enable_vocal_analysis:

            self.vocal_waveform = np.fft.irfft(
                spectrum_complex * self._vocal_formant_mask, n=self.block_size
            ).astype(np.float32)

            self._record_vocal_waveform(self.vocal_waveform)

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
        # NOTE: kept unconditional - attack_hit (and beat_trigger
        # fallback in mode3/mode4) depends on self.percussive.
        #

        self._mag_history[self._mag_history_index] = magnitude
        self._mag_history_index = (
            self._mag_history_index + 1
        ) % self._HPSS_TIME_FRAMES
        self._mag_history_filled = min(
            self._mag_history_filled + 1, self._HPSS_TIME_FRAMES
        )
        
        # t_hpss0 = perf_counter()
        
        if _HPSS_NATIVE_AVAILABLE:

            harmonic_spectrum, percussive_spectrum = _hpss_native.hpss_separate(
                magnitude,
                self._mag_history,
                self._mag_history_filled,
                self._HPSS_FREQ_WINDOW,
            )

        else:

            if self._mag_history_filled >= 3:

                history = self._mag_history[: self._mag_history_filled]

                harmonic_spectrum = np.median(history, axis=0)

            else:

                harmonic_spectrum = magnitude

            percussive_spectrum = self._frequency_median(
                magnitude, self._HPSS_FREQ_WINDOW
            )
        
        # t_hpss1 = perf_counter()

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

        kick_energy_raw = float(
            (percussive_component * self._kick_energy_mask).sum()
        )

        snare_energy_raw = float(
            (percussive_component * self._snare_energy_mask).sum()
        )

        self._kick_peak = max(kick_energy_raw, self._kick_peak * 0.995)

        kick_norm = min(kick_energy_raw / self._kick_peak, 1.0)

        kick_attack = 0.75 if kick_norm > self.kick_energy else 0.2

        self.kick_energy += (kick_norm - self.kick_energy) * kick_attack

        self._snare_peak = max(snare_energy_raw, self._snare_peak * 0.995)

        snare_norm = min(snare_energy_raw / self._snare_peak, 1.0)

        snare_attack = 0.75 if snare_norm > self.snare_energy else 0.2

        self.snare_energy += (snare_norm - self.snare_energy) * snare_attack

        self.kick_hit, self._kick_avg = self._onset(
            self.kick_energy, self._kick_avg, *self._KICK_ONSET
        )

        self.snare_hit, self._snare_avg = self._onset(
            self.snare_energy, self._snare_avg, *self._SNARE_ONSET
        )
        
        self._feature_counter += 1
        update_features = (
            self._feature_counter % self._FEATURE_UPDATE_EVERY == 0
        )

        if self.enable_vocal_analysis:

            formant_magnitude = harmonic_component * self._vocal_formant_mask

            formant_energy = float(formant_magnitude.sum())

            presence_raw = float(
                np.clip(formant_energy / (harmonic_energy + 1e-9), 0.0, 1.0)
            )

            presence_attack = 0.3 if presence_raw > self.vocal_presence else 0.08

            self.vocal_presence += (presence_raw - self.vocal_presence) * presence_attack

            formant_total = formant_energy + 1e-9

            if formant_energy > 1e-6:

                formant_centroid_hz = float(
                    (self._freqs * formant_magnitude).sum()
                ) / formant_total

                formant_centroid_hz = max(
                    formant_centroid_hz, self._VOCAL_FORMANT_MIN_HZ
                )

                brightness = (
                    (np.log(formant_centroid_hz) - np.log(self._VOCAL_FORMANT_MIN_HZ))
                    / (
                        np.log(self._VOCAL_FORMANT_MAX_HZ)
                        - np.log(self._VOCAL_FORMANT_MIN_HZ)
                    )
                )

                brightness = float(np.clip(brightness, 0.0, 1.0))

                self.vocal_brightness += (brightness - self.vocal_brightness) * 0.2

            if self._prev_formant_magnitude is not None:

                formant_rise = formant_magnitude - self._prev_formant_magnitude

                formant_flux = float(np.maximum(formant_rise, 0.0).sum())

            else:

                formant_flux = 0.0

            self._prev_formant_magnitude = formant_magnitude

            self._formant_flux_peak = max(formant_flux, self._formant_flux_peak * 0.995)

            formant_flux_norm = min(formant_flux / self._formant_flux_peak, 1.0)

            vocal_activity_attack = 0.7 if formant_flux_norm > self.vocal_activity else 0.2

            self.vocal_activity += (
                formant_flux_norm - self.vocal_activity
            ) * vocal_activity_attack

            vocal_hit_raw, self._vocal_activity_avg = self._onset(
                self.vocal_activity, self._vocal_activity_avg, *self._VOCAL_ONSET
            )

            self.vocal_hit = bool(
                vocal_hit_raw and self.vocal_presence > self._VOCAL_PRESENCE_FLOOR
            )

            vocal_pitch = self._estimate_pitch(harmonic_component, self._vocal_pitch_mask)

            if (
                vocal_pitch is not None
                and vocal_pitch[2] > self._PITCH_CONFIDENCE_FLOOR
                and self.vocal_presence > self._VOCAL_PRESENCE_FLOOR
            ):

                pitch_class, midi, confidence = vocal_pitch

                self.vocal_note_class = pitch_class
                self.vocal_note_midi += (midi - self.vocal_note_midi) * 0.3
                self.vocal_note_confidence += (
                    confidence - self.vocal_note_confidence
                ) * 0.3

            else:

                self.vocal_note_confidence *= 0.9

        if self.enable_pitch_tracking and update_features:

            bass_pitch = self._estimate_pitch(
                harmonic_component, self._bass_pitch_mask
            )

            if bass_pitch is not None and bass_pitch[2] > self._PITCH_CONFIDENCE_FLOOR:

                pitch_class, midi, confidence = bass_pitch

                self.bass_note_class = pitch_class
                self.bass_note_midi += (midi - self.bass_note_midi) * 0.3
                self.bass_note_confidence += (
                    confidence - self.bass_note_confidence
                ) * 0.3

            else:

                self.bass_note_confidence *= 0.9

            melody_pitch = self._estimate_pitch(
                harmonic_component, self._melody_pitch_mask
            )

            if (
                melody_pitch is not None
                and melody_pitch[2] > self._PITCH_CONFIDENCE_FLOOR
            ):

                pitch_class, midi, confidence = melody_pitch

                self.melody_note_class = pitch_class
                self.melody_note_midi += (midi - self.melody_note_midi) * 0.35
                self.melody_note_confidence += (
                    confidence - self.melody_note_confidence
                ) * 0.35

            else:

                self.melody_note_confidence *= 0.9

            interval = abs(self.bass_note_class - self.melody_note_class) % 12

            self.harmonic_interval = min(interval, 12 - interval)

            self.interval_consonance = float(
                self._INTERVAL_CONSONANCE[self.harmonic_interval]
            )

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

        if self.on_beat:

            self._beat_count += 1

            phase_index = self._beat_count % self._BAR_BEATS

            self._phase_energy[phase_index] += (
                self.bass - self._phase_energy[phase_index]
            ) * 0.3

            downbeat_offset = int(np.argmax(self._phase_energy))

            self.bar_beat_index = (
                self._beat_count - downbeat_offset
            ) % self._BAR_BEATS

            self.on_downbeat = self.bar_beat_index == 0

        else:

            self.on_downbeat = False

        if self._beat_period_frames:

            self.bar_phase = (
                (self.bar_beat_index + self.beat_phase) / self._BAR_BEATS
            ) % 1.0

        else:

            self.bar_phase = 0.0

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
        
        # self._debug_counter = getattr(self, "_debug_counter", 0) + 1
        
        # if self._debug_counter % 40 == 0:

        #     print(
        #         f"[audio] hpss={(t_hpss1 - t_hpss0) * 1000:.2f} ms   "
        #         f"callback_total={(perf_counter() - t0_total) * 1000:.2f} ms"
        #     )

        if self.enable_harmony and update_features:

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

            self._update_key_and_chord()

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

            self.beat_confidence *= 0.9

            return

        bpm = 60.0 * self._tempo_frame_rate / peak_lag

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

    @staticmethod
    def _build_chord_templates():

        templates = np.zeros((24, 12), dtype=np.float32)

        for root in range(12):

            major = np.zeros(12, dtype=np.float32)
            major[root] = 1.0
            major[(root + MusicAnalyzer._CHORD_THIRD_MAJOR) % 12] = 0.85
            major[(root + MusicAnalyzer._CHORD_FIFTH) % 12] = 0.75

            minor = np.zeros(12, dtype=np.float32)
            minor[root] = 1.0
            minor[(root + MusicAnalyzer._CHORD_THIRD_MINOR) % 12] = 0.85
            minor[(root + MusicAnalyzer._CHORD_FIFTH) % 12] = 0.75

            templates[root] = major
            templates[12 + root] = minor

        return templates

    # ---------------------------------------------------------

    def _update_key_and_chord(self):

        chroma = self.chroma

        norm = float(np.linalg.norm(chroma))

        if norm < 1e-6:

            return

        normalized = chroma / norm

        #
        # Key.
        #

        best_key_score = -1e9
        best_key = (self.key_tonic, self.key_is_major)

        for tonic in range(12):

            major_profile = np.roll(self._KEY_PROFILE_MAJOR, tonic)
            minor_profile = np.roll(self._KEY_PROFILE_MINOR, tonic)

            major_score = float(
                np.dot(normalized, major_profile)
                / (np.linalg.norm(major_profile) + 1e-9)
            )

            minor_score = float(
                np.dot(normalized, minor_profile)
                / (np.linalg.norm(minor_profile) + 1e-9)
            )

            if major_score > best_key_score:

                best_key_score = major_score
                best_key = (tonic, True)

            if minor_score > best_key_score:

                best_key_score = minor_score
                best_key = (tonic, False)

        key_confidence = float(np.clip(best_key_score / 6.5, 0.0, 1.0))

        self.key_confidence += (key_confidence - self.key_confidence) * 0.02

        if key_confidence > self._KEY_CONFIDENCE_THRESHOLD:

            if best_key != (self.key_tonic, self.key_is_major):

                self.key_tonic, self.key_is_major = best_key

        self.key_name = (
            f"{self._NOTE_NAMES[self.key_tonic]} "
            f"{'major' if self.key_is_major else 'minor'}"
        )

        #
        # Chord.
        #

        scores = (
            self._chord_templates @ normalized
        ) / self._chord_template_norms

        best_index = int(np.argmax(scores))

        chord_confidence = float(np.clip(scores[best_index], 0.0, 1.0))

        chord_root = best_index % 12
        chord_is_major = best_index < 12

        candidate = (chord_root, chord_is_major)

        self.chord_confidence += (chord_confidence - self.chord_confidence) * 0.15

        if candidate == self._pending_chord:

            self._pending_chord_count += 1

        else:

            self._pending_chord = candidate
            self._pending_chord_count = 1

        self.chord_changed = False

        if (
            self._pending_chord_count >= self._CHORD_HOLD_FRAMES
            and chord_confidence > self._CHORD_CONFIDENCE_THRESHOLD
            and candidate != (self.chord_root, self.chord_is_major)
        ):

            self.chord_root, self.chord_is_major = candidate

            self.chord_name = (
                f"{self._NOTE_NAMES[self.chord_root]}"
                f"{'' if self.chord_is_major else 'm'}"
            )

            self.chord_changed = True

        current_template = self._chord_templates[
            self.chord_root + (0 if self.chord_is_major else 12)
        ]

        current_norm = float(np.linalg.norm(current_template)) + 1e-9

        consonance = float(
            np.clip(
                np.dot(normalized, current_template) / current_norm,
                0.0,
                1.0,
            )
        )

        self.consonance += (consonance - self.consonance) * 0.2

        self.tension = 1.0 - self.consonance

    # ---------------------------------------------------------

    def _estimate_pitch(self, magnitude, mask):

        restricted = magnitude * mask

        total = float(restricted.sum())

        if total <= 1e-9:

            return None

        product = restricted.copy()

        for factor in (2, 3, 4):

            n = len(restricted) // factor

            if n < 2:

                break

            downsampled = np.zeros_like(restricted)
            downsampled[:n] = restricted[::factor][:n]

            product *= downsampled

        peak_index = int(np.argmax(product))

        peak_value = float(product[peak_index])

        if peak_value <= 0.0:

            return None

        product_total = float(product.sum()) + 1e-9

        confidence = float(np.clip(peak_value / product_total * 4.0, 0.0, 1.0))

        freq = float(self._freqs[peak_index])

        if freq <= 1.0:

            return None

        midi = 69.0 + 12.0 * math.log2(freq / 440.0)

        pitch_class = int(round(midi)) % 12

        return pitch_class, midi, confidence

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

    # ---------------------------------------------------------

    @property
    def chord_tones(self):
        """
        (root, third, fifth) pitch classes of the currently detected
        chord.
        """

        third_interval = (
            self._CHORD_THIRD_MAJOR
            if self.chord_is_major
            else self._CHORD_THIRD_MINOR
        )

        return (
            self.chord_root,
            (self.chord_root + third_interval) % 12,
            (self.chord_root + self._CHORD_FIFTH) % 12,
        )
