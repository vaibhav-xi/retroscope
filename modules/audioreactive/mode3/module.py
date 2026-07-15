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

from .attractor import DustAttractor
from .shockwave import ShockwaveField
from .web import web_rings, web_spokes
from .sparks import SparkBurst
from modules.audioreactive.native import fixed_dashes, life_dashes

# _IS_DESKTOP = platform.system() == "Darwin"
_IS_DESKTOP = True

_SPECTRUM_RESOLUTION = 128 if _IS_DESKTOP else 64

_DUST_CAPACITY = 1400 if _IS_DESKTOP else 380
_DUST_RESEED_FRACTION = 0.015

_SHOCKWAVE_CAPACITY = 24 if _IS_DESKTOP else 10
_SHOCKWAVE_SEGMENTS = 48 if _IS_DESKTOP else 24

_WEB_RING_COUNT = 4 if _IS_DESKTOP else 3
_WEB_SPOKE_COUNT = 48 if _IS_DESKTOP else 24

_SPARK_CAPACITY = 260 if _IS_DESKTOP else 80
_SPARK_BURST_SIZE = 18 if _IS_DESKTOP else 8


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


def _lerp_color(a, b, t):

    t = max(0.0, min(1.0, t))

    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class AudioReactiveMode3(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 3")

        self.audio = MusicAnalyzer(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            spectrum_resolution=_SPECTRUM_RESOLUTION,
            enable_band_waveforms=False,
            enable_vocal_analysis=False,
            enable_pitch_tracking=False,
            enable_harmony=False,
        )

        self.rotation = 0.0

        self.bass_smooth = 0.0
        self.mid_smooth = 0.0
        self.high_smooth = 0.0

        self.dust = None
        self.shockwaves = None
        self.sparks = None

        self._dim_color = (0.0, 0.0, 0.0)
        self._bright_color = (1.0, 1.0, 1.0)

        self.dust_renderable = None
        self.web_renderable = None
        self.shockwave_renderable = None
        self.spark_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        self.dust = DustAttractor(
            capacity=_DUST_CAPACITY,
            random=context.random,
        )

        self.shockwaves = ShockwaveField(
            capacity=_SHOCKWAVE_CAPACITY,
            segments=_SHOCKWAVE_SEGMENTS,
        )

        self.sparks = SparkBurst(
            capacity=_SPARK_CAPACITY,
            random=context.random,
        )

        theme = context.theme

        self._dim_color = _normalize_color(theme.trace_glow)
        self._bright_color = _normalize_color(theme.trace_core)

        self.dust_renderable = Renderable(
            material=Material(
                color=self._bright_color,
                line_width=1.0,
            ),
            is_dynamic=True,
        )

        self.web_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.trace_main),
                line_width=1.5,
            ),
            is_dynamic=True,
        )

        self.shockwave_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.accent),
                line_width=2.0,
            ),
            is_dynamic=True,
        )

        self.spark_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.text),
                line_width=1.0,
            ),
            is_dynamic=True,
        )

    # ---------------------------------------------------------

    def update(self, context):

        dt = context.delta_time

        audio = self.audio

        self.rotation += dt * 0.2

        self.bass_smooth += (audio.bass - self.bass_smooth) * 0.25
        self.mid_smooth += (audio.mid - self.mid_smooth) * 0.25
        self.high_smooth += (audio.high - self.high_smooth) * 0.25

        self.dust.set_parameters(
            bass=self.bass_smooth,
            mid=self.mid_smooth,
            high=self.high_smooth,
        )

        self.dust.update(reseed_fraction=_DUST_RESEED_FRACTION)

        beat_trigger = (
            audio.on_beat if audio.beat_confidence > 0.3 else audio.attack_hit
        )

        if beat_trigger:

            self.shockwaves.spawn(
                strength=14.0 + self.bass_smooth * 22.0,
                speed=140.0 + self.bass_smooth * 160.0,
                wobble=0.2,
            )

        if audio.drop:
            
            self.shockwaves.spawn(
                strength=30.0 + self.bass_smooth * 20.0,
                speed=260.0,
                wobble=0.05,
            )

        if audio.mid_hit:

            self.shockwaves.spawn(
                strength=8.0 + audio.mid * 14.0,
                speed=220.0 + audio.mid * 180.0,
                wobble=0.6,
            )

        if audio.high_hit:

            self.shockwaves.spawn(
                strength=4.0 + audio.high * 8.0,
                speed=320.0 + audio.high * 220.0,
                wobble=1.0,
            )

            origin_angle = context.random.uniform(
                0.0, 2.0 * math.pi
            )

            origin_radius = 150.0 + audio.high * 40.0

            self.sparks.burst(
                origin=(
                    math.cos(origin_angle) * origin_radius,
                    math.sin(origin_angle) * origin_radius,
                ),
                count=_SPARK_BURST_SIZE,
                speed_scale=1.0 + audio.high,
            )

        self.shockwaves.update(dt)

        self.sparks.update(dt)

    # ---------------------------------------------------------

    def emit(self, context, frame):

        cx, cy = context.center

        audio = self.audio
        
        scale = 90.0 * (
            0.85 + self.bass_smooth * 0.45 + audio.section_energy * 0.2
        )

        positions = self.dust.points((0.0, 0.0), scale)

        positions = self.shockwaves.kick(positions, (0.0, 0.0))

        self.dust_renderable.material = Material(
            color=_lerp_color(
                self._dim_color,
                self._bright_color,
                audio.centroid,
            ),
            line_width=1.0,
        )

        self.dust_renderable.clear()

        for points in fixed_dashes(positions, dx=0.6, dy=0.6, center=(cx, cy)):

            self.dust_renderable.add(Polyline(points=points))

        self.web_renderable.clear()

        web_kwargs = dict(
            center=(cx, cy),
            spectrum=audio.spectrum,
            ring_count=_WEB_RING_COUNT,
            spoke_count=_WEB_SPOKE_COUNT,
            base_radius=150.0,
            radius_step=26.0,
            amplitude=60.0 + self.mid_smooth * 40.0,
            rotation=self.rotation,
        )

        for points in web_rings(**web_kwargs):

            self.web_renderable.add(Polyline(points=points))

        for points in web_spokes(**web_kwargs):

            self.web_renderable.add(Polyline(points=points))

        self.shockwave_renderable.clear()

        for points, life in self.shockwaves.rings((cx, cy)):

            self.shockwave_renderable.add(Polyline(points=points))

        self.spark_renderable.clear()

        spark_positions, spark_life = self.sparks.points()

        for points in life_dashes(
            spark_positions, spark_life, center=(cx, cy), size_base=2.0, size_scale=4.0
        ):

            self.spark_renderable.add(Polyline(points=points))

        frame.add_renderable(self.dust_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.web_renderable, Layer.MAIN)
        frame.add_renderable(self.shockwave_renderable, Layer.MAIN)
        frame.add_renderable(self.spark_renderable, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
