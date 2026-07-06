"""
RetroScope

Stroke Builder

Uses the native implementation when available.

Falls back to the Python implementation during development.
"""

try:

    #
    # Native implementation.
    #

    from ._stroke_builder import build

except ImportError:

    #
    # Python fallback.
    #

    from .stroke_builder_python import StrokeBuilder as _PythonStrokeBuilder

    def build(polyline):

        return _PythonStrokeBuilder.build(
            polyline
        )


class StrokeBuilder:

    @staticmethod
    def build(polyline):

        return build(
            polyline.points,
            2.0,
        )