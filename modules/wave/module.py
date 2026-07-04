"""
RetroScope

Wave Module

Consumes a signal from the Signal Registry and converts it
into a renderable Polyline.
"""

from __future__ import annotations

import config

from core.module import Module
from core.signal import Signal

from render.primitives import Polyline

from modules.wave.generator import SignalGenerator
from render.renderable import Renderable
from render_es2.material import Material


class WaveModule(Module):

    def __init__(self):

        super().__init__("Wave")

        #
        # Local signal generator
        #

        self.generator = SignalGenerator()

        #
        # Display settings
        #

        self.samples = config.WIDTH

        self.amplitude = 0.30

        self.speed = 1.0

    # ---------------------------------------------------------

    def initialize(self, context):

        #
        # Register the engine's primary signal.
        #

        context.signals.register(

            Signal(

                "main",

                self.generator.sample,

            )

        )

    # ---------------------------------------------------------

    def update(self, context):

        #
        # Animate phase.
        #

        self.generator.phase += (

            self.speed
            * context.delta_time
            * 2.0

        )

    # ---------------------------------------------------------

    def emit(self, context, frame):

        points = []

        center = config.HEIGHT / 2
        scale = config.HEIGHT * self.amplitude

        #
        # Sample the signal.
        #

        for x in range(self.samples):

            t = x / self.samples

            value = context.signals.sample(
                "main",
                t,
            )

            y = center - value * scale

            points.append(
                (x, y)
            )

        #
        # Wave renderable.
        #

        wave = Renderable(
            material=Material(
                color=(
                    0.2,
                    1.0,
                    0.5,
                ),
            ),
        )

        wave.add(

            Polyline(

                points=points,

                color=context.theme.trace_main,   # temporary

                width=2,

            )

        )

        frame.add_renderable(
            wave
        )

    # ---------------------------------------------------------

    def shutdown(self):

        pass