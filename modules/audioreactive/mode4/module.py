
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

from modules.audioreactive.native import BoidSwarm
from .growth import GrowthTree
from .comet import PulseComet
from .sparks import CometSparks
from .colors import hsv


# _IS_DESKTOP = platform.system() == "Darwin"
_IS_DESKTOP = True

_SPECTRUM_RESOLUTION = 64 if _IS_DESKTOP else 32

_BOID_CAPACITY = 160 if _IS_DESKTOP else 45
_MAX_BOID_LINKS = 90 if _IS_DESKTOP else 26
_GROWTH_CAPACITY = 160 if _IS_DESKTOP else 60
_GROWTH_MAX_DEPTH = 6 if _IS_DESKTOP else 4
_COMET_TRAIL_LENGTH = 140 if _IS_DESKTOP else 70
_SPARK_CAPACITY = 90 if _IS_DESKTOP else 30
_CORE_RAY_COUNT = 64 if _IS_DESKTOP else 28

#
# Three fixed anchor directions for the shared "tonal gaze" -
# bass/mid/high act as barycentric weights over these.
#

_ANCHOR_ANGLES = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)


def _core_rays(center, count, length, rotation):

    cx, cy = center

    angles = rotation + np.linspace(
        0.0, 2.0 * math.pi, count, endpoint=False
    )

    for angle in angles:

        x = cx + math.cos(angle) * length
        y = cy + math.sin(angle) * length

        yield np.array(
            [[cx, cy], [x, y]],
            dtype=np.float32,
        )


def _pulse_ring(center, radius, segments=48):

    cx, cy = center

    angles = np.linspace(0.0, 2.0 * math.pi, segments + 1)

    x = cx + radius * np.cos(angles)
    y = cy + radius * np.sin(angles)

    return np.column_stack([x, y]).astype(np.float32)


class AudioReactiveMode4(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 4")

        self.audio = MusicAnalyzer(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            spectrum_resolution=_SPECTRUM_RESOLUTION,
        )

        self.rotation = 0.0
        self.hue_time = 0.0

        self.bass_smooth = 0.0
        self.mid_smooth = 0.0
        self.high_smooth = 0.0

        self.focus = (0.0, 0.0)

        # Shared heartbeat: 1.0 on a bass hit, decays to 0.
        self.beat_pulse = 0.0

        # Percussive radius kick for the comet on treble hits.
        self.comet_kick = 0.0

        # Startle scatter: decaying repulsion strength + the point
        # the flock is currently fleeing from.
        self.startle_strength = 0.0
        self.startle_point = (0.0, 0.0)

        self.boids = None
        self.growth = None
        self.comet = None
        self.sparks = None

        self.core_renderable = None
        self.growth_renderable = None
        self.blossom_renderable = None
        self.boid_renderable = None
        self.link_renderable = None
        self.comet_renderable = None
        self.spark_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        self.boids = BoidSwarm(
            capacity=_BOID_CAPACITY,
            random=context.random,
        )

        self.growth = GrowthTree(
            capacity=_GROWTH_CAPACITY,
            max_depth=_GROWTH_MAX_DEPTH,
            random=context.random,
        )

        self.comet = PulseComet(
            trail_length=_COMET_TRAIL_LENGTH,
        )

        self.sparks = CometSparks(
            capacity=_SPARK_CAPACITY,
            random=context.random,
        )

        self.core_renderable = Renderable(
            material=Material(color=(1.0, 1.0, 1.0), line_width=1.5),
            is_dynamic=True,
        )

        self.growth_renderable = Renderable(
            material=Material(color=(1.0, 1.0, 1.0), line_width=1.3),
            is_dynamic=True,
        )

        self.blossom_renderable = Renderable(
            material=Material(color=(1.0, 1.0, 1.0), line_width=1.2),
            is_dynamic=True,
        )

        self.boid_renderable = Renderable(
            material=Material(color=(1.0, 1.0, 1.0), line_width=1.5),
            is_dynamic=True,
        )

        self.link_renderable = Renderable(
            material=Material(color=(1.0, 1.0, 1.0), line_width=0.75),
            is_dynamic=True,
        )

        self.comet_renderable = Renderable(
            material=Material(color=(1.0, 1.0, 1.0), line_width=2.0),
            is_dynamic=True,
        )

        self.spark_renderable = Renderable(
            material=Material(color=(1.0, 1.0, 1.0), line_width=1.0),
            is_dynamic=True,
        )

    # ---------------------------------------------------------

    def update(self, context):

        dt = context.delta_time

        audio = self.audio

        self.rotation += dt * 0.1

        self.hue_time += dt * (0.05 + audio.level * 0.2)

        self.bass_smooth += (audio.bass - self.bass_smooth) * 0.18
        self.mid_smooth += (audio.mid - self.mid_smooth) * 0.25
        self.high_smooth += (audio.high - self.high_smooth) * 0.35
        
        weights = (self.bass_smooth, self.mid_smooth, self.high_smooth)
        total_weight = sum(weights) + 1e-6

        gaze_x = sum(
            w * math.cos(a) for w, a in zip(weights, _ANCHOR_ANGLES)
        ) / total_weight

        gaze_y = sum(
            w * math.sin(a) for w, a in zip(weights, _ANCHOR_ANGLES)
        ) / total_weight

        focus_radius = 50.0 + (sum(weights) / 3.0) * 150.0

        self.focus = (gaze_x * focus_radius, gaze_y * focus_radius)

        self.beat_pulse *= math.exp(-dt * 6.0)

        beat_trigger = (
            audio.on_beat if audio.beat_confidence > 0.3 else audio.attack_hit
        )

        if beat_trigger:
            self.beat_pulse = max(self.beat_pulse, 1.0)

        self.comet_kick *= math.exp(-dt * 5.0)

        if audio.high_hit:
            self.comet_kick = max(self.comet_kick, 0.6)

        self.startle_strength *= math.exp(-dt * 3.0)

        if audio.flux > 0.65 and context.random.random() < dt * 6.0:

            self.startle_strength = 1.0

            angle = context.random.uniform(0.0, 2.0 * math.pi)
            radius = context.random.uniform(20.0, 90.0)

            self.startle_point = (
                math.cos(angle) * radius,
                math.sin(angle) * radius,
            )

        #
        # Growth
        #

        if beat_trigger:
            self.growth.spurt(amount=18.0 + self.bass_smooth * 26.0)

        if audio.drop:
            self.growth.spurt(amount=40.0 + self.bass_smooth * 30.0)

        if audio.high_hit:
            self.growth.fork(count=2 if _IS_DESKTOP else 1)

        self.growth.update(
            dt,
            ambient_rate=6.0 + self.mid_smooth * 14.0,
            spawn_chance=dt * (0.2 + self.mid_smooth * 0.8),
        )

        #
        # Boids
        #

        if audio.beat_confidence > 0.3:
            # Sharpest right as a beat lands, relaxed by the midpoint
            # between beats - quantized motion, not a reaction to
            # whatever bass energy happens to be present this frame.
            beat_snap = (1.0 - audio.beat_phase) ** 3
        else:
            beat_snap = 0.0

        self.boids.update(
            dt,
            focus=self.focus,
            cohesion=(
                0.6
                + self.bass_smooth * 1.8
                + self.beat_pulse * 1.2
                + beat_snap * 1.0
            ),
            alignment=0.8 + self.mid_smooth * 1.6,
            separation=40.0,
            jitter=6.0 + audio.high * 60.0,
            max_speed=70.0 + self.mid_smooth * 90.0,
            threat=self.startle_point,
            threat_strength=self.startle_strength * 260.0,
        )

        effective_bass = min(1.0, self.bass_smooth + self.comet_kick)

        self.comet.update(
            dt,
            bass=effective_bass,
            mid=self.mid_smooth,
            high=self.high_smooth,
            center=(0.0, 0.0),
        )

        if audio.high_hit or (audio.attack_hit and self.bass_smooth > 0.7):

            trail = self.comet.trail()

            if len(trail) >= 2:

                head = trail[-1]
                prev = trail[-2]

                self.sparks.eject(
                    origin=(float(head[0]), float(head[1])),
                    back_direction=(
                        float(prev[0] - head[0]),
                        float(prev[1] - head[1]),
                    ),
                    count=6 if _IS_DESKTOP else 3,
                    speed_scale=1.0 + audio.high,
                )

        self.sparks.update(dt)

    # ---------------------------------------------------------

    def emit(self, context, frame):

        cx, cy = context.center

        hue = self.hue_time

        self.core_renderable.material = Material(
            color=hsv(hue, 0.65, 1.0),
            line_width=1.4 + self.beat_pulse * 1.8,
        )

        self.core_renderable.clear()

        ray_length = (
            26.0 + self.bass_smooth * 46.0 + self.beat_pulse * 30.0
        )

        for points in _core_rays(
            center=(cx, cy),
            count=_CORE_RAY_COUNT,
            length=ray_length,
            rotation=self.rotation,
        ):

            self.core_renderable.add(Polyline(points=points))

        self.core_renderable.add(
            Polyline(
                points=_pulse_ring(
                    center=(cx, cy),
                    radius=16.0 + self.beat_pulse * 34.0,
                )
            )
        )

        #
        # Growth tree.
        #

        self.growth_renderable.material = Material(
            color=hsv((hue + 0.5) % 1.0, 0.5, 0.85),
            line_width=1.3,
        )

        self.growth_renderable.clear()

        for points, depth in self.growth.segments():

            points = points.copy()

            points[:, 0] += cx
            points[:, 1] += cy

            self.growth_renderable.add(Polyline(points=points))

        self.blossom_renderable.material = Material(
            color=hsv((hue + 0.15) % 1.0, 0.85, 1.0),
            line_width=1.2,
        )

        self.blossom_renderable.clear()

        for points, depth in self.growth.blossoms():

            points = points.copy()

            points[:, 0] += cx
            points[:, 1] += cy

            self.blossom_renderable.add(Polyline(points=points))

        #
        # Boid swarm + its constellation links.
        #

        self.boid_renderable.material = Material(
            color=hsv((hue + 0.33) % 1.0, 0.7, 1.0),
            line_width=1.5,
        )

        self.boid_renderable.clear()

        for points in self.boids.render_points():

            points = points.copy()

            points[:, 0] += cx
            points[:, 1] += cy

            self.boid_renderable.add(Polyline(points=points))

        self.link_renderable.material = Material(
            color=hsv((hue + 0.33) % 1.0, 0.35, 0.5),
            line_width=0.75,
        )

        self.link_renderable.clear()

        for points in self.boids.neighbor_links(max_links=_MAX_BOID_LINKS):

            points = points.copy()

            points[:, 0] += cx
            points[:, 1] += cy

            self.link_renderable.add(Polyline(points=points))

        #
        # Comet trail + sparks.
        #

        self.comet_renderable.material = Material(
            color=hsv((hue + 0.66) % 1.0, 0.55, 1.0),
            line_width=2.0 + self.comet_kick * 2.0,
        )

        self.comet_renderable.clear()

        trail = self.comet.trail()

        if len(trail) >= 2:

            trail = trail.copy()

            trail[:, 0] += cx
            trail[:, 1] += cy

            self.comet_renderable.add(Polyline(points=trail))

        self.spark_renderable.material = Material(
            color=hsv((hue + 0.66) % 1.0, 0.25, 1.0),
            line_width=1.0,
        )

        self.spark_renderable.clear()

        spark_positions, spark_life = self.sparks.points()

        for (x, y), life in zip(spark_positions, spark_life):

            size = 1.0 + life * 3.0

            self.spark_renderable.add(
                Polyline(
                    points=np.array(
                        [
                            [cx + x - size, cy + y],
                            [cx + x + size, cy + y],
                        ],
                        dtype=np.float32,
                    )
                )
            )

        #
        # Submit renderables, back to front.
        #

        frame.add_renderable(self.link_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.growth_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.blossom_renderable, Layer.MAIN)
        frame.add_renderable(self.boid_renderable, Layer.MAIN)
        frame.add_renderable(self.spark_renderable, Layer.MAIN)
        frame.add_renderable(self.comet_renderable, Layer.OVERLAY)
        frame.add_renderable(self.core_renderable, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()