"""
RetroScope

Overlay Module

Draws the oscilloscope information overlay.

The overlay is renderer-independent and only emits
Text primitives.
"""

import config

from core.module import Module

from render_backup.primitives import Text


class OverlayModule(Module):

    def __init__(self):

        super().__init__("Overlay")

    # ---------------------------------------------------------

    def initialize(self, context):

        pass

    # ---------------------------------------------------------

    def update(self, context):

        pass

    # ---------------------------------------------------------

    def emit(self, context, frame):

        theme = context.theme

        #
        # Top Left
        #

        frame.add(

            Text(

                text="CH1",

                position=(15, 12),

                color=theme.text,

                size=18,

            )

        )

        frame.add(

            Text(

                text="AUTO",

                position=(80, 12),

                color=theme.text,

                size=18,

            )

        )

        #
        # Top Right
        #

        frame.add(

            Text(

                text="1 ms/div",

                position=(config.WIDTH - 170, 12),

                color=theme.text,

                size=18,

            )

        )

        frame.add(

            Text(

                text="500 mV/div",

                position=(config.WIDTH - 170, 36),

                color=theme.text,

                size=18,

            )

        )

        #
        # Bottom Left
        #

        frame.add(

            Text(

                text="RetroScope",

                position=(15, config.HEIGHT - 30),

                color=theme.accent,

                size=16,

            )

        )

    # ---------------------------------------------------------

    def shutdown(self):

        pass