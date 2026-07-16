"""
RetroScope

Stroke Builder

Uses the native implementation when available.
"""

try:

    from ._native import build as NativeBuild
    from ._native import build_many as NativeBuildMany

    class StrokeBuilder:

        # Set once by Window at startup from the real window size
        # (see render_es2/window.py). Defaults match the old
        # hardcoded values so nothing breaks if it's never set.
        screen_width = 800.0
        screen_height = 480.0

        @staticmethod
        def build(
            primitive,
            vertex_buffer,
            width=2.0,
        ):

            if primitive.points.ndim == 3:

                NativeBuildMany(
                    primitive.points,
                    float(width),
                    vertex_buffer,
                    StrokeBuilder.screen_width,
                    StrokeBuilder.screen_height,
                )

            else:

                NativeBuild(
                    primitive.points,
                    float(width),
                    vertex_buffer,
                    StrokeBuilder.screen_width,
                    StrokeBuilder.screen_height,
                )

        @staticmethod
        def build_many(
            primitives,
            vertex_buffer,
            width=2.0,
        ):

            if (
                len(primitives) == 1
                and primitives[0].points.ndim == 3
            ):

                NativeBuildMany(
                    primitives[0].points,
                    float(width),
                    vertex_buffer,
                    StrokeBuilder.screen_width,
                    StrokeBuilder.screen_height,
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
                StrokeBuilder.screen_width,
                StrokeBuilder.screen_height,
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
