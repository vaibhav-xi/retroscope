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
            polyline,
            vertex_buffer,
        ):

            NativeBuild(

                polyline.points,

                2.0,

                vertex_buffer,

            )

        @staticmethod
        def build_many(
            polylines,
            vertex_buffer,
            width=2.0,
        ):
            """
            Build every polyline in `polylines` into `vertex_buffer`
            in a single native call, instead of one call (and one
            reserve) per primitive.
            """

            NativeBuildMany(

                [p.points for p in polylines],

                float(width),

                vertex_buffer,

            )

except ImportError:

    from .stroke_builder_python import StrokeBuilder as PythonBuilder

    class StrokeBuilder:

        @staticmethod
        def build(
            polyline,
            vertex_buffer,
        ):

            PythonBuilder.build(
                polyline,
                vertex_buffer,
            )

        @staticmethod
        def build_many(
            polylines,
            vertex_buffer,
            width=2.0,
        ):

            for polyline in polylines:

                PythonBuilder.build(
                    polyline,
                    vertex_buffer,
                )
