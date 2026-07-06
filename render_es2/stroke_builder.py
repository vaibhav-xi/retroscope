"""
RetroScope

Stroke Builder

Dispatches to the active implementation.

Currently the Python implementation is used while the
native builder is being migrated to the new VertexBuffer API.
"""

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