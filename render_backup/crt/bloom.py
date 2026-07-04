"""
RetroScope

Bloom Stage

Creates the phosphor glow around bright traces.

Bloom is intentionally subtle.
Persistence is the primary CRT effect.
"""

from __future__ import annotations

import pygame


class BloomStage:

    def __init__(self):

        #
        # Tunable later via Settings.
        #

        self.enabled = True

        self.strength = 90

        self.downscale = 2

    # ---------------------------------------------------------

    def process(self, surface):

        if not self.enabled:
            return

        width = surface.get_width()
        height = surface.get_height()

        #
        # Downsample
        #

        small = pygame.transform.smoothscale(
            surface,
            (
                width // self.downscale,
                height // self.downscale,
            ),
        )

        #
        # Upsample
        #

        bloom = pygame.transform.smoothscale(
            small,
            (
                width,
                height,
            ),
        )

        bloom.set_alpha(self.strength)

        #
        # Additive blend
        #

        surface.blit(
            bloom,
            (0, 0),
            special_flags=pygame.BLEND_ADD,
        )