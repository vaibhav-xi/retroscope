"""
RetroScope

Noise Stage

Applies a subtle phosphor shimmer.

This is NOT television static.

The goal is to make the display feel alive without
becoming visually distracting.
"""

from __future__ import annotations

import random

import pygame


class NoiseStage:

    def __init__(self):

        self.enabled = True

        #
        # Number of shimmering pixels.
        #

        self.pixels = 120

        #
        # Brightness variation.
        #

        self.intensity = 20

    # ---------------------------------------------------------

    def process(self, surface):

        if not self.enabled:

            return

        width, height = surface.get_size()

        for _ in range(self.pixels):

            x = random.randrange(width)
            y = random.randrange(height)

            color = surface.get_at((x, y))

            boost = random.randint(
                0,
                self.intensity,
            )

            r = min(255, color.r + boost)
            g = min(255, color.g + boost)
            b = min(255, color.b + boost)

            surface.set_at(

                (x, y),

                (r, g, b),

            )