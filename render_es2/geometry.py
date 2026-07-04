"""
RetroScope

Geometry Builder

Converts engine primitives into GPU vertex arrays.
"""

import config
from render.primitives import Polyline


class Geometry:
    
    @staticmethod
    def rgb(color):

        return (
            color[0] / 255.0,
            color[1] / 255.0,
            color[2] / 255.0,
        )

    @staticmethod
    def build(frame):

        vertices = []
        
        # print(config.WIDTH, config.HEIGHT)

        for primitive in frame.primitives:

            if not isinstance(primitive, Polyline):
                continue

            points = primitive.points

            if len(points) < 2:
                continue

            #
            # Convert screen coordinates
            # to OpenGL coordinates.
            #

            for i in range(len(points) - 1):

                x1, y1 = points[i]
                x2, y2 = points[i + 1]

                r, g, b = Geometry.rgb(primitive.color)

                vertices.extend([

                    Geometry._x(x1),
                    Geometry._y(y1),
                    r,
                    g,
                    b,

                    Geometry._x(x2),
                    Geometry._y(y2),
                    r,
                    g,
                    b,

                ])

        return vertices

    # -------------------------------------------------

    @staticmethod
    def _x(x):

        return (2.0 * x / config.WIDTH) - 1.0


    @staticmethod
    def _y(y):

        return 1.0 - (2.0 * y / config.HEIGHT)