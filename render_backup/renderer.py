"""
RetroScope

Renderer

Converts a Frame into pixels.

The renderer owns:

- Beam surface
- Primitive rasterization
- CRT pipeline

It does NOT own:

- pygame initialization
- Window
- Clock
- Display swapping
"""

from __future__ import annotations

import pygame

import config

from render_backup.primitives import (
    Point,
    Polyline,
    Circle,
    Rectangle,
    Text,
)

from render_backup.crt.pipeline import CRTPipeline


class Renderer:

    def __init__(self):

        #
        # Off-screen beam surface.
        #

        self.beam = pygame.Surface(

            (
                config.WIDTH,
                config.HEIGHT,
            ),

            pygame.SRCALPHA,

        )

        #
        # CRT pipeline.
        #

        self.crt = CRTPipeline()

        #
        # Font cache.
        #

        self.font_cache = {}

    # ---------------------------------------------------------

    def _font(self, size):

        if size not in self.font_cache:

            self.font_cache[size] = pygame.font.SysFont(
                "Courier New",
                size,
            )

        return self.font_cache[size]

    # ---------------------------------------------------------

    def render(
        self,
        frame,
        screen,
    ):

        #
        # Clear beam.
        #

        self.beam.fill((0, 0, 0, 0))

        #
        # Draw primitives.
        #

        for primitive in frame:

            #
            # Point
            #

            if isinstance(primitive, Point):

                pygame.draw.circle(

                    self.beam,

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

                        self.beam,

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

                    self.beam,

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

                        self.beam,

                        primitive.color,

                        rect,

                    )

                else:

                    pygame.draw.rect(

                        self.beam,

                        primitive.color,

                        rect,

                        1,

                    )

            #
            # Text
            #

            elif isinstance(primitive, Text):

                font = self._font(
                    primitive.size
                )

                image = font.render(

                    primitive.text,

                    True,

                    primitive.color,

                )

                self.beam.blit(

                    image,

                    primitive.position,

                )

        #
        # CRT pipeline.
        #

        self.crt.process(
            self.beam
        )

        #
        # Present to screen.
        #

        screen.blit(

            self.beam,

            (0, 0),

        )