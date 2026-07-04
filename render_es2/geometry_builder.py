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
        # Build render commands in render order.
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

                #
                # Static geometry already cached.
                #

                if (
                    not renderable.is_dynamic
                    and
                    not renderable.is_dirty
                    and
                    renderable.cached_vertices is not None
                ):

                    vertices = None

                else:

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

                    #
                    # Cache static geometry.
                    #

                    if (
                        not renderable.is_dynamic
                        and vertices
                    ):

                        renderable.cached_vertices = vertices

                #
                # Skip empty renderables.
                #

                if (
                    vertices is not None
                    and
                    not vertices
                ):
                    continue

                packet.add(

                    RenderCommand(

                        renderable=renderable,

                        vertices=vertices,

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