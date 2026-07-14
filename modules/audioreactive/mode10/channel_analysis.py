from __future__ import annotations

import math

import numpy as np


class ChannelAnalyzer:

    _BASS_MAX_HZ = 250.0
    _MID_MAX_HZ = 2000.0

    def __init__(self, samplerate: int, window_size: int):

        self.window_size = window_size

        self._window = np.hanning(window_size).astype(np.float32)

        freqs = np.fft.rfftfreq(window_size, d=1.0 / samplerate)

        self._bass_mask = (freqs >= 40.0) & (freqs < self._BASS_MAX_HZ)
        self._mid_mask = (freqs >= self._BASS_MAX_HZ) & (freqs < self._MID_MAX_HZ)
        self._high_mask = freqs >= self._MID_MAX_HZ

        self.level: float = 0.0
        self.bass: float = 0.0
        self.mid: float = 0.0
        self.high: float = 0.0

        self._level_peak = 1e-4
        self._bass_peak = 1e-4
        self._mid_peak = 1e-4
        self._high_peak = 1e-4

    # ---------------------------------------------------------

    def analyze(self, samples: np.ndarray):

        if len(samples) < self.window_size:

            pad = np.zeros(self.window_size - len(samples), dtype=np.float32)

            samples = np.concatenate((pad, samples))

        else:

            samples = samples[-self.window_size:]

        rms = float(np.sqrt(np.mean(samples * samples)) + 1e-9)

        self._level_peak = max(rms, self._level_peak * 0.995)

        level_norm = min(rms / self._level_peak, 1.0)

        self.level += (level_norm - self.level) * (
            0.5 if level_norm > self.level else 0.15
        )

        windowed = samples * self._window

        magnitude = np.abs(np.fft.rfft(windowed))

        bass_energy = float(magnitude[self._bass_mask].sum())
        mid_energy = float(magnitude[self._mid_mask].sum())
        high_energy = float(magnitude[self._high_mask].sum())

        self._bass_peak = max(bass_energy, self._bass_peak * 0.995)
        self._mid_peak = max(mid_energy, self._mid_peak * 0.995)
        self._high_peak = max(high_energy, self._high_peak * 0.995)

        bass_norm = min(bass_energy / self._bass_peak, 1.0)
        mid_norm = min(mid_energy / self._mid_peak, 1.0)
        high_norm = min(high_energy / self._high_peak, 1.0)

        self.bass += (bass_norm - self.bass) * (0.6 if bass_norm > self.bass else 0.15)
        self.mid += (mid_norm - self.mid) * (0.6 if mid_norm > self.mid else 0.15)
        self.high += (high_norm - self.high) * (0.7 if high_norm > self.high else 0.2)


def stereo_correlation(left: np.ndarray, right: np.ndarray) -> float:
    """
    +1.0 = perfectly correlated (mono-like - most commercial,
    center-panned content), 0.0 = fully decorrelated (wide stereo),
    -1.0 = out of phase. This is the same quantity a professional
    "phase scope"/correlation meter shows.
    """

    n = min(len(left), len(right))

    if n < 2:

        return 0.0

    l = left[-n:]
    r = right[-n:]

    denom = math.sqrt(float(np.mean(l * l)) * float(np.mean(r * r))) + 1e-9

    correlation = float(np.mean(l * r)) / denom

    return float(np.clip(correlation, -1.0, 1.0))


def rose_curve(
    center,
    base_radius: float,
    left_amount: float,
    right_amount: float,
    left_petals: int,
    right_petals: int,
    phase_left: float,
    phase_right: float,
    correlation: float,
    segments: int,
    include_left: bool = True,
    include_right: bool = True,
):

    cx, cy = center

    theta = np.linspace(0.0, 2.0 * math.pi, segments, endpoint=True)

    roundness = 1.0 - abs(correlation)

    shape_gain = 0.4 + 0.6 * roundness

    r = np.ones_like(theta)

    if include_left:

        r = r + left_amount * shape_gain * np.cos(left_petals * theta + phase_left)

    if include_right:

        r = r + right_amount * shape_gain * np.cos(right_petals * theta + phase_right)

    diagonal_bias = correlation * 0.35 * np.cos(2.0 * (theta - math.pi / 4.0))

    r = r + diagonal_bias

    r = np.clip(r, 0.12, 1.9) * base_radius

    x = cx + r * np.cos(theta)
    y = cy + r * np.sin(theta)

    return np.column_stack([x, y]).astype(np.float32)
