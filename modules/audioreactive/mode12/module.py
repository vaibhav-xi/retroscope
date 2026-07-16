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

_IS_DESKTOP = True

_TRACE_WINDOW_SAMPLES = 900 if _IS_DESKTOP else 500
_TRACE_POINTS = 500 if _IS_DESKTOP else 260


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


class AudioReactiveMode12(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 12 (Vector Scope, Blanked, No Grid)")

        self.audio = AudioInput(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            stereo=True,
            loopback=_IS_WINDOWS,
        )

        self.rect = (0.0, 0.0, 1.0, 1.0)

        self._dim = (0.0, 0.0, 0.0)
        self._bright = (1.0, 1.0, 1.0)
        self._warn = (1.0, 1.0, 1.0)

        self.trace_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        theme = context.theme

        self._dim = _normalize_color(theme.trace_glow)
        self._bright = _normalize_color(theme.trace_core)
        self._warn = _normalize_color(theme.text)

        self.trace_renderable = Renderable(
            material=Material(color=self._bright, line_width=2.0),
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
    def _downsample_pair(a, b, target_points: int):

        n = min(len(a), len(b))

        if n <= target_points:

            return a[:n], b[:n]

        indices = np.linspace(0, n - 1, target_points).astype(np.int64)

        return a[indices], b[indices]

    # ---------------------------------------------------------

    @staticmethod
    def _trigger_offset(reference, search_span: int) -> int:

        span = min(search_span, len(reference) - 1)

        if span <= 0:

            return 0

        segment = reference[:span]

        signs = np.signbit(segment)

        crossings = np.flatnonzero(signs[:-1] & ~signs[1:])

        if len(crossings) == 0:

            return 0

        return int(crossings[0]) + 1

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

    def update(self, context):

        pass

    # ---------------------------------------------------------

    def emit(self, context, frame):

        audio = self.audio

        left, right = audio.recent_stereo(_TRACE_WINDOW_SAMPLES)

        offset = self._trigger_offset(left, search_span=len(left) // 3 or 1)

        if offset:

            left = left[offset:]
            right = right[offset:]

        x_ds, y_ds = self._downsample_pair(left, right, _TRACE_POINTS)

        if len(x_ds):

            peak = max(
                float(np.max(np.abs(x_ds))),
                float(np.max(np.abs(y_ds))),
                1e-4,
            )

        else:

            peak = 1e-4

        gain = 0.92 / max(peak, 0.03)

        self.trace_renderable.clear()

        if len(x_ds) >= 2:

            points = self._xy_trace(x_ds, y_ds, self.rect, gain)

            for segment in self._split_on_jumps(points):

                if len(segment) >= 2:

                    self.trace_renderable.add(Polyline(points=segment))

        frame.add_renderable(self.trace_renderable, Layer.MAIN)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
