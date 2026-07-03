"""
RetroScope

Scanline Stage

Applies CRT scanlines.

This stage is intentionally lightweight and is one of the
cheapest CRT effects.
"""

from __future__ import annotations

import pygame


class ScanlineStage:

    def __init__(self):

        self.enabled = True

        #
        # Darkness of scanlines.
        #

        self.alpha = 35

        #
        # Lazily-created overlay.
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

        overlay.fill((0, 0, 0, 0))

        #
        # Draw every other line.
        #

        for y in range(0, height, 2):

            pygame.draw.line(

                overlay,

                (0, 0, 0, self.alpha),

                (0, y),

                (width, y),

            )

        self._overlay = overlay
        self._size = size

    # ---------------------------------------------------------

    def process(self, surface):

        if not self.enabled:
            return

        size = surface.get_size()

        #
        # Only rebuild if resolution changes.
        #

        if self._overlay is None or size != self._size:

            self._build_overlay(size)

        surface.blit(

            self._overlay,

            (0, 0),

        )