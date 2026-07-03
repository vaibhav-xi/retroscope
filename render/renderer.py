"""
RetroScope

Renderer

Converts a Frame into pixels.

The renderer knows only about render primitives.
It never knows what simulation produced them.
"""

from __future__ import annotations

import pygame

import config

from core.frame import Frame

from render.primitives import (
    Point,
    Polyline,
    Circle,
    Rectangle,
    Text,
)


class Renderer:

    def __init__(self) -> None:

        pygame.init()

        flags = 0

        if config.FULLSCREEN:
            flags |= pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(
            (config.WIDTH, config.HEIGHT),
            flags,
        )

        pygame.display.set_caption(
            config.WINDOW_TITLE
        )

        self.clock = pygame.time.Clock()

        #
        # Default font
        #

        self.font_cache = {}

    # ---------------------------------------------------------

    def begin_frame(self) -> None:

        self.screen.fill((0, 0, 0))

    # ---------------------------------------------------------

    def render(self, frame: Frame) -> None:

        for primitive in frame:

            #
            # Point
            #

            if isinstance(primitive, Point):

                pygame.draw.circle(
                    self.screen,
                    primitive.color,
                    (
                        int(primitive.position[0]),
                        int(primitive.position[1]),
                    ),
                    primitive.size,
                )

            #
            # Polyline
            #

            elif isinstance(primitive, Polyline):

                if len(primitive.points) >= 2:

                    pygame.draw.lines(
                        self.screen,
                        primitive.color,
                        False,
                        primitive.points,
                        primitive.width,
                    )

            #
            # Circle
            #

            elif isinstance(primitive, Circle):

                pygame.draw.circle(
                    self.screen,
                    primitive.color,
                    (
                        int(primitive.center[0]),
                        int(primitive.center[1]),
                    ),
                    int(primitive.radius),
                    primitive.width,
                )

            #
            # Rectangle
            #

            elif isinstance(primitive, Rectangle):

                rect = pygame.Rect(
                    primitive.x,
                    primitive.y,
                    primitive.width,
                    primitive.height,
                )

                if primitive.filled:

                    pygame.draw.rect(
                        self.screen,
                        primitive.color,
                        rect,
                    )

                else:

                    pygame.draw.rect(
                        self.screen,
                        primitive.color,
                        rect,
                        1,
                    )

            #
            # Text
            #

            elif isinstance(primitive, Text):

                size = primitive.size

                if size not in self.font_cache:

                    self.font_cache[size] = pygame.font.SysFont(
                        "Courier New",
                        size,
                    )

                font = self.font_cache[size]

                surface = font.render(
                    primitive.text,
                    True,
                    primitive.color,
                )

                self.screen.blit(
                    surface,
                    primitive.position,
                )

    # ---------------------------------------------------------

    def end_frame(self) -> float:

        pygame.display.flip()

        self.clock.tick(config.FPS)

        return self.clock.get_fps()

    # ---------------------------------------------------------

    def shutdown(self) -> None:

        pygame.quit()