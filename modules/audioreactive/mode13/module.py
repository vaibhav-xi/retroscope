from __future__ import annotations

import numpy as np

import config

from core.module import Module
from core.frame import Layer

from render.primitives import PolylineBatch
from render.renderable import Renderable
from render_es2.material import Material

from inputs.audio import AudioInput

import platform

_IS_WINDOWS = platform.system() == "Windows"

_PERSISTENCE_SECONDS = 3

_MIN_FRAME_SAMPLES = 64
_MAX_FRAME_SAMPLES = 4000

_BRIGHTNESS_LEVELS = 6

LINE_WIDTH = 1


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


def _lerp_color(a, b, t):

    t = max(0.0, min(1.0, t))

    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


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

        self._dim = (0.0, 0.0, 0.0)
        self._bright = (1.0, 1.0, 1.0)

        self.brightness_layers = []

        self._gain_peak = 1e-4

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        theme = context.theme

        self._dim = _normalize_color(theme.trace_glow)
        self._bright = _normalize_color(theme.trace_core)

        self.brightness_layers = []

        for level in range(_BRIGHTNESS_LEVELS):

            # level 0 = slowest segments = brightest.
            t = 1.0 - (level / max(_BRIGHTNESS_LEVELS - 1, 1))

            color = _lerp_color(self._dim, self._bright, t * t)

            self.brightness_layers.append(
                Renderable(
                    material=Material(color=color, line_width=LINE_WIDTH),
                    is_dynamic=True,
                )
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

    @staticmethod
    def _bucket_by_speed(points, num_levels: int):

        if len(points) < 2:

            return []

        starts = points[:-1]
        ends = points[1:]

        seg_len = np.sqrt(np.sum((ends - starts) ** 2, axis=1))

        order = np.argsort(seg_len)

        ranks = np.empty_like(order)
        ranks[order] = np.arange(len(seg_len))

        bucket_idx = np.clip(
            (ranks * num_levels) // max(len(seg_len), 1),
            0,
            num_levels - 1,
        )

        buckets = []

        for level in range(num_levels):

            mask = bucket_idx == level

            if not np.any(mask):

                continue

            segments = np.stack(
                [starts[mask], ends[mask]],
                axis=1,
            ).astype(np.float32)

            buckets.append((segments, level))

        return buckets

    # ---------------------------------------------------------

    def update(self, context):

        pass

    # ---------------------------------------------------------

    def emit(self, context, frame):

        audio = self.audio

        needed = int(round(_PERSISTENCE_SECONDS * audio.samplerate))

        needed = max(_MIN_FRAME_SAMPLES, min(_MAX_FRAME_SAMPLES, needed))

        left, right = audio.recent_stereo(needed)

        for renderable in self.brightness_layers:

            renderable.clear()

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

                for segments, level in self._bucket_by_speed(stroke, _BRIGHTNESS_LEVELS):

                    self.brightness_layers[level].add(
                        PolylineBatch(points=segments)
                    )

        for renderable in reversed(self.brightness_layers):

            frame.add_renderable(renderable, Layer.MAIN)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
