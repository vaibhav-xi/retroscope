
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
        input_gain: float = 4.0,
        channel: int = 0,
        channels: int = 1,
        latency=None,
        muted: bool = False,
    ):

        self.device = device
        self.samplerate = samplerate
        self.block_size = block_size
        self.band_count = band_count
        self.spectrum_resolution = spectrum_resolution

        self.input_gain = max(0.0, float(input_gain))
        self.channel = channel
        self.channels = max(channels, channel + 1)
        self.latency = latency
        self.muted = bool(muted)

        self._stream = None
        self._window = np.hanning(block_size).astype(np.float32)
        
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

        self._freqs = np.fft.rfftfreq(block_size, d=1.0 / samplerate)

        nyquist = samplerate * 0.5

        self._band_edges = np.geomspace(40.0, nyquist, band_count + 1)
        self._spectrum_edges = np.geomspace(40.0, nyquist, spectrum_resolution + 1)

        self._available = sd is not None

    # ---------------------------------------------------------
    # Gain / mute controls
    # ---------------------------------------------------------

    def set_gain(self, gain: float):
        """Set the linear input gain multiplier (0.0 = silent, 1.0 = unity)."""

        self.input_gain = max(0.0, float(gain))

    # ---------------------------------------------------------

    @property
    def gain_db(self) -> float:
        """Current input gain expressed in dB (-inf if fully muted/zeroed)."""

        if self.input_gain <= 0.0:

            return float("-inf")

        return float(20.0 * np.log10(self.input_gain))

    # ---------------------------------------------------------

    def set_gain_db(self, db: float):
        """Set the input gain from a dB value (0 dB = unity gain)."""

        self.input_gain = float(10.0 ** (db / 20.0))

    # ---------------------------------------------------------

    def set_muted(self, muted: bool):

        self.muted = bool(muted)

    # ---------------------------------------------------------

    def set_channel(self, channel: int):
        """
        Switch which captured channel is analyzed. Only valid for
        channel indices already within `self.channels` - reopen
        the stream (stop/start) after raising `self.channels` if
        you need to select a channel beyond what's currently open.
        """

        if channel >= self.channels:

            raise ValueError(
                f"channel {channel} is outside the "
                f"{self.channels}-channel stream currently open "
                f"- restart with channels >= {channel + 1}"
            )

        self.channel = channel

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
                channels=self.channels,
                samplerate=self.samplerate,
                blocksize=self.block_size,
                latency=self.latency,
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

        samples = indata[:, self.channel].astype(np.float32)

        if self.muted:

            samples = samples * 0.0

        elif self.input_gain != 1.0:

            samples = np.clip(samples * self.input_gain, -1.0, 1.0)
            
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