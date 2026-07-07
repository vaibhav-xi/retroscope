"""
RetroScope

Stroke Builder

Uses the native implementation when available.
"""

try:

    from ._native import build as NativeBuild

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