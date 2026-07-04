"""
RetroScope

Geometry Builder

Converts engine primitives into GPU render commands.
"""

import config

from render.primitives import Polyline

from render_es2.render_packet import (
    RenderPacket,
    RenderCommand,
)

from render_es2.material import Material

class GeometryBuilder:

    @staticmethod
    def build(frame):

        packet = RenderPacket()

        #
        # Build one render command per layer.
        #

        for layer, renderables in frame.layers.items():

            vertices = []

            for renderable in renderables:

                if not renderable.is_visible:
                    continue

                for primitive in renderable.primitives:

                    if not isinstance(
                        primitive,
                        Polyline,
                    ):
                        continue

                    points = primitive.points

                    if len(points) < 2:
                        continue

                    for i in range(
                        len(points) - 1
                    ):

                        x1, y1 = points[i]
                        x2, y2 = points[i + 1]

                        vertices.extend([

                            GeometryBuilder._x(x1),
                            GeometryBuilder._y(y1),

                            GeometryBuilder._x(x2),
                            GeometryBuilder._y(y2),

                        ])

            #
            # Skip empty layers.
            #

            if not vertices:
                continue

            packet.add(

                RenderCommand(

                    vertices=vertices,

                    material=Material(

                        color=(0.0, 1.0, 0.4),

                    ),

                )

            )

        return packet

    # ---------------------------------------------------------

    @staticmethod
    def _x(x):

        return (
            (2.0 * x / config.WIDTH)
            - 1.0
        )

    # ---------------------------------------------------------

    @staticmethod
    def _y(y):

        return (
            1.0
            - (2.0 * y / config.HEIGHT)
        )