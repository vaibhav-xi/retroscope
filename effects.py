"""
RetroScope Effects
"""

import math
import random
import pygame
import config


class BootAnimation:

    def __init__(self):

        self.frame = 0

        self.finished = False

        self.font_big = pygame.font.SysFont(
            "Courier New",
            40,
            bold=True
        )

        self.font_small = pygame.font.SysFont(
            "Courier New",
            20,
            bold=True
        )

    def draw(self, screen):

        if self.finished:
            return

        screen.fill((0, 0, 0))

        #
        # Fade in logo
        #

        alpha = min(255, self.frame * 3)

        title = self.font_big.render(
            "RETROSCOPE",
            True,
            config.TRACE_MAIN,
        )

        subtitle = self.font_small.render(
            "Booting...",
            True,
            config.TEXT,
        )

        title.set_alpha(alpha)
        subtitle.set_alpha(alpha)

        rect = title.get_rect(
            center=(
                config.WIDTH // 2,
                config.HEIGHT // 2 - 20,
            )
        )

        screen.blit(title, rect)

        rect = subtitle.get_rect(
            center=(
                config.WIDTH // 2,
                config.HEIGHT // 2 + 30,
            )
        )

        screen.blit(subtitle, rect)

        #
        # Fake horizontal sweep
        #

        y = int(
            (self.frame * 6)
            % config.HEIGHT
        )

        pygame.draw.line(
            screen,
            config.TRACE_MAIN,
            (0, y),
            (config.WIDTH, y),
            2,
        )

        self.frame += 1

        if self.frame > 120:
            self.finished = True


# ----------------------------------------------------------


class Flicker:

    def __init__(self):

        self.alpha = 0

    def update(self):

        self.alpha = random.randint(
            0,
            6,
        )

    def draw(self, surface):

        if self.alpha == 0:
            return

        overlay = pygame.Surface(
            (
                config.WIDTH,
                config.HEIGHT,
            )
        )

        overlay.fill(
            (
                self.alpha,
                self.alpha,
                self.alpha,
            )
        )

        surface.blit(
            overlay,
            (0, 0),
            special_flags=pygame.BLEND_ADD,
        )


# ----------------------------------------------------------


class NoiseField:

    def __init__(self):

        pass

    def draw(self, surface):

        for _ in range(40):

            x = random.randrange(config.WIDTH)

            y = random.randrange(config.HEIGHT)

            brightness = random.randint(5, 20)

            surface.set_at(
                (
                    x,
                    y,
                ),
                (
                    0,
                    brightness,
                    0,
                ),
            )


# ----------------------------------------------------------


class PhosphorDecay:

    def __init__(self):

        self.overlay = pygame.Surface(
            (
                config.WIDTH,
                config.HEIGHT
            )
        )

        self.overlay.fill((0, 0, 0))

    def apply(self, surface):

        self.overlay.set_alpha(
            config.PERSISTENCE_ALPHA
        )

        surface.blit(
            self.overlay,
            (0, 0),
        )
