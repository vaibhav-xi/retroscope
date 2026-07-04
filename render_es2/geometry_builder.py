"""
RetroScope

Geometry Builder

Converts engine primitives into GPU render commands.
"""

import config

from core.frame import Layer

from render.primitives import Polyline

from render_es2.render_packet import (
    RenderPacket,
    RenderCommand,
)

class GeometryBuilder:

    @staticmethod
    def build(frame):

        packet = RenderPacket()

        #
        # Build render commands in explicit layer order.
        #

        for layer in (
            Layer.BACKGROUND,
            Layer.MAIN,
            Layer.OVERLAY,
            Layer.UI,
        ):

            for renderable in frame.layers[layer]:

                if not renderable.is_visible:
                    continue

                vertices = []

                for primitive in renderable.primitives:

                    if not isinstance(
                        primitive,
                        Polyline,
                    ):
                        continue

                    points = primitive.points

                    if len(points) < 2:
                        continue

                    for i in range(len(points) - 1):

                        x1, y1 = points[i]
                        x2, y2 = points[i + 1]

                        vertices.extend([

                            GeometryBuilder._x(x1),
                            GeometryBuilder._y(y1),

                            GeometryBuilder._x(x2),
                            GeometryBuilder._y(y2),

                        ])

                if not vertices:
                    continue

                if (
                    renderable.is_dynamic
                    or renderable.is_dirty
                ):

                    packet.add(

                        RenderCommand(

                            renderable=renderable,

                            vertices=vertices,

                        )

                    )

                else:

                    #
                    # Static mesh already lives on the GPU.
                    #

                    packet.add(

                        RenderCommand(

                            renderable=renderable,

                            vertices=None,

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