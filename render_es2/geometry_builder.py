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

from render_es2.stroke_builder import StrokeBuilder

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

                        if isinstance(
                            primitive,
                            Polyline,
                        ):

                            vertices.extend(

                                StrokeBuilder.build(
                                    primitive
                                )

                            )

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