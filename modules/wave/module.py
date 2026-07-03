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

        theme = context.theme

        points = []

        center = config.HEIGHT / 2

        scale = config.HEIGHT * self.amplitude

        #
        # Sample the signal registry.
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

        frame.add(

            Polyline(

                points=points,

                color=theme.trace_main,

                width=2,

            )

        )

    # ---------------------------------------------------------

    def shutdown(self):

        pass