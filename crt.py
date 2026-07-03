"""
RetroScope v0.2
CRT Rendering Engine
"""

import random
import pygame

import config


class CRT:

    def __init__(self):

        #
        # Persistent phosphor
        #

        self.phosphor = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        ).convert_alpha()

        self.phosphor.fill((0, 0, 0, 0))

        #
        # Glow buffer
        #

        self.glow = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        ).convert_alpha()

        #
        # Overlay buffer
        #

        self.overlay = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        ).convert_alpha()

        #
        # Reusable fade surface
        #

        self.fade = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        )

        self.fade.fill(
            (0, 0, 0, config.PERSISTENCE_ALPHA)
        )

    # -----------------------------------------------------

    def update(self, beam_surface):

        #
        # Fade previous phosphor
        #

        if config.runtime["persistence"]:

            self.phosphor.blit(
                self.fade,
                (0, 0),
                special_flags=pygame.BLEND_RGBA_SUB,
            )

        else:

            self.phosphor.fill((0, 0, 0, 0))

        #
        # Add fresh beam
        #

        self.phosphor.blit(
            beam_surface,
            (0, 0),
            special_flags=pygame.BLEND_ADD,
        )

    # -----------------------------------------------------

    def render(self, screen):

        #
        # Bloom
        #

        if config.runtime["glow"]:

            self.glow.fill((0, 0, 0, 0))

            bloom = pygame.transform.smoothscale(
                self.phosphor,
                (
                    config.WIDTH // 2,
                    config.HEIGHT // 2,
                ),
            )

            bloom = pygame.transform.smoothscale(
                bloom,
                (
                    config.WIDTH,
                    config.HEIGHT,
                ),
            )

            bloom.set_alpha(
                config.BLOOM_ALPHA
            )

            self.glow.blit(
                bloom,
                (0, 0),
                special_flags=pygame.BLEND_ADD,
            )

            #
            # Draw glow
            #

            screen.blit(
                self.glow,
                (0, 0),
                special_flags=pygame.BLEND_ADD,
            )

        #
        # Draw phosphor
        #

        screen.blit(
            self.phosphor,
            (0, 0),
        )

        #
        # Overlay
        #

        self.overlay.fill((0, 0, 0, 0))

        #
        # Scanlines
        #

        if config.runtime["scanlines"]:

            for y in range(
                0,
                config.HEIGHT,
                2,
            ):

                pygame.draw.line(
                    self.overlay,
                    (
                        0,
                        0,
                        0,
                        config.SCANLINE_ALPHA,
                    ),
                    (0, y),
                    (config.WIDTH, y),
                )

        #
        # Noise
        #

        if config.runtime["noise"]:

            for _ in range(
                config.NOISE_PIXELS
            ):

                x = random.randrange(
                    config.WIDTH
                )

                y = random.randrange(
                    config.HEIGHT
                )

                g = random.randint(
                    15,
                    50,
                )

                self.overlay.set_at(
                    (x, y),
                    (0, g, 0, 70),
                )

        #
        # Vignette
        #

        if config.runtime["vignette"]:

            for i in range(14):

                pygame.draw.rect(

                    self.overlay,

                    (
                        0,
                        0,
                        0,
                        i * 6,
                    ),

                    pygame.Rect(

                        i * 6,
                        i * 6,

                        config.WIDTH - i * 12,
                        config.HEIGHT - i * 12,

                    ),

                    2,
                )

        #
        # Draw overlay
        #

        screen.blit(
            self.overlay,
            (0, 0),
        )
