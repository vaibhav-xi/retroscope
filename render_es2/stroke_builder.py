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

from .stroke_builder_python import StrokeBuilder as PythonBuilder
from ._stroke_builder import build as NativeBuild
    

class StrokeBuilder:

    @staticmethod
    def build(polyline):

        py = PythonBuilder.build(polyline)

        c = NativeBuild(
            polyline.points,
            2.0,
        )

        if len(py) != len(c):
            print(
                "Length mismatch:",
                len(py),
                len(c),
            )
            return py

        for i, (a, b) in enumerate(zip(py, c)):

            if abs(a - b) > 0.0001:

                print(
                    f"Mismatch at {i}: "
                    f"{a:.6f} != {b:.6f}"
                )

                return py

        return c