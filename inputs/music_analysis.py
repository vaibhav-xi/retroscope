
from __future__ import annotations

import numpy as np

from inputs.audio import AudioInput


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

        nyquist = samplerate * 0.5

        self._log_lo = np.log(40.0)
        self._log_span = np.log(nyquist) - self._log_lo

        self._prev_magnitude = None
        self._flux_peak = 1e-4

        self._bass_avg = 1e-4
        self._mid_avg = 1e-4
        self._high_avg = 1e-4

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

        self.beat = self.bass_hit

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

    @property
    def lows(self) -> float:

        return (self.bass + self.low_mid) * 0.5

    # ---------------------------------------------------------

    @property
    def highs(self) -> float:

        return (self.high_mid + self.high) * 0.5