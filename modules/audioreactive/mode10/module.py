
from __future__ import annotations

import platform
from collections import deque

import numpy as np

import config

from core.module import Module
from core.frame import Layer

from render.primitives import Polyline
from render.renderable import Renderable
from render_es2.material import Material

from inputs.audio import AudioInput

from .channel_analysis import ChannelAnalyzer, rose_curve, stereo_correlation

_IS_DESKTOP = platform.system() == "Darwin"

_CHANNEL_WINDOW = 2048

_TRACE_WINDOW_SAMPLES = 900 if _IS_DESKTOP else 500
_TRACE_POINTS = 420 if _IS_DESKTOP else 220
_GHOST_LAYERS = 3 if _IS_DESKTOP else 2

_ROSE_SEGMENTS = 220 if _IS_DESKTOP else 130

_MIN_PETALS = 2
_MAX_PETALS = 7


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


def _lerp_color(a, b, t):

    t = max(0.0, min(1.0, t))

    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _petal_count(mid_energy: float) -> int:

    count = _MIN_PETALS + round(mid_energy * (_MAX_PETALS - _MIN_PETALS))

    return int(max(_MIN_PETALS, min(_MAX_PETALS, count)))


class AudioReactiveMode10(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 10 (Stereo Rose)")

        self.audio = AudioInput(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            stereo=True,
        )

        self.left_analyzer = None
        self.right_analyzer = None

        self.phase_left = 0.0
        self.phase_right = 0.0

        self.correlation = 0.0

        self.rect = (0.0, 0.0, 1.0, 1.0)
        self.center = (0.0, 0.0)
        self.base_radius = 100.0

        self._dim = (0.0, 0.0, 0.0)
        self._bright = (1.0, 1.0, 1.0)
        self._left_color = (1.0, 1.0, 1.0)
        self._right_color = (1.0, 1.0, 1.0)
        self._warn = (1.0, 1.0, 1.0)

        self.grid_renderable = None
        self.grid_minor_renderable = None
        self.grid_center_renderable = None

        self.ghost_layers = []
        self._ghost_history = deque(maxlen=_GHOST_LAYERS)

        self.left_rose_renderable = None
        self.right_rose_renderable = None
        self.combined_rose_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        self.left_analyzer = ChannelAnalyzer(
            samplerate=self.audio.samplerate,
            window_size=_CHANNEL_WINDOW,
        )

        self.right_analyzer = ChannelAnalyzer(
            samplerate=self.audio.samplerate,
            window_size=_CHANNEL_WINDOW,
        )

        theme = context.theme

        grid_major = _normalize_color(theme.grid_major)
        grid_minor = _normalize_color(theme.grid_minor)
        grid_center = _normalize_color(theme.grid_center)

        self._dim = _normalize_color(theme.trace_glow)
        self._bright = _normalize_color(theme.trace_core)
        self._left_color = _normalize_color(theme.trace_main)
        self._right_color = _normalize_color(theme.accent)
        self._warn = _normalize_color(theme.text)

        self.grid_renderable = Renderable(
            material=Material(color=grid_major, line_width=1.0),
            is_dynamic=False,
        )

        self.grid_minor_renderable = Renderable(
            material=Material(color=grid_minor, line_width=1.0),
            is_dynamic=False,
        )

        self.grid_center_renderable = Renderable(
            material=Material(color=grid_center, line_width=1.3),
            is_dynamic=True,
        )

        self.ghost_layers = []

        for i in range(_GHOST_LAYERS):

            t = (i + 1) / _GHOST_LAYERS

            self.ghost_layers.append(
                Renderable(
                    material=Material(color=self._dim, line_width=0.8 + t * 0.5),
                    is_dynamic=True,
                )
            )

        self.left_rose_renderable = Renderable(
            material=Material(color=self._left_color, line_width=1.5),
            is_dynamic=True,
        )

        self.right_rose_renderable = Renderable(
            material=Material(color=self._right_color, line_width=1.5),
            is_dynamic=True,
        )

        self.combined_rose_renderable = Renderable(
            material=Material(color=self._bright, line_width=2.2),
            is_dynamic=True,
        )

        self._compute_layout(context)
        self._build_graticule()

    # ---------------------------------------------------------

    def _compute_layout(self, context):

        margin = 24.0

        size = min(float(context.width), float(context.height)) - margin * 2.0

        cx = float(context.width) * 0.5
        cy = float(context.height) * 0.5

        half = size * 0.5

        self.rect = (cx - half, cy - half, cx + half, cy + half)
        self.center = (cx, cy)
        self.base_radius = half * 0.55

    # ---------------------------------------------------------

    def _build_graticule(self):

        self.grid_renderable.clear()
        self.grid_minor_renderable.clear()
        self.grid_center_renderable.clear()

        cols = rows = 10

        for points, is_center in self._graticule_lines(self.rect, cols, rows):

            if is_center:

                self.grid_center_renderable.add(Polyline(points=points))

            else:

                self.grid_renderable.add(Polyline(points=points))

        for points in self._minor_ticks(self.rect, cols, rows):

            self.grid_minor_renderable.add(Polyline(points=points))

    # ---------------------------------------------------------

    @staticmethod
    def _graticule_lines(rect, cols: int, rows: int):

        x0, y0, x1, y1 = rect

        for col in range(cols + 1):

            x = x0 + (x1 - x0) * (col / cols)

            is_center = col == cols // 2

            yield (
                np.array([[x, y0], [x, y1]], dtype=np.float32),
                is_center,
            )

        for row in range(rows + 1):

            y = y0 + (y1 - y0) * (row / rows)

            is_center = row == rows // 2

            yield (
                np.array([[x0, y], [x1, y]], dtype=np.float32),
                is_center,
            )

    # ---------------------------------------------------------

    @staticmethod
    def _minor_ticks(rect, cols: int, rows: int, tick_size: float = 3.0):

        x0, y0, x1, y1 = rect

        for col in range(cols):

            x = x0 + (x1 - x0) * ((col + 0.5) / cols)

            yield np.array([[x, y0], [x, y0 + tick_size]], dtype=np.float32)
            yield np.array([[x, y1 - tick_size], [x, y1]], dtype=np.float32)

        for row in range(rows):

            y = y0 + (y1 - y0) * ((row + 0.5) / rows)

            yield np.array([[x0, y], [x0 + tick_size, y]], dtype=np.float32)
            yield np.array([[x1 - tick_size, y], [x1, y]], dtype=np.float32)

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

    def update(self, context):

        dt = context.delta_time

        audio = self.audio

        left, right = audio.recent_stereo(_CHANNEL_WINDOW)

        self.left_analyzer.analyze(left)
        self.right_analyzer.analyze(right)

        self.correlation = stereo_correlation(left, right)

        self.phase_left += dt * (0.3 + self.left_analyzer.high * 1.6)
        self.phase_right += dt * (0.3 + self.right_analyzer.high * 1.6)

    # ---------------------------------------------------------

    def emit(self, context, frame):

        audio = self.audio

        left_a = self.left_analyzer
        right_a = self.right_analyzer

        left_petals = _petal_count(left_a.mid)
        right_petals = _petal_count(right_a.mid)

        left_amount = 0.15 + left_a.level * 0.65
        right_amount = 0.15 + right_a.level * 0.65

        #
        # Raw XY ghost trace underneath - the honest, undoctored
        # correlation/phase reading, same technique as Mode 9.
        #

        left_raw, right_raw = audio.recent_stereo(_TRACE_WINDOW_SAMPLES)

        x_ds, y_ds = self._downsample_pair(left_raw, right_raw, _TRACE_POINTS)

        if len(x_ds):

            ghost_peak = max(
                float(np.max(np.abs(x_ds))),
                float(np.max(np.abs(y_ds))),
                1e-4,
            )

        else:

            ghost_peak = 1e-4

        ghost_gain = 0.85 / max(ghost_peak, 0.03)

        ghost_points = (
            self._xy_trace(x_ds, y_ds, self.rect, ghost_gain)
            if len(x_ds) >= 2
            else np.zeros((0, 2), dtype=np.float32)
        )

        self._ghost_history.append(ghost_points)

        ghost_history = list(self._ghost_history)

        offset = len(self.ghost_layers) - len(ghost_history)

        for renderable in self.ghost_layers:

            renderable.clear()

        for i, pts in enumerate(ghost_history):

            renderable = self.ghost_layers[offset + i]

            if len(pts) >= 2:

                renderable.add(Polyline(points=pts))

        self.left_rose_renderable.clear()

        left_points = rose_curve(
            center=self.center,
            base_radius=self.base_radius,
            left_amount=left_amount,
            right_amount=right_amount,
            left_petals=left_petals,
            right_petals=right_petals,
            phase_left=self.phase_left,
            phase_right=self.phase_right,
            correlation=self.correlation,
            segments=_ROSE_SEGMENTS,
            include_left=True,
            include_right=False,
        )

        self.left_rose_renderable.add(Polyline(points=left_points))

        self.right_rose_renderable.clear()

        right_points = rose_curve(
            center=self.center,
            base_radius=self.base_radius,
            left_amount=left_amount,
            right_amount=right_amount,
            left_petals=left_petals,
            right_petals=right_petals,
            phase_left=self.phase_left,
            phase_right=self.phase_right,
            correlation=self.correlation,
            segments=_ROSE_SEGMENTS,
            include_left=False,
            include_right=True,
        )

        self.right_rose_renderable.add(Polyline(points=right_points))

        self.combined_rose_renderable.clear()

        combined_points = rose_curve(
            center=self.center,
            base_radius=self.base_radius,
            left_amount=left_amount,
            right_amount=right_amount,
            left_petals=left_petals,
            right_petals=right_petals,
            phase_left=self.phase_left,
            phase_right=self.phase_right,
            correlation=self.correlation,
            segments=_ROSE_SEGMENTS,
            include_left=True,
            include_right=True,
        )

        self.combined_rose_renderable.add(Polyline(points=combined_points))
        
        total_level = left_a.level + right_a.level + 1e-6

        balance = right_a.level / total_level

        self.combined_rose_renderable.material = Material(
            color=_lerp_color(self._left_color, self._right_color, balance),
            line_width=2.0 + (left_a.level + right_a.level) * 1.5,
        )

        self.left_rose_renderable.material = Material(
            color=self._left_color,
            line_width=1.3 + left_a.level * 1.5,
        )

        self.right_rose_renderable.material = Material(
            color=self._right_color,
            line_width=1.3 + right_a.level * 1.5,
        )

        self.grid_center_renderable.material = Material(
            color=self._bright if audio.stereo_available else _lerp_color(self._dim, self._warn, 0.6),
            line_width=1.3,
        )

        frame.add_renderable(self.grid_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.grid_minor_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.grid_center_renderable, Layer.BACKGROUND)

        for renderable in self.ghost_layers:

            frame.add_renderable(renderable, Layer.BACKGROUND)

        frame.add_renderable(self.left_rose_renderable, Layer.MAIN)
        frame.add_renderable(self.right_rose_renderable, Layer.MAIN)
        frame.add_renderable(self.combined_rose_renderable, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
