"""
RetroScope

Stroke Builder

Uses the native implementation when available.
"""

try:

    from ._native import build as NativeBuild
    from ._native import build_many as NativeBuildMany

    class StrokeBuilder:

        @staticmethod
        def build(
            primitive,
            vertex_buffer,
        ):

            if primitive.points.ndim == 3:

                # PolylineBatch: many (P, 2) polylines at once.

                NativeBuildMany(
                    primitive.points,
                    2.0,
                    vertex_buffer,
                )

            else:

                NativeBuild(
                    primitive.points,
                    2.0,
                    vertex_buffer,
                )

        @staticmethod
        def build_many(
            primitives,
            vertex_buffer,
            width=2.0,
        ):
            """
            Build every Polyline/PolylineBatch in `primitives` into
            `vertex_buffer` in a single native call. PolylineBatch
            entries are expanded into their individual segments so a
            renderable mixing single polylines and dash batches
            still ends up as one native call.
            """

            if (
                len(primitives) == 1
                and primitives[0].points.ndim == 3
            ):

                NativeBuildMany(
                    primitives[0].points,
                    float(width),
                    vertex_buffer,
                )

                return

            parts = []

            for primitive in primitives:

                if primitive.points.ndim == 3:

                    parts.extend(primitive.points)

                else:

                    parts.append(primitive.points)

            NativeBuildMany(
                parts,
                float(width),
                vertex_buffer,
            )

except ImportError:

    from .stroke_builder_python import StrokeBuilder as PythonBuilder
    from render.primitives import Polyline

    class StrokeBuilder:

        @staticmethod
        def build(
            primitive,
            vertex_buffer,
        ):

            if primitive.points.ndim == 3:

                for points in primitive.points:

                    PythonBuilder.build(
                        Polyline(points=points),
                        vertex_buffer,
                    )

            else:

                PythonBuilder.build(
                    primitive,
                    vertex_buffer,
                )

        @staticmethod
        def build_many(
            primitives,
            vertex_buffer,
            width=2.0,
        ):

            for primitive in primitives:

                StrokeBuilder.build(
                    primitive,
                    vertex_buffer,
                )
