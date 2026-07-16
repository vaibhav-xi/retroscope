from __future__ import annotations

import numpy as np

import config

from core.module import Module
from core.frame import Layer

from render.primitives import Polyline
from render.renderable import Renderable
from render_es2.material import Material

from inputs.audio import AudioInput

import platform

_IS_WINDOWS = platform.system() == "Windows"

_MIN_FRAME_SAMPLES = 64
_MAX_FRAME_SAMPLES = 4000

_MIN_PERSISTENCE_SECONDS = 1
_MAX_PERSISTENCE_SECONDS = 50
_DEFAULT_PERSISTENCE_SECONDS = 8

_ANALYSIS_SECONDS = 0.2

_MIN_STROKE_POINTS = 4


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


class AudioReactiveMode13(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 13 (Vector Scope, Accurate)")

        self.audio = AudioInput(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            stereo=True,
            loopback=_IS_WINDOWS,
        )

        self.rect = (0.0, 0.0, 1.0, 1.0)

        self._bright = (1.0, 1.0, 1.0)

        self.trace_renderable = None

        self._gain_peak = 1e-4

        self._cycle_seconds = _DEFAULT_PERSISTENCE_SECONDS

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        theme = context.theme

        self._bright = _normalize_color(theme.trace_core)

        self.trace_renderable = Renderable(
            material=Material(color=self._bright, line_width=1.0),
            is_dynamic=True,
        )

        self._compute_layout(context)

    # ---------------------------------------------------------

    def _compute_layout(self, context):

        margin = 24.0

        size = min(float(context.width), float(context.height)) - margin * 2.0

        cx = float(context.width) * 0.5
        cy = float(context.height) * 0.5

        half = size * 0.5

        self.rect = (cx - half, cy - half, cx + half, cy + half)

    # ---------------------------------------------------------

    @staticmethod
    def _xy_trace(x_samples, y_samples, rect, gain: float):

        x0, y0, x1, y1 = rect

        count = min(len(x_samples), len(y_samples))

        if count < 2:

            return np.zeros((0, 2), dtype=np.float32)

        cx = (x0 + x1) * 0.5
        cy = (y0 + y1) * 0.5

        half_w = (x1 - x0) * 0.5
        half_h = (y1 - y0) * 0.5

        x = cx + np.clip(x_samples[:count] * gain, -1.0, 1.0) * half_w
        y = cy - np.clip(y_samples[:count] * gain, -1.0, 1.0) * half_h

        return np.column_stack([x, y]).astype(np.float32)

    # ---------------------------------------------------------

    @staticmethod
    def _split_on_jumps(points, max_factor: float = 6.0, min_threshold: float = 4.0):
        """
        Beam blanking approximation - any point-to-point jump much
        larger than the typical spacing is a reposition, not a
        stroke, so it starts a new disconnected segment.
        """

        if len(points) < 2:

            return [points] if len(points) else []

        deltas = points[1:] - points[:-1]

        dist = np.sqrt(np.sum(deltas * deltas, axis=1))

        typical = float(np.median(dist)) if len(dist) else 0.0

        threshold = max(min_threshold, typical * max_factor)

        breaks = np.flatnonzero(dist > threshold) + 1

        if len(breaks) == 0:

            return [points]

        return np.split(points, breaks)

    # ---------------------------------------------------------

    def _measure_cycle_seconds(self, audio):
        analysis_samples = int(_ANALYSIS_SECONDS * audio.samplerate)

        left, right = audio.recent_stereo(analysis_samples)

        if len(left) < _MIN_STROKE_POINTS * 2:

            return None

        peak = max(
            float(np.max(np.abs(left))),
            float(np.max(np.abs(right))),
            1e-4,
        )

        if peak < 0.02:

            return None

        gain = 0.9 / max(peak, 0.05)

        points = self._xy_trace(left, right, self.rect, gain)

        strokes = self._split_on_jumps(points)

        lengths = [len(s) for s in strokes if len(s) >= _MIN_STROKE_POINTS]

        if not lengths:

            return None

        return float(np.median(lengths)) / audio.samplerate

    # ---------------------------------------------------------

    def update(self, context):

        pass

    # ---------------------------------------------------------

    def emit(self, context, frame):

        audio = self.audio

        measured = self._measure_cycle_seconds(audio)

        if measured is not None:

            target = min(
                _MAX_PERSISTENCE_SECONDS,
                max(_MIN_PERSISTENCE_SECONDS, measured * 1.15),
            )

            self._cycle_seconds += (target - self._cycle_seconds) * 0.08

        needed = int(round(self._cycle_seconds * audio.samplerate))

        needed = max(_MIN_FRAME_SAMPLES, min(_MAX_FRAME_SAMPLES, needed))

        left, right = audio.recent_stereo(needed)

        self.trace_renderable.clear()

        if len(left) >= 2:

            peak = max(
                float(np.max(np.abs(left))),
                float(np.max(np.abs(right))),
                1e-4,
            )

            self._gain_peak = max(peak, self._gain_peak * 0.98)

            gain = 0.9 / max(self._gain_peak, 0.05)

            points = self._xy_trace(left, right, self.rect, gain)

            for stroke in self._split_on_jumps(points):

                if len(stroke) >= 2:

                    self.trace_renderable.add(Polyline(points=stroke))

        frame.add_renderable(self.trace_renderable, Layer.MAIN)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
