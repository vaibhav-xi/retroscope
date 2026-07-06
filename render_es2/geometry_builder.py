"""
RetroScope

Geometry Builder

Converts engine primitives into GPU render commands.
"""

from core.frame import Layer

from render.builder_registry import BuilderRegistry

from render_es2.render_packet import (
    RenderPacket,
    RenderCommand,
)

from render_es2.geometry import Geometry

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

                    geometry = None

                else:

                    geometry = Geometry()

                    #
                    # Ask the registry which builder handles
                    # this primitive.
                    #

                    for primitive in renderable.primitives:

                        builder = BuilderRegistry.builder_for(
                            primitive
                        )

                        if builder is None:
                            continue

                        geometry.vertices.extend(

                            builder.build(
                                primitive
                            )

                        )

                    #
                    # Cache static geometry.
                    #

                    if (
                        not renderable.is_dynamic
                        and
                        geometry.vertices
                    ):

                        renderable.cached_geometry = geometry

                #
                # Skip empty renderables.
                #

                if (
                    geometry is not None
                    and
                    not geometry.vertices
                ):
                    continue

                packet.add(

                    RenderCommand(

                        renderable=renderable,

                        geometry=geometry,

                    )

                )

        return packet