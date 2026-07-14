
from __future__ import annotations

import math

import numpy as np

import config

from core.module import Module
from core.frame import Layer

from render.primitives import Polyline
from render.renderable import Renderable
from render_es2.material import Material

from inputs.music_analysis import MusicAnalyzer

from modules.audioreactive.native import EmberField, spectrum_ring

_SPECTRUM_RESOLUTION = 96
_EMBER_CAPACITY = 400
_CORE_SEGMENTS = 128


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


class AudioReactiveMode1(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 1")

        self.audio = MusicAnalyzer(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            spectrum_resolution=_SPECTRUM_RESOLUTION,
        )

        self.rotation = 0.0
        self.pulse = 0.0

        self.embers = None

        self.rings = []
        self.core = None
        self.ember_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        self.embers = EmberField(
            capacity=_EMBER_CAPACITY,
            inner_radius=70.0,
            random=context.random,
        )

        theme = context.theme

        self.rings = [
            Renderable(
                material=Material(
                    color=_normalize_color(theme.trace_glow),
                    line_width=1.5,
                ),
                is_dynamic=True,
            ),
            Renderable(
                material=Material(
                    color=_normalize_color(theme.trace_main),
                    line_width=2.0,
                ),
                is_dynamic=True,
            ),
            Renderable(
                material=Material(
                    color=_normalize_color(theme.trace_core),
                    line_width=2.0,
                ),
                is_dynamic=True,
            ),
        ]

        self.core = Renderable(
            material=Material(
                color=_normalize_color(theme.trace_core),
                line_width=2.0,
            ),
            is_dynamic=True,
        )

        self.ember_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.trace_main),
                line_width=1.0,
            ),
            is_dynamic=True,
        )

    # ---------------------------------------------------------

    def update(self, context):

        dt = context.delta_time

        self.rotation += dt * 0.12

        audio = self.audio

        level = audio.level

        self.pulse += (level - self.pulse) * 0.25

        #
        # Once tempo is confidently locked, spawn on the phase-locked
        # beat pulse rather than a raw same-frame bass threshold - the
        # embers land on the actual beat grid instead of re-triggering
        # on every bass transient regardless of song tempo. Before
        # lock (first few seconds, or on untuned percussion), fall
        # back to the raw percussive attack so it isn't silent.
        #

        beat_trigger = (
            audio.on_beat if audio.beat_confidence > 0.3 else audio.attack_hit
        )

        if beat_trigger:

            burst = 6

            burst = max(1, round(burst * (0.5 + 0.5 * audio.attack)))

            self.embers.spawn(burst)

        elif level > 0.05:

            if context.random.random() < dt * 2.0:
                self.embers.spawn(1)

        self.embers.update(dt)

    # ---------------------------------------------------------

    def emit(self, context, frame):

        cx, cy = context.center

        spectrum = self.audio.spectrum

        layers = (
            (self.rings[0], 210.0, 90.0, -0.6),
            (self.rings[1], 165.0, 70.0, 1.0),
            (self.rings[2], 120.0, 46.0, 1.6),
        )

        for renderable, base_radius, amplitude, speed in layers:

            renderable.clear()

            points = spectrum_ring(
                spectrum,
                base_radius=base_radius + self.pulse * 12.0,
                amplitude=amplitude,
                rotation=self.rotation * speed,
            )

            points[:, 0] += cx
            points[:, 1] += cy

            renderable.add(
                Polyline(points=points)
            )

        self.core.clear()

        core_radius = 46.0 + self.pulse * 30.0

        angles = np.linspace(
            0.0,
            2.0 * math.pi,
            _CORE_SEGMENTS + 1,
        )

        core_points = np.column_stack(
            [
                cx + core_radius * np.cos(angles),
                cy + core_radius * np.sin(angles),
            ]
        ).astype(np.float32)

        self.core.add(
            Polyline(points=core_points)
        )
        
        self.ember_renderable.clear()

        positions, life = self.embers.points()

        for (x, y), remaining in zip(positions, life):

            angle = math.atan2(y, x)

            streak = 4.0 + remaining * 6.0

            dx = math.cos(angle) * streak
            dy = math.sin(angle) * streak

            self.ember_renderable.add(
                Polyline(
                    points=np.array(
                        [
                            [cx + x - dx, cy + y - dy],
                            [cx + x + dx, cy + y + dy],
                        ],
                        dtype=np.float32,
                    )
                )
            )

        frame.add_renderable(self.rings[0], Layer.BACKGROUND)
        frame.add_renderable(self.rings[1], Layer.MAIN)
        frame.add_renderable(self.ember_renderable, Layer.MAIN)
        frame.add_renderable(self.rings[2], Layer.MAIN)
        frame.add_renderable(self.core, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
