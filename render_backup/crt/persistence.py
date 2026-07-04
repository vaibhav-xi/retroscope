"""
RetroScope

Persistence Stage

Maintains phosphor persistence between frames.

This is the heart of the CRT renderer.
"""

from __future__ import annotations

import pygame

import config


class PersistenceStage:

    def __init__(self):

        #
        # Persistent phosphor buffer.
        #

        self.buffer = pygame.Surface(
            (
                config.WIDTH,
                config.HEIGHT,
            ),
            pygame.SRCALPHA,
        ).convert_alpha()

        self.buffer.fill((0, 0, 0, 0))

        #
        # Fade surface
        #

        self.fade_surface = pygame.Surface(
            (
                config.WIDTH,
                config.HEIGHT,
            ),
            pygame.SRCALPHA,
        ).convert_alpha()

        #
        # Default fade
        #

        self.fade_alpha = 18

    # ---------------------------------------------------------

    def process(
        self,
        beam_surface,
    ):

        #
        # Fade old phosphor.
        #

        self.fade_surface.fill(

            (
                0,
                0,
                0,
                self.fade_alpha,
            )

        )

        self.buffer.blit(

            self.fade_surface,

            (0, 0),

            special_flags=pygame.BLEND_RGBA_SUB,

        )

        #
        # Add current beam.
        #

        self.buffer.blit(

            beam_surface,

            (0, 0),

            special_flags=pygame.BLEND_ADD,

        )

        #
        # Copy phosphor back.
        #

        beam_surface.blit(

            self.buffer,

            (0, 0),

        )