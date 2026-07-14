
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

_IS_DESKTOP = platform.system() == "Darwin"

_SPECTRUM_RESOLUTION = 64 if _IS_DESKTOP else 32

_WAVE_POINTS = 420 if _IS_DESKTOP else 220
_LISSAJOUS_POINTS = 480 if _IS_DESKTOP else 240
_BAND_WAVE_POINTS = 260 if _IS_DESKTOP else 140

_BEATS_SHOWN = 2
_FALLBACK_WINDOW_SECONDS = 0.4
_LISSAJOUS_WINDOW_SECONDS = 0.045


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


def _lerp_color(a, b, t):

    t = max(0.0, min(1.0, t))

    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class AudioReactiveMode7(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 7 (Oscilloscope)")

        self.audio = MusicAnalyzer(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            spectrum_resolution=_SPECTRUM_RESOLUTION,
        )

        self.kick_flash = 0.0
        self.snare_flash = 0.0
        self.trigger_flash = 0.0

        self.main_rect = (0.0, 0.0, 1.0, 1.0)
        self.liss_rect = (0.0, 0.0, 1.0, 1.0)
        self.low_rect = (0.0, 0.0, 1.0, 1.0)
        self.mid_rect = (0.0, 0.0, 1.0, 1.0)
        self.high_rect = (0.0, 0.0, 1.0, 1.0)

        self._dim = (0.0, 0.0, 0.0)
        self._mid_c = (0.0, 0.0, 0.0)
        self._bright = (1.0, 1.0, 1.0)
        self._accent = (1.0, 1.0, 1.0)
        self._text = (1.0, 1.0, 1.0)

        self.grid_renderable = None
        self.grid_center_renderable = None
        self.grid_minor_renderable = None

        self.wave_renderable = None
        self.wave_glow_renderable = None

        self.liss_renderable = None

        self.low_renderable = None
        self.mid_renderable = None
        self.high_renderable = None

        self.marker_renderable = None

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

        self.wave_renderable = Renderable(
            material=Material(color=self._bright, line_width=2.0),
            is_dynamic=True,
        )

        self.wave_glow_renderable = Renderable(
            material=Material(color=self._dim, line_width=4.0),
            is_dynamic=True,
        )

        self.liss_renderable = Renderable(
            material=Material(color=self._mid_c, line_width=1.6),
            is_dynamic=True,
        )

        self.low_renderable = Renderable(
            material=Material(color=self._dim, line_width=1.5),
            is_dynamic=True,
        )

        self.mid_renderable = Renderable(
            material=Material(color=self._mid_c, line_width=1.5),
            is_dynamic=True,
        )

        self.high_renderable = Renderable(
            material=Material(color=self._bright, line_width=1.5),
            is_dynamic=True,
        )

        self.marker_renderable = Renderable(
            material=Material(color=self._accent, line_width=1.5),
            is_dynamic=True,
        )

        self._build_graticule(context)

    # ---------------------------------------------------------

    def _compute_layout(self, context):

        width = float(context.width)
        height = float(context.height)

        margin = 16.0

        top_h = height * 0.30

        self.main_rect = (margin, margin, width - margin, margin + top_h)

        remaining_top = margin + top_h + 14.0

        bottom_h = max(height - remaining_top - margin, 40.0)

        liss_size = min(width * 0.42, bottom_h)

        self.liss_rect = (
            margin,
            remaining_top,
            margin + liss_size,
            remaining_top + liss_size,
        )

        band_x0 = margin + liss_size + 20.0
        band_x1 = width - margin

        band_h = (bottom_h - 16.0) / 3.0

        self.low_rect = (
            band_x0, remaining_top,
            band_x1, remaining_top + band_h,
        )

        self.mid_rect = (
            band_x0, remaining_top + band_h + 8.0,
            band_x1, remaining_top + 2.0 * band_h + 8.0,
        )

        self.high_rect = (
            band_x0, remaining_top + 2.0 * band_h + 16.0,
            band_x1, remaining_top + 3.0 * band_h + 16.0,
        )

    # ---------------------------------------------------------

    def _build_graticule(self, context):

        self._compute_layout(context)

        self.grid_renderable.clear()
        self.grid_center_renderable.clear()
        self.grid_minor_renderable.clear()

        panels = (
            (self.main_rect, 10, 6),
            (self.liss_rect, 8, 8),
            (self.low_rect, 8, 4),
            (self.mid_rect, 8, 4),
            (self.high_rect, 8, 4),
        )

        for rect, cols, rows in panels:

            for points, is_center in scope.graticule_lines(rect, cols, rows):

                if is_center:

                    self.grid_center_renderable.add(Polyline(points=points))

                else:

                    self.grid_renderable.add(Polyline(points=points))

        for rect, cols, rows in (
            (self.main_rect, 10, 6),
            (self.liss_rect, 8, 8),
        ):

            for points in scope.minor_ticks(rect, cols, rows):

                self.grid_minor_renderable.add(Polyline(points=points))

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

        raw = audio.recent_waveform(window_samples + samples_since_beat)

        wave_window = raw[:window_samples] if len(raw) >= window_samples else raw

        wave_points_raw = scope.downsample(wave_window, _WAVE_POINTS)

        peak = float(np.max(np.abs(wave_points_raw))) if len(wave_points_raw) else 1e-4

        wave_gain = 0.85 / max(peak, 0.04)

        self.wave_renderable.clear()
        self.wave_glow_renderable.clear()

        if len(wave_points_raw) >= 2:

            points = scope.waveform_trace(wave_points_raw, self.main_rect, gain=wave_gain)

            self.wave_renderable.add(Polyline(points=points))
            self.wave_glow_renderable.add(Polyline(points=points))

        self.wave_renderable.material = Material(
            color=_lerp_color(self._bright, self._accent, self.trigger_flash * 0.5),
            line_width=1.8 + self.trigger_flash * 1.2,
        )

        self.wave_glow_renderable.material = Material(
            color=_lerp_color(self._dim, self._bright, 0.3),
            line_width=4.0 + self.kick_flash * 3.0,
        )

        self.marker_renderable.clear()

        x0, y0, x1, y1 = self.main_rect

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
        
        liss_window_samples = max(64, int(samplerate * _LISSAJOUS_WINDOW_SECONDS))

        if audio.melody_note_confidence >= audio.bass_note_confidence and audio.melody_note_confidence > 0.1:

            dominant_midi = audio.melody_note_midi

        elif audio.bass_note_confidence > 0.1:

            dominant_midi = audio.bass_note_midi

        else:

            dominant_midi = 57.0  # A3 fallback, used only while unpitched

        freq = 440.0 * (2.0 ** ((dominant_midi - 69.0) / 12.0))
        freq = max(50.0, min(freq, 2000.0))

        delay_samples = int(samplerate / freq / 4.0)
        delay_samples = max(2, min(delay_samples, liss_window_samples // 2))

        liss_buffer = audio.recent_waveform(liss_window_samples + delay_samples)

        x_samples = liss_buffer[delay_samples:]
        y_samples = liss_buffer[:liss_window_samples]

        x_ds, y_ds = scope.downsample_pair(x_samples, y_samples, _LISSAJOUS_POINTS)

        if len(x_ds):

            liss_peak = max(
                float(np.max(np.abs(x_ds))),
                float(np.max(np.abs(y_ds))),
                1e-4,
            )

        else:

            liss_peak = 1e-4

        liss_gain = 0.85 / max(liss_peak, 0.04)

        self.liss_renderable.clear()

        if len(x_ds) >= 2:

            liss_points = scope.lissajous_trace(x_ds, y_ds, self.liss_rect, gain=liss_gain)

            self.liss_renderable.add(Polyline(points=liss_points))

        self.liss_renderable.material = Material(
            color=_lerp_color(self._mid_c, self._accent, audio.tension),
            line_width=1.4 + audio.consonance * 1.0,
        )

        def _auto_gain(samples):

            if len(samples) == 0:
                return 1.0

            peak = float(np.max(np.abs(samples)))

            return 0.85 / max(peak, 0.02)

        low_ds = scope.downsample(audio.low_waveform, _BAND_WAVE_POINTS)
        mid_ds = scope.downsample(audio.mid_waveform, _BAND_WAVE_POINTS)
        high_ds = scope.downsample(audio.high_waveform, _BAND_WAVE_POINTS)

        self.low_renderable.clear()
        self.mid_renderable.clear()
        self.high_renderable.clear()

        if len(low_ds) >= 2:

            self.low_renderable.add(
                Polyline(points=scope.waveform_trace(low_ds, self.low_rect, gain=_auto_gain(low_ds)))
            )

        if len(mid_ds) >= 2:

            self.mid_renderable.add(
                Polyline(points=scope.waveform_trace(mid_ds, self.mid_rect, gain=_auto_gain(mid_ds)))
            )

        if len(high_ds) >= 2:

            self.high_renderable.add(
                Polyline(points=scope.waveform_trace(high_ds, self.high_rect, gain=_auto_gain(high_ds)))
            )

        self.low_renderable.material = Material(
            color=self._dim,
            line_width=1.3 + audio.bass * 2.2 + self.kick_flash * 1.5,
        )

        self.mid_renderable.material = Material(
            color=self._mid_c,
            line_width=1.3 + audio.mid * 2.2,
        )

        self.high_renderable.material = Material(
            color=self._bright,
            line_width=1.3 + audio.high * 2.2 + self.snare_flash * 1.5,
        )

        frame.add_renderable(self.grid_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.grid_minor_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.grid_center_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.wave_glow_renderable, Layer.MAIN)
        frame.add_renderable(self.low_renderable, Layer.MAIN)
        frame.add_renderable(self.mid_renderable, Layer.MAIN)
        frame.add_renderable(self.high_renderable, Layer.MAIN)
        frame.add_renderable(self.liss_renderable, Layer.MAIN)
        frame.add_renderable(self.wave_renderable, Layer.OVERLAY)
        frame.add_renderable(self.marker_renderable, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
