from __future__ import annotations

import math
import platform

import numpy as np

import config

from core.module import Module
from core.frame import Layer

from render.primitives import Polyline
from render.renderable import Renderable
from render_es2.material import Material

from inputs.music_analysis import MusicAnalyzer

from . import scope

# _IS_DESKTOP = platform.system() == "Darwin"
_IS_DESKTOP = True

_SPECTRUM_RESOLUTION = 64 if _IS_DESKTOP else 32

_WAVE_POINTS = 480 if _IS_DESKTOP else 260

_BEATS_SHOWN = 2
_FALLBACK_WINDOW_SECONDS = 0.4

_NOW_DOT_SIDES = 6


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


def _lerp_color(a, b, t):

    t = max(0.0, min(1.0, t))

    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class AudioReactiveMode8(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 8 (Oscilloscope)")

        self.audio = MusicAnalyzer(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            spectrum_resolution=_SPECTRUM_RESOLUTION,
            enable_band_waveforms=False,
            enable_vocal_analysis=True,
            enable_pitch_tracking=False,
            enable_harmony=True,
        )

        self.kick_flash = 0.0
        self.snare_flash = 0.0
        self.vocal_flash = 0.0
        self.trigger_flash = 0.0

        self.rect = (0.0, 0.0, 1.0, 1.0)

        self._dim = (0.0, 0.0, 0.0)
        self._mid_c = (0.0, 0.0, 0.0)
        self._bright = (1.0, 1.0, 1.0)
        self._accent = (1.0, 1.0, 1.0)
        self._text = (1.0, 1.0, 1.0)
        self._grid_major = (0.0, 0.0, 0.0)
        self._grid_center = (0.0, 0.0, 0.0)
        self._grid_minor = (0.0, 0.0, 0.0)

        self.grid_renderable = None
        self.grid_center_renderable = None
        self.grid_minor_renderable = None

        self.vocal_renderable = None
        self.wave_renderable = None
        self.wave_glow_renderable = None
        self.marker_renderable = None
        self.now_dot_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        theme = context.theme

        self._grid_major = _normalize_color(theme.grid_major)
        self._grid_center = _normalize_color(theme.grid_center)
        self._grid_minor = _normalize_color(theme.grid_minor)

        self._dim = _normalize_color(theme.trace_glow)
        self._mid_c = _normalize_color(theme.trace_main)
        self._bright = _normalize_color(theme.trace_core)
        self._accent = _normalize_color(theme.accent)
        self._text = _normalize_color(theme.text)

        self.grid_renderable = Renderable(
            material=Material(color=self._grid_major, line_width=1.0),
            is_dynamic=False,
        )

        self.grid_center_renderable = Renderable(
            material=Material(color=self._grid_center, line_width=1.3),
            is_dynamic=False,
        )

        self.grid_minor_renderable = Renderable(
            material=Material(color=self._grid_minor, line_width=1.0),
            is_dynamic=False,
        )

        self.vocal_renderable = Renderable(
            material=Material(color=self._dim, line_width=1.2),
            is_dynamic=True,
        )

        self.wave_glow_renderable = Renderable(
            material=Material(color=self._dim, line_width=4.0),
            is_dynamic=True,
        )

        self.wave_renderable = Renderable(
            material=Material(color=self._bright, line_width=2.0),
            is_dynamic=True,
        )

        self.marker_renderable = Renderable(
            material=Material(color=self._accent, line_width=1.5),
            is_dynamic=True,
        )

        self.now_dot_renderable = Renderable(
            material=Material(color=self._text, line_width=1.5),
            is_dynamic=True,
        )

        self._build_graticule(context)

    # ---------------------------------------------------------

    def _build_graticule(self, context):

        margin = 24.0

        self.rect = (
            margin,
            margin,
            float(context.width) - margin,
            float(context.height) - margin,
        )

        self.grid_renderable.clear()
        self.grid_minor_renderable.clear()

        for points, is_center in scope.graticule_lines(self.rect, cols=10, rows=8):

            if not is_center:

                self.grid_renderable.add(Polyline(points=points))

        for points in scope.minor_ticks(self.rect, cols=10, rows=8):

            self.grid_minor_renderable.add(Polyline(points=points))

        self.grid_center_renderable.clear()

        for points, is_center in scope.graticule_lines(self.rect, cols=10, rows=8):

            if is_center:

                self.grid_center_renderable.add(Polyline(points=points))

    # ---------------------------------------------------------

    def update(self, context):

        dt = context.delta_time

        audio = self.audio

        self.kick_flash *= math.exp(-dt * 8.0)

        if audio.kick_hit:
            self.kick_flash = 1.0

        self.snare_flash *= math.exp(-dt * 10.0)

        if audio.snare_hit:
            self.snare_flash = 1.0

        self.vocal_flash *= math.exp(-dt * 7.0)

        if audio.vocal_hit:
            self.vocal_flash = 1.0

        beat_trigger = (
            audio.on_beat if audio.beat_confidence > 0.3 else audio.attack_hit
        )

        self.trigger_flash *= math.exp(-dt * 6.0)

        if beat_trigger:
            self.trigger_flash = 1.0

    # ---------------------------------------------------------

    def emit(self, context, frame):

        audio = self.audio

        samplerate = audio.samplerate

        locked = audio.beat_confidence > 0.3 and audio.bpm > 0.0

        if locked:

            samples_per_beat = max(64, int(samplerate * 60.0 / audio.bpm))
            window_samples = samples_per_beat * _BEATS_SHOWN
            samples_since_beat = int(audio.beat_phase * samples_per_beat)

        else:

            window_samples = max(64, int(samplerate * _FALLBACK_WINDOW_SECONDS))
            samples_since_beat = 0

        lookback = window_samples + samples_since_beat

        raw = audio.recent_waveform(lookback)
        vocal_raw = audio.recent_vocal_waveform(lookback)

        wave_window = raw[:window_samples] if len(raw) >= window_samples else raw

        vocal_window = (
            vocal_raw[:window_samples]
            if len(vocal_raw) >= window_samples
            else vocal_raw
        )

        wave_points_raw = scope.downsample(wave_window, _WAVE_POINTS)
        vocal_points_raw = scope.downsample(vocal_window, _WAVE_POINTS)


        peak = float(np.max(np.abs(wave_points_raw))) if len(wave_points_raw) else 1e-4

        wave_gain = 0.85 / max(peak, 0.04)

        vocal_peak = (
            float(np.max(np.abs(vocal_points_raw))) if len(vocal_points_raw) else 1e-4
        )

        vocal_gain = (0.75 / max(vocal_peak, 0.03)) * (0.4 + audio.vocal_presence * 1.4)

        self.vocal_renderable.clear()

        if len(vocal_points_raw) >= 2:

            vocal_points = scope.waveform_trace(vocal_points_raw, self.rect, gain=vocal_gain)

            self.vocal_renderable.add(Polyline(points=vocal_points))

        self.vocal_renderable.material = Material(
            color=_lerp_color(self._dim, self._text, min(1.0, audio.vocal_presence * 1.3)),
            line_width=1.0 + audio.vocal_activity * 1.8 + self.vocal_flash * 1.5,
        )

        self.wave_renderable.clear()
        self.wave_glow_renderable.clear()

        wave_points = np.zeros((0, 2), dtype=np.float32)

        if len(wave_points_raw) >= 2:

            wave_points = scope.waveform_trace(wave_points_raw, self.rect, gain=wave_gain)

            self.wave_renderable.add(Polyline(points=wave_points))
            self.wave_glow_renderable.add(Polyline(points=wave_points))

        self.wave_renderable.material = Material(
            color=_lerp_color(self._bright, self._accent, audio.tension * 0.6 + self.trigger_flash * 0.3),
            line_width=1.8 + self.trigger_flash * 1.2,
        )

        self.wave_glow_renderable.material = Material(
            color=_lerp_color(self._dim, self._bright, 0.3),
            line_width=4.0 + self.kick_flash * 3.0,
        )

        self.grid_center_renderable.material = Material(
            color=_lerp_color(self._grid_center, self._accent, audio.key_confidence),
            line_width=1.3 + audio.key_confidence * 1.5,
        )

        self.marker_renderable.clear()

        x0, y0, x1, y1 = self.rect

        marker_x = x1 - 4.0

        if self.kick_flash > 0.05:

            size = 6.0 + self.kick_flash * 10.0

            self.marker_renderable.add(
                Polyline(
                    points=np.array(
                        [[marker_x - size, y1 - 4.0], [marker_x, y1 - 4.0 - size]],
                        dtype=np.float32,
                    )
                )
            )

        if self.snare_flash > 0.05:

            size = 6.0 + self.snare_flash * 10.0

            self.marker_renderable.add(
                Polyline(
                    points=np.array(
                        [[marker_x - size, y0 + 4.0], [marker_x, y0 + 4.0 + size]],
                        dtype=np.float32,
                    )
                )
            )

        if self.vocal_flash > 0.05:

            size = 5.0 + self.vocal_flash * 9.0

            mid_y = (y0 + y1) * 0.5 + (y1 - y0) * 0.28

            self.marker_renderable.add(
                Polyline(
                    points=np.array(
                        [[marker_x - size, mid_y], [marker_x, mid_y - size]],
                        dtype=np.float32,
                    )
                )
            )

        trigger_y = (y0 + y1) * 0.5 - (y1 - y0) * 0.5 * 0.35

        self.marker_renderable.add(
            Polyline(
                points=np.array(
                    [[x0, trigger_y], [x1, trigger_y]],
                    dtype=np.float32,
                )
            )
        )

        self.marker_renderable.material = Material(
            color=_lerp_color(self._accent, self._bright, self.trigger_flash),
            line_width=1.2 + self.trigger_flash * 1.5,
        )

        self.now_dot_renderable.clear()

        if len(wave_points) > 0:

            tip_x, tip_y = wave_points[-1]

            size = 3.0 + audio.level * 6.0 + self.vocal_flash * 4.0

            angles = np.linspace(0.0, 2.0 * math.pi, _NOW_DOT_SIDES, endpoint=False)

            dot_x = tip_x + size * np.cos(angles)
            dot_y = tip_y + size * np.sin(angles)

            dot_points = np.column_stack([dot_x, dot_y]).astype(np.float32)
            dot_points = np.vstack([dot_points, dot_points[0]])

            self.now_dot_renderable.add(Polyline(points=dot_points))

        self.now_dot_renderable.material = Material(
            color=_lerp_color(self._bright, self._text, audio.vocal_activity),
            line_width=1.5 + self.vocal_flash * 2.0,
        )

        frame.add_renderable(self.grid_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.grid_minor_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.grid_center_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.vocal_renderable, Layer.MAIN)
        frame.add_renderable(self.wave_glow_renderable, Layer.MAIN)
        frame.add_renderable(self.wave_renderable, Layer.OVERLAY)
        frame.add_renderable(self.marker_renderable, Layer.OVERLAY)
        frame.add_renderable(self.now_dot_renderable, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
