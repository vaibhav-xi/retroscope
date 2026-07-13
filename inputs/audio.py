"""
RetroScope

Audio Input

Captures microphone audio and reduces it to a small set of
smoothed, auto-normalized signals:

    level     - overall loudness,        0.0 .. 1.0
    bands     - N smoothed frequency bands (bass..treble)
    spectrum  - a higher resolution spectrum curve, for shapes
    beat      - True on strong bass transients

This module knows nothing about rendering, modules or the engine.
It only listens and analyses.

If no microphone is available (missing hardware, missing
`sounddevice`, permissions, etc.) it fails quietly and simply
reports silence, so the rest of the engine keeps running.
"""

from __future__ import annotations

import numpy as np

try:

    import sounddevice as sd

except ImportError:

    sd = None


class AudioInput:

    def __init__(
        self,
        device=None,
        samplerate: int = 44100,
        block_size: int = 1024,
        band_count: int = 5,
        spectrum_resolution: int = 64,
    ):

        self.device = device
        self.samplerate = samplerate
        self.block_size = block_size
        self.band_count = band_count
        self.spectrum_resolution = spectrum_resolution

        self._stream = None
        self._window = np.hanning(block_size).astype(np.float32)

        #
        # Public, smoothed state.
        #
        # Modules only ever read these. They are written from the
        # audio callback thread; plain numpy/float assignment is
        # sufficiently atomic for our purposes here (no locks).
        #

        self.level: float = 0.0
        self.bands = np.zeros(band_count, dtype=np.float32)
        self.spectrum = np.zeros(spectrum_resolution, dtype=np.float32)
        self.beat: bool = False

        #
        # Internal envelope / auto-gain state.
        #

        self._level_peak = 1e-4
        self._band_peaks = np.full(band_count, 1e-4, dtype=np.float32)
        self._spectrum_peaks = np.full(spectrum_resolution, 1e-4, dtype=np.float32)
        self._bass_average = 1e-4

        #
        # Log-spaced bin edges (bass gets far fewer, wider Hz
        # per-bucket than treble, which matches how we actually
        # perceive frequency).
        #

        self._freqs = np.fft.rfftfreq(block_size, d=1.0 / samplerate)

        nyquist = samplerate * 0.5

        self._band_edges = np.geomspace(40.0, nyquist, band_count + 1)
        self._spectrum_edges = np.geomspace(40.0, nyquist, spectrum_resolution + 1)

        self._available = sd is not None

    # ---------------------------------------------------------

    def start(self):

        if not self._available:

            print(
                "[AudioInput] sounddevice is not installed - "
                "running silent."
            )

            return

        try:

            self._stream = sd.InputStream(
                device=self.device,
                channels=1,
                samplerate=self.samplerate,
                blocksize=self.block_size,
                callback=self._callback,
            )

            self._stream.start()

        except Exception as exc:

            print(
                f"[AudioInput] could not open input device "
                f"({exc}) - running silent."
            )

            self._stream = None

    # ---------------------------------------------------------

    def stop(self):

        if self._stream is not None:

            self._stream.stop()
            self._stream.close()

            self._stream = None

    # ---------------------------------------------------------
    # Audio thread callback
    # ---------------------------------------------------------

    def _callback(self, indata, frames, time_info, status):

        samples = indata[:, 0].astype(np.float32)

        #
        # Overall loudness, auto-normalized against a slowly
        # decaying peak so it adapts to any microphone / gain.
        #

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

        #
        # Spectrum.
        #

        windowed = samples * self._window

        magnitude = np.abs(np.fft.rfft(windowed))

        new_bands = self._bucket(
            magnitude,
            self._band_edges,
            self._band_peaks,
        )

        self.bands = self._smooth(
            self.bands,
            new_bands,
            attack=0.7,
            release=0.12,
        )

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

        #
        # Simple bass-driven transient / beat detector.
        #

        bass = float(new_bands[0]) if len(new_bands) else 0.0

        self._bass_average += (bass - self._bass_average) * 0.05

        self.beat = bass > (self._bass_average * 1.5 + 0.05)

    # ---------------------------------------------------------

    @staticmethod
    def _smooth(current, target, attack, release):

        rate = np.where(
            target > current,
            attack,
            release,
        )

        return current + (target - current) * rate

    # ---------------------------------------------------------

    def _bucket(self, magnitude, edges, peaks):
        """
        Average FFT magnitude into log-spaced buckets, then
        normalize each bucket against its own slowly decaying
        peak (auto-gain per band).
        """

        count = len(edges) - 1

        out = np.empty(count, dtype=np.float32)

        for i in range(count):

            lo = np.searchsorted(self._freqs, edges[i])
            hi = np.searchsorted(self._freqs, edges[i + 1])

            if hi <= lo:
                hi = lo + 1

            segment = magnitude[lo:hi]

            out[i] = segment.mean() if segment.size else 0.0

        peaks[:] = np.maximum(out, peaks * 0.995)

        return np.clip(out / peaks, 0.0, 1.0)
