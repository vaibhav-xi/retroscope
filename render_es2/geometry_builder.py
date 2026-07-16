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

                    #
                    # Ask the registry which builder handles each
                    # primitive, and group consecutive primitives
                    # that share a builder so batch-capable
                    # builders (StrokeBuilder) build them in one
                    # native call instead of one call per
                    # primitive.
                    #

                    profiler = GeometryBuilder.profiler

                    run_builder = None
                    run_items = []

                    def _flush(builder, items):

                        if not items:
                            return

                        profiler.begin(
                            "StrokeBuilder"
                        )

                        if hasattr(builder, "build_many"):

                            builder.build_many(
                                items,
                                geometry.vertex_buffer,
                                width=renderable.material.line_width,
                            )

                        else:

                            for item in items:

                                builder.build(
                                    item,
                                    geometry.vertex_buffer,
                                )

                        profiler.end(
                            "StrokeBuilder"
                        )

                    for primitive in renderable.primitives:

                        builder = BuilderRegistry.builder_for(
                            primitive
                        )

                        if builder is None:
                            continue

                        if builder is not run_builder:

                            _flush(run_builder, run_items)

                            run_builder = builder
                            run_items = []

                        run_items.append(primitive)

                    _flush(run_builder, run_items)

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
