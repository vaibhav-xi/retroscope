"""
RetroScope

Stroke Builder

Converts geometric primitives into GPU vertex data.

Initially this simply emits line endpoints.

Later this will generate thick triangle geometry.
"""

import config

from render.primitives import Polyline

import math

class StrokeBuilder:

    @staticmethod
    def build(polyline: Polyline):

        vertices = []

        points = polyline.points

        if len(points) < 2:
            return vertices

        for i in range(len(points) - 1):

            x1, y1 = points[i]
            x2, y2 = points[i + 1]

            #
            # Segment direction.
            #

            dx = x2 - x1
            dy = y2 - y1

            length = math.hypot(
                dx,
                dy,
            )

            #
            # Ignore zero-length segments.
            #

            if length == 0:
                continue

            #
            # Unit direction.
            #

            ux = dx / length
            uy = dy / length

            #
            # Unit perpendicular.
            #

            px = -uy
            py = ux
            
            if i == 0:
                print(
                    f"dir=({ux:.3f}, {uy:.3f}) "
                    f"perp=({px:.3f}, {py:.3f})"
                )

            #
            # Still emit the original GL_LINES geometry.
            #

            vertices.extend([

                StrokeBuilder._x(x1),
                StrokeBuilder._y(y1),

                StrokeBuilder._x(x2),
                StrokeBuilder._y(y2),

            ])

        return vertices

    # ---------------------------------------------------------

    @staticmethod
    def _x(x):

        return (2.0 * x / config.WIDTH) - 1.0

    # ---------------------------------------------------------

    @staticmethod
    def _y(y):

        return 1.0 - (2.0 * y / config.HEIGHT)