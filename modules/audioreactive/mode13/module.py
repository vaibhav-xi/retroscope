from __future__ import annotations

import json
import pathlib
import subprocess
import sys

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
_MAX_FRAME_SAMPLES = 15000

_STATE_FILE = pathlib.Path(__file__).parent / "tuning.json"

_DEFAULTS = {
    "persistence_seconds": 3.620,
    "point_stride": 1.000,
    "blank_max_factor": 9.686,
    "blank_min_threshold": 0.500,
    "gain_release": 0.925,
    "gain_target": 1.000,
    "gain_floor": 0.010,
    "smoothing": 6.762,
    "line_width": 1.075,
}


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

        self._tuning = dict(_DEFAULTS)
        self._tuning_process = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        theme = context.theme

        self._bright = _normalize_color(theme.trace_core)

        self.trace_renderable = Renderable(
            material=Material(color=self._bright, line_width=_DEFAULTS["line_width"]),
            is_dynamic=True,
        )

        self._compute_layout(context)

        self._launch_tuning_panel()

    # ---------------------------------------------------------

    def _launch_tuning_panel(self):

        panel_path = pathlib.Path(__file__).parent / "tuning_panel.py"

        try:

            self._tuning_process = subprocess.Popen(
                [sys.executable, str(panel_path)]
            )

        except OSError as exc:

            print(
                f"[Mode13] could not launch tuning panel ({exc}) - "
                f"using defaults."
            )

    # ---------------------------------------------------------

    def _poll_tuning(self):

        try:

            if _STATE_FILE.exists():

                self._tuning.update(
                    json.loads(_STATE_FILE.read_text())
                )

        except (ValueError, OSError):

            pass

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
    def _split_on_jumps(points, max_factor: float, min_threshold: float):

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
    def _smooth_stroke(points, window: int):

        window = int(round(window))

        if window <= 1 or len(points) < window:

            return points

        kernel = np.ones(window, dtype=np.float32) / window

        x = np.convolve(points[:, 0], kernel, mode="valid")
        y = np.convolve(points[:, 1], kernel, mode="valid")

        return np.column_stack([x, y]).astype(np.float32)

    # ---------------------------------------------------------

    def update(self, context):

        pass

    # ---------------------------------------------------------

    def emit(self, context, frame):

        audio = self.audio

        self._poll_tuning()

        persistence_seconds = self._tuning["persistence_seconds"]
        point_stride = max(1, int(round(self._tuning["point_stride"])))
        blank_max_factor = self._tuning["blank_max_factor"]
        blank_min_threshold = self._tuning["blank_min_threshold"]
        gain_release = self._tuning["gain_release"]
        gain_target = self._tuning["gain_target"]
        gain_floor = self._tuning["gain_floor"]
        smoothing = self._tuning["smoothing"]
        line_width = self._tuning["line_width"]

        needed = int(round(persistence_seconds * audio.samplerate))

        needed = max(_MIN_FRAME_SAMPLES, min(_MAX_FRAME_SAMPLES, needed))

        left, right = audio.recent_stereo(needed)

        if point_stride > 1:

            left = left[::point_stride]
            right = right[::point_stride]

        self.trace_renderable.clear()

        self.trace_renderable.material = Material(
            color=self._bright,
            line_width=line_width,
        )

        if len(left) >= 2:

            peak = max(
                float(np.max(np.abs(left))),
                float(np.max(np.abs(right))),
                1e-4,
            )

            self._gain_peak = max(peak, self._gain_peak * gain_release)

            gain = gain_target / max(self._gain_peak, gain_floor)

            points = self._xy_trace(left, right, self.rect, gain)

            for stroke in self._split_on_jumps(
                points,
                max_factor=blank_max_factor,
                min_threshold=blank_min_threshold,
            ):

                stroke = self._smooth_stroke(stroke, smoothing)

                if len(stroke) >= 2:

                    self.trace_renderable.add(Polyline(points=stroke))

        frame.add_renderable(self.trace_renderable, Layer.MAIN)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()

        if self._tuning_process is not None:

            self._tuning_process.terminate()
