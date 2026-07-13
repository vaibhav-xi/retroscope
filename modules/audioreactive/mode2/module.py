"""
RetroScope

Audio Reactive - Mode 2

A denser, more musically-aware companion to Mode 1.

Where Mode 1 treats audio as a single loudness signal plus one
spectrum curve, Mode 2 splits it into named frequency ranges
(bass, low_mid, mid, high_mid, high - see inputs/music_analysis.py)
and reacts to each one differently:

    bass   -> pulse tunnel shells + harmonograph's widest arm +
              orbit ring spawns
    mid    -> nested kaleidoscope rings + harmonograph's middle
              arm + orbit ring radius
    high   -> lightning bolts + harmonograph's tightest arm +
              orbit ring speed
    flux   -> occasional extra lightning on any strong transient,
              even ones that don't cleanly belong to one band
    centroid (spectral brightness) -> blends the harmonograph's
              color between the theme's dim and bright trace
              colors, so the whole thing visibly "whitens" when
              the mix turns trebly

Everything is still built from Polylines - the only primitive
with a GPU builder today (render/builder_registry.py) - and each
system is batched into a single Renderable, so this mode costs
the same handful of draw calls as Mode 1 regardless of how much
geometry is on screen. Vertex counts are tiered down on anything
that isn't a Mac (the Raspberry Pi 3B target).

Simulation only.
No OpenGL.
No GPU calls.
"""

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

from .harmonograph import harmonograph_curve
from .kaleidoscope import kaleidoscope_layers
from .tunnel import PulseTunnel
from .lightning import LightningField
from .orbit import OrbitField

_IS_DESKTOP = platform.system() == "Darwin"

_SPECTRUM_RESOLUTION = 128 if _IS_DESKTOP else 64
_HARMONOGRAPH_POINTS = 600 if _IS_DESKTOP else 260
_KALEIDOSCOPE_LAYERS = 4 if _IS_DESKTOP else 2
_KALEIDOSCOPE_SEGMENTS = 96 if _IS_DESKTOP else 48
_TUNNEL_CAPACITY = 20 if _IS_DESKTOP else 8
_TUNNEL_SIDES = 9
_LIGHTNING_CAPACITY = 16 if _IS_DESKTOP else 6
_LIGHTNING_DEPTH = 4 if _IS_DESKTOP else 2
_ORBIT_CAPACITY = 260 if _IS_DESKTOP else 70
_ORBIT_SPAWN_PER_HIT = 4 if _IS_DESKTOP else 2


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


def _lerp_color(a, b, t):

    t = max(0.0, min(1.0, t))

    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class AudioReactiveMode2(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 2")

        self.audio = MusicAnalyzer(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            spectrum_resolution=_SPECTRUM_RESOLUTION,
        )

        self.rotation = 0.0
        self.phase = 0.0

        self.bass_smooth = 0.0
        self.mid_smooth = 0.0
        self.high_smooth = 0.0

        self.tunnel = None
        self.lightning = None
        self.orbit = None

        self._dark_color = (0.0, 0.0, 0.0)
        self._bright_color = (1.0, 1.0, 1.0)

        self.harmonograph_renderable = None
        self.kaleidoscope_renderable = None
        self.tunnel_renderable = None
        self.lightning_renderable = None
        self.orbit_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        self.tunnel = PulseTunnel(
            capacity=_TUNNEL_CAPACITY,
            sides=_TUNNEL_SIDES,
            random=context.random,
        )

        self.lightning = LightningField(
            capacity=_LIGHTNING_CAPACITY,
            depth=_LIGHTNING_DEPTH,
            random=context.random,
        )

        self.orbit = OrbitField(
            capacity=_ORBIT_CAPACITY,
            random=context.random,
        )

        theme = context.theme

        self._dark_color = _normalize_color(theme.trace_glow)
        self._bright_color = _normalize_color(theme.trace_core)

        self.harmonograph_renderable = Renderable(
            material=Material(
                color=self._bright_color,
                line_width=2.0,
            ),
            is_dynamic=True,
        )

        self.kaleidoscope_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.trace_main),
                line_width=1.5,
            ),
            is_dynamic=True,
        )

        self.tunnel_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.trace_glow),
                line_width=1.5,
            ),
            is_dynamic=True,
        )

        self.lightning_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.text),
                line_width=1.5,
            ),
            is_dynamic=True,
        )

        self.orbit_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.accent),
                line_width=1.0,
            ),
            is_dynamic=True,
        )

    # ---------------------------------------------------------

    def update(self, context):

        dt = context.delta_time

        audio = self.audio

        self.rotation += dt * 0.15
        self.phase += dt * (0.4 + audio.mid * 0.6)

        self.bass_smooth += (audio.bass - self.bass_smooth) * 0.2
        self.mid_smooth += (audio.mid - self.mid_smooth) * 0.2
        self.high_smooth += (audio.high - self.high_smooth) * 0.2

        if audio.bass_hit:

            self.tunnel.spawn(strength=audio.bass)

            self.orbit.spawn(
                count=_ORBIT_SPAWN_PER_HIT,
                base_radius=90.0,
            )

        self.tunnel.update(dt)

        self.orbit.update(
            dt,
            radius_target=90.0 + self.mid_smooth * 40.0,
            speed_scale=1.0 + audio.high * 3.0,
        )

        if audio.high_hit:

            self.lightning.spawn(
                origin=(0.0, 0.0),
                count=3 if _IS_DESKTOP else 1,
                min_length=40.0,
                max_length=90.0 + audio.high * 60.0,
            )

        if (
            audio.flux > 0.6
            and context.random.random() < dt * 4.0
        ):

            self.lightning.spawn(
                origin=(0.0, 0.0),
                count=1,
                min_length=30.0,
                max_length=70.0,
            )

        self.lightning.update(dt)

    # ---------------------------------------------------------

    def emit(self, context, frame):

        cx, cy = context.center

        audio = self.audio

        self.harmonograph_renderable.material = Material(
            color=_lerp_color(
                self._dark_color,
                self._bright_color,
                audio.centroid,
            ),
            line_width=2.0,
        )

        self.harmonograph_renderable.clear()

        curve = harmonograph_curve(
            bass=self.bass_smooth,
            mid=self.mid_smooth,
            high=self.high_smooth,
            phase=self.phase,
            point_count=_HARMONOGRAPH_POINTS,
            base_radius=60.0,
        )

        curve[:, 0] += cx
        curve[:, 1] += cy

        self.harmonograph_renderable.add(Polyline(points=curve))

        self.kaleidoscope_renderable.clear()

        for points in kaleidoscope_layers(
            center=(cx, cy),
            layer_count=_KALEIDOSCOPE_LAYERS,
            base_radius=130.0,
            radius_step=34.0 + self.mid_smooth * 10.0,
            petal_amplitude=14.0 + self.mid_smooth * 22.0,
            petal_count=5,
            rotation=self.rotation,
            segments=_KALEIDOSCOPE_SEGMENTS,
        ):

            self.kaleidoscope_renderable.add(
                Polyline(points=points)
            )

        self.tunnel_renderable.clear()

        for points, life in self.tunnel.shells((cx, cy)):

            self.tunnel_renderable.add(Polyline(points=points))

        self.lightning_renderable.clear()

        for points in self.lightning.polylines():

            points = points.copy()

            points[:, 0] += cx
            points[:, 1] += cy

            self.lightning_renderable.add(Polyline(points=points))

        self.orbit_renderable.clear()

        positions, sizes = self.orbit.points((cx, cy))

        for (x, y), size in zip(positions, sizes):

            angle = math.atan2(y - cy, x - cx) + math.pi / 2.0

            dx = math.cos(angle) * size
            dy = math.sin(angle) * size

            self.orbit_renderable.add(
                Polyline(
                    points=np.array(
                        [
                            [x - dx, y - dy],
                            [x + dx, y + dy],
                        ],
                        dtype=np.float32,
                    )
                )
            )

        frame.add_renderable(self.tunnel_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.kaleidoscope_renderable, Layer.MAIN)
        frame.add_renderable(self.orbit_renderable, Layer.MAIN)
        frame.add_renderable(self.lightning_renderable, Layer.MAIN)
        frame.add_renderable(self.harmonograph_renderable, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
