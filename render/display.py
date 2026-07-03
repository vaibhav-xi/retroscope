"""
RetroScope

Display

Owns the application window.

Responsibilities:

- pygame initialization
- window creation
- fullscreen
- caption
- clock
- presenting frames

The Display knows nothing about rendering.
"""

from __future__ import annotations

import pygame

import config


class Display:

    def __init__(self):

        #
        # Initialize pygame.
        #

        pygame.init()

        #
        # Window flags.
        #

        flags = 0

        if config.FULLSCREEN:

            flags |= pygame.FULLSCREEN

        #
        # Create window.
        #

        self.screen = pygame.display.set_mode(

            (
                config.WIDTH,
                config.HEIGHT,
            ),

            flags,

        )

        pygame.display.set_caption(

            config.WINDOW_TITLE

        )

        #
        # Timing
        #

        self.clock = pygame.time.Clock()

    # ---------------------------------------------------------

    def begin_frame(self):

        """
        Clear the display.

        Normally black.
        """

        self.screen.fill(

            (
                0,
                0,
                0,
            )

        )

    # ---------------------------------------------------------

    def end_frame(self):

        """
        Present the frame.

        Returns measured FPS.
        """

        pygame.display.flip()

        self.clock.tick(

            config.FPS

        )

        return self.clock.get_fps()

    # ---------------------------------------------------------

    def shutdown(self):

        pygame.quit()