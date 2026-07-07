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

from render_es2._native import VertexBuffer

class GeometryBuilder:
    
    profiler = None

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
                    renderable.cached_geometry is not None
                ):

                    geometry = None

                else:

                    geometry = Geometry()

                    geometry.vertex_buffer = VertexBuffer()
                    
                    # print(geometry.vertex_buffer)

                    #
                    # Ask the registry which builder handles
                    # each primitive.
                    #
                    
                    # print(
                    #     "renderable",
                    #     len(renderable.primitives),
                    #     renderable.material.color,
                    # )

                    for primitive in renderable.primitives:
                        
                        
                        # print(
                        #     " primitive",
                        #     primitive,
                        # )

                        builder = BuilderRegistry.builder_for(
                            primitive
                        )

                        if builder is None:
                            continue

                        profiler = GeometryBuilder.profiler

                        profiler.begin(
                            "StrokeBuilder"
                        )

                        builder.build(

                            primitive,

                            geometry.vertex_buffer,

                        )
                        
                        # print(
                        #     "after build",
                        #     geometry.vertex_buffer.count
                        # )

                        profiler.end(
                            "StrokeBuilder"
                        )

                    #
                    # Cache static geometry.
                    #

                    if (
                        not renderable.is_dynamic
                        and
                        geometry.vertex_buffer.count > 0
                    ):

                        renderable.cached_geometry = geometry

                #
                # Skip empty renderables.
                #

                if (
                    geometry is not None
                    and
                    geometry.vertex_buffer.count == 0
                ):
                    continue

                packet.add(

                    RenderCommand(

                        renderable=renderable,

                        geometry=geometry,

                    )

                )

        return packet