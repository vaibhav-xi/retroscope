from __future__ import annotations

import platform

import numpy as np

try:

    import sounddevice as sd

except ImportError:

    sd = None


_IS_WINDOWS = platform.system() == "Windows"


class AudioInput:

    def __init__(
        self,
        device=None,
        samplerate: int = 44100,
        block_size: int = 1024,
        band_count: int = 5,
        spectrum_resolution: int = 64,
        input_gain: float = 1.0,
        channel: int = 0,
        channels: int = 1,
        latency=None,
        muted: bool = False,
        stereo: bool = False,
        loopback: bool = False,
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

        self.stereo_requested = bool(stereo)
        self.stereo_available = False

        # WASAPI "record what you hear" loopback. Only meaningful on
        # Windows - ignored everywhere else so mac/BlackHole setups
        # keep working unchanged.
        self.loopback = bool(loopback) and _IS_WINDOWS

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

        self.waveform_history_seconds = 2.0

        self._waveform_capacity = max(
            block_size * 2,
            int(self.waveform_history_seconds * samplerate),
        )

        self._waveform_buffer = np.zeros(self._waveform_capacity, dtype=np.float32)
        self._waveform_write = 0

        self._left_buffer = np.zeros(self._waveform_capacity, dtype=np.float32)
        self._right_buffer = np.zeros(self._waveform_capacity, dtype=np.float32)
        self._stereo_write = 0

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

        if channel >= self.channels:

            raise ValueError(
                f"channel {channel} is outside the "
                f"{self.channels}-channel stream currently open "
                f"- restart with channels >= {channel + 1}"
            )

        self.channel = channel

    # ---------------------------------------------------------
    # WASAPI loopback helpers (Windows only)
    # ---------------------------------------------------------

    @staticmethod
    def list_wasapi_output_devices():
        if sd is None:

            print("[AudioInput] sounddevice is not installed.")
            return

        hostapis = sd.query_hostapis()

        wasapi_index = next(
            (i for i, api in enumerate(hostapis) if "WASAPI" in api["name"]),
            None,
        )

        if wasapi_index is None:

            print("[AudioInput] WASAPI is not available on this system.")
            return

        for i, info in enumerate(sd.query_devices()):

            if info["hostapi"] == wasapi_index and info["max_output_channels"] >= 1:

                print(f"[{i}] {info['name']}  ({info['max_output_channels']} ch)")

    # ---------------------------------------------------------

    @staticmethod
    def _find_wasapi_loopback_target(device):

        if sd is None:

            raise RuntimeError("sounddevice is not installed")

        hostapis = sd.query_hostapis()

        wasapi_index = next(
            (i for i, api in enumerate(hostapis) if "WASAPI" in api["name"]),
            None,
        )

        if wasapi_index is None:

            raise RuntimeError("WASAPI host API not available on this system")

        if device is None:

            output_index = hostapis[wasapi_index]["default_output_device"]

            if output_index < 0:

                raise RuntimeError("no default WASAPI output device")

            return output_index

        devices = sd.query_devices()

        if isinstance(device, int):

            info = devices[device]

            if info["hostapi"] != wasapi_index or info["max_output_channels"] < 1:

                raise RuntimeError(f"device {device} is not a WASAPI output device")

            return device

        # Treat `device` as a name substring, e.g. "Speakers", "Realtek".
        name = str(device).lower()

        for i, info in enumerate(devices):

            if (
                info["hostapi"] == wasapi_index
                and info["max_output_channels"] >= 1
                and name in info["name"].lower()
            ):

                return i

        raise RuntimeError(f"no WASAPI output device matching '{device}'")

    # ---------------------------------------------------------

    def _retune(self, samplerate: int):
        
        self.samplerate = samplerate

        self._freqs = np.fft.rfftfreq(self.block_size, d=1.0 / samplerate)

        nyquist = samplerate * 0.5

        self._band_edges = np.geomspace(40.0, nyquist, self.band_count + 1)
        self._spectrum_edges = np.geomspace(40.0, nyquist, self.spectrum_resolution + 1)

        self._waveform_capacity = max(
            self.block_size * 2,
            int(self.waveform_history_seconds * samplerate),
        )

        self._waveform_buffer = np.zeros(self._waveform_capacity, dtype=np.float32)
        self._waveform_write = 0

        self._left_buffer = np.zeros(self._waveform_capacity, dtype=np.float32)
        self._right_buffer = np.zeros(self._waveform_capacity, dtype=np.float32)
        self._stereo_write = 0

    # ---------------------------------------------------------

    def _open_wasapi_loopback_stream(self):

        output_index = self._find_wasapi_loopback_target(self.device)

        info = sd.query_devices(output_index)

        samplerate = int(info["default_samplerate"])
        channels = max(2, min(max(self.channels, 2), info["max_output_channels"]))

        if samplerate != self.samplerate:

            print(
                f"[AudioInput] WASAPI loopback device runs at "
                f"{samplerate} Hz, adjusting from {self.samplerate} Hz."
            )

            self._retune(samplerate)

        self.channels = channels

        self._stream = sd.InputStream(
            device=output_index,
            channels=channels,
            samplerate=samplerate,
            blocksize=self.block_size,
            latency=self.latency,
            dtype="float32",
            extra_settings=sd.WasapiSettings(loopback=True),
            callback=self._callback,
        )

        self._stream.start()

        print(
            f"[AudioInput] WASAPI loopback capturing '{info['name']}' "
            f"({channels} ch @ {samplerate} Hz)."
        )

    # ---------------------------------------------------------

    def start(self):

        if not self._available:

            print(
                "[AudioInput] sounddevice is not installed - "
                "running silent."
            )

            return

        requested_channels = self.channels

        if self.stereo_requested:

            requested_channels = max(requested_channels, 2)

        if self.loopback:

            try:

                self._open_wasapi_loopback_stream()

                self.stereo_available = self.channels >= 2

                return

            except Exception as exc:

                print(
                    f"[AudioInput] WASAPI loopback unavailable ({exc}) "
                    f"- falling back to a regular input device."
                )

                self.loopback = False

        try:

            self._open_stream(requested_channels)

            self.stereo_available = self.channels >= 2

        except Exception as exc:

            if requested_channels > 1:

                print(
                    f"[AudioInput] stereo capture unavailable "
                    f"({exc}) - falling back to mono."
                )

                try:

                    self._open_stream(1)

                    self.stereo_available = False

                except Exception as exc2:

                    print(
                        f"[AudioInput] could not open input device "
                        f"({exc2}) - running silent."
                    )

                    self._stream = None
                    self.stereo_available = False

            else:

                print(
                    f"[AudioInput] could not open input device "
                    f"({exc}) - running silent."
                )

                self._stream = None
                self.stereo_available = False

    # ---------------------------------------------------------

    def _open_stream(self, channels: int):

        self.channels = max(channels, self.channel + 1)

        self._stream = sd.InputStream(
            device=self.device,
            channels=self.channels,
            samplerate=self.samplerate,
            blocksize=self.block_size,
            latency=self.latency,
            callback=self._callback,
        )

        self._stream.start()

    # ---------------------------------------------------------

    def stop(self):

        if self._stream is not None:

            self._stream.stop()
            self._stream.close()

            self._stream = None

    # ---------------------------------------------------------
    # Waveform ring buffer
    # ---------------------------------------------------------

    def _record_waveform(self, samples):

        n = len(samples)

        capacity = self._waveform_capacity

        if n >= capacity:

            self._waveform_buffer[:] = samples[-capacity:]
            self._waveform_write = 0

            return

        end = self._waveform_write + n

        if end <= capacity:

            self._waveform_buffer[self._waveform_write:end] = samples

        else:

            first = capacity - self._waveform_write

            self._waveform_buffer[self._waveform_write:] = samples[:first]

            remaining = n - first

            self._waveform_buffer[:remaining] = samples[first:]

        self._waveform_write = end % capacity

    # ---------------------------------------------------------

    def recent_waveform(self, sample_count: int) -> np.ndarray:
        """
        Returns the most recent `sample_count` raw samples, oldest
        first, newest last (i.e. index -1 is "now").
        """

        capacity = self._waveform_capacity

        sample_count = max(0, min(sample_count, capacity))

        if sample_count == 0:

            return np.zeros(0, dtype=np.float32)

        start = (self._waveform_write - sample_count) % capacity

        if start + sample_count <= capacity:

            return self._waveform_buffer[start:start + sample_count].copy()

        first = capacity - start

        return np.concatenate(
            (
                self._waveform_buffer[start:],
                self._waveform_buffer[: sample_count - first],
            )
        )

    # ---------------------------------------------------------
    # Stereo ring buffer
    # ---------------------------------------------------------

    def _record_stereo(self, left, right):

        n = len(left)

        capacity = self._waveform_capacity

        if n >= capacity:

            self._left_buffer[:] = left[-capacity:]
            self._right_buffer[:] = right[-capacity:]
            self._stereo_write = 0

            return

        end = self._stereo_write + n

        if end <= capacity:

            self._left_buffer[self._stereo_write:end] = left
            self._right_buffer[self._stereo_write:end] = right

        else:

            first = capacity - self._stereo_write

            self._left_buffer[self._stereo_write:] = left[:first]
            self._right_buffer[self._stereo_write:] = right[:first]

            remaining = n - first

            self._left_buffer[:remaining] = left[first:]
            self._right_buffer[:remaining] = right[first:]

        self._stereo_write = end % capacity

    # ---------------------------------------------------------

    def recent_stereo(self, sample_count: int):

        capacity = self._waveform_capacity

        sample_count = max(0, min(sample_count, capacity))

        if sample_count == 0:

            empty = np.zeros(0, dtype=np.float32)

            return empty, empty

        start = (self._stereo_write - sample_count) % capacity

        if start + sample_count <= capacity:

            return (
                self._left_buffer[start:start + sample_count].copy(),
                self._right_buffer[start:start + sample_count].copy(),
            )

        first = capacity - start

        left = np.concatenate(
            (self._left_buffer[start:], self._left_buffer[: sample_count - first])
        )

        right = np.concatenate(
            (self._right_buffer[start:], self._right_buffer[: sample_count - first])
        )

        return left, right

    # ---------------------------------------------------------
    # Audio thread callback
    # ---------------------------------------------------------

    def _callback(self, indata, frames, time_info, status):

        samples = indata[:, self.channel].astype(np.float32)

        if self.channels >= 2:

            left_raw = indata[:, 0].astype(np.float32)
            right_raw = indata[:, 1].astype(np.float32)

        else:

            left_raw = samples
            right_raw = samples

        if self.muted:

            samples = samples * 0.0
            left_raw = left_raw * 0.0
            right_raw = right_raw * 0.0

        elif self.input_gain != 1.0:

            samples = np.clip(samples * self.input_gain, -1.0, 1.0)
            left_raw = np.clip(left_raw * self.input_gain, -1.0, 1.0)
            right_raw = np.clip(right_raw * self.input_gain, -1.0, 1.0)

        self._record_waveform(samples)
        self._record_stereo(left_raw, right_raw)

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
