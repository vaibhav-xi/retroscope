"""
RetroScope

Vertex Buffer

A CPU-side vertex buffer.

Builders generate VertexBuffers.

Meshes upload VertexBuffers to the GPU.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class VertexBuffer:

    vertices: np.ndarray

    @classmethod
    def from_vertices(
        cls,
        vertices,
    ):

        return cls(

            vertices=np.asarray(
                vertices,
                dtype=np.float32,
            )

        )