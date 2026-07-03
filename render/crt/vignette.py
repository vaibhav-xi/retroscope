"""
RetroScope

Vignette Stage

Darkens the edges of the display slightly to simulate
the curved face of a CRT.

This is a static effect and is cached.
"""

from __future__ import annotations

import math
import pygame


class VignetteStage:

    def __init__(self):

        self.enabled = True

        #
        # Edge darkness
        #

        self.strength = 0.35

        #
        # Cached vignette
        #

        self._overlay = None
        self._size = None

    # ---------------------------------------------------------

    def _build_overlay(self, size):

        width, height = size

        overlay = pygame.Surface(
            size,
            pygame.SRCALPHA,
        ).convert_alpha()

        cx = width / 2
        cy = height / 2

        max_dist = math.sqrt(cx * cx + cy * cy)

        for y in range(height):

            for x in range(width):

                dx = x - cx
                dy = y - cy

                distance = math.sqrt(dx * dx + dy * dy)

                t = distance / max_dist

                #
                # Smooth radial falloff.
                #

                alpha = int(
                    (t ** 2) * 255 * self.strength
                )

                overlay.set_at(

                    (x, y),

                    (0, 0, 0, alpha),

                )

        self._overlay = overlay
        self._size = size

    # ---------------------------------------------------------

    def process(self, surface):

        if not self.enabled:

            return

        size = surface.get_size()

        if self._overlay is None or size != self._size:

            self._build_overlay(size)

        surface.blit(

            self._overlay,

            (0, 0),

        )