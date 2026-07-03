"""
RetroScope v0.2
Electron Beam Renderer
"""

import pygame
import config


class BeamRenderer:

    def __init__(self):

        self.surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        ).convert_alpha()

    # -----------------------------------------------------

    def clear(self):

        self.surface.fill((0, 0, 0, 0))

    # -----------------------------------------------------

    def draw(self, samples):

        """
        samples: iterable of floats (-1.0 ... +1.0)
        """

        self.clear()

        centre = config.HEIGHT // 2

        amplitude = int(
            config.HEIGHT *
            config.runtime["amplitude"] *
            0.40
        )

        points = []

        for x, value in enumerate(samples):

            y = int(centre - value * amplitude)

            points.append((x, y))

        #
        # Beam halo
        #

        pygame.draw.lines(
            self.surface,
            (0, 90, 20),
            False,
            points,
            11,
        )

        #
        # Outer glow
        #

        pygame.draw.lines(
            self.surface,
            config.TRACE_GLOW,
            False,
            points,
            7,
        )

        #
        # Main beam
        #

        pygame.draw.lines(
            self.surface,
            config.TRACE_MAIN,
            False,
            points,
            3,
        )

        #
        # Bright phosphor core
        #

        pygame.draw.aalines(
            self.surface,
            config.TRACE_CORE,
            False,
            points,
        )

        #
        # Small highlights
        #

        for x, y in points[::20]:

            pygame.draw.circle(
                self.surface,
                (255, 255, 255),
                (x, y),
                1,
            )

        return self.surface
