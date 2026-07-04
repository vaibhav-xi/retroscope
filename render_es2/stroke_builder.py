"""
RetroScope

Stroke Builder

Converts geometric primitives into GPU vertex data.

Initially this simply emits line endpoints.

Later this will generate thick triangle geometry.
"""

import config

from render.primitives import Polyline


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