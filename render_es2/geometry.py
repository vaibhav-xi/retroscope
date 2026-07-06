"""
RetroScope

Geometry

Container for GPU-ready geometry.
"""

from dataclasses import dataclass
from typing import Optional

from render_es2.vertex_buffer import VertexBuffer


@dataclass
class Geometry:

    vertex_buffer: Optional[VertexBuffer] = None

    indices: Optional[list[int]] = None