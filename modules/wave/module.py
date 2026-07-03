"""
RetroScope

Wave Module

Converts a signal into render primitives.

The module knows nothing about pygame.

The module knows nothing about CRT.

It only converts samples into a Polyline.
"""

from __future__ import annotations

import config

from core.module import Module

from render.primitives import Polyline

from modules.wave.generator import SignalGenerator


class WaveModule(Module):

    def __init__(self):

        super().__init__("Wave")

        self.generator = SignalGenerator()

        #
        # Display settings
        #

        self.samples = config.WIDTH

        self.amplitude = 0.30

        self.speed = 1.0

    # ---------------------------------------------------------

    def initialize(self, context):

        pass

    # ---------------------------------------------------------

    def update(self, context):

        #
        # Advance signal phase.
        #

        self.generator.phase += (
            self.speed * context.delta_time * 2.0
        )

    # ---------------------------------------------------------

    def emit(self, context, frame):

        theme = context.theme

        points = []

        center_y = config.HEIGHT / 2

        scale = config.HEIGHT * self.amplitude

        #
        # Sample the signal
        #

        for x in range(self.samples):

            t = x / self.samples

            value = self.generator.sample(t)

            y = center_y - value * scale

            points.append(
                (x, y)
            )

        #
        # Emit waveform
        #

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