"""
RetroScope

Vertex Buffer

CPU-side vertex storage.

Builders write vertices here.

Meshes upload them to the GPU.
"""

from dataclasses import dataclass, field

import numpy as np


@dataclass
class VertexBuffer:

    #
    # CPU vertex data.
    #

    vertices: np.ndarray = field(

        default_factory=lambda:

            np.empty(
                0,
                dtype=np.float32,
            )

    )

    #
    # Number of valid floats.
    #

    count: int = 0

    # ---------------------------------------------------------

    @classmethod
    def from_vertices(
        cls,
        vertices,
    ):

        array = np.asarray(
            vertices,
            dtype=np.float32,
        )

        return cls(

            vertices=array,

            count=len(array),

        )

    # ---------------------------------------------------------

    def clear(self):

        self.vertices = np.empty(
            0,
            dtype=np.float32,
        )

        self.count = 0
        
        # ---------------------------------------------------------

    def reserve(
        self,
        capacity,
    ):

        if self.vertices.size >= capacity:
            return

        self.vertices = np.empty(
            capacity,
            dtype=np.float32,
        )

        self.count = 0

    # ---------------------------------------------------------

    def append(
        self,
        vertices,
    ):

        vertices = np.asarray(
            vertices,
            dtype=np.float32,
        )

        required = self.count + len(vertices)

        if required > self.vertices.size:

            new_capacity = max(
                required,
                max(
                    1024,
                    self.vertices.size * 2,
                ),
            )

            new_array = np.empty(
                new_capacity,
                dtype=np.float32,
            )

            if self.count:

                new_array[:self.count] = \
                    self.vertices[:self.count]

            self.vertices = new_array

        self.vertices[
            self.count:required
        ] = vertices

        self.count = required
        
    # ---------------------------------------------------------

    def push(
        self,
        value,
    ):

        if self.count >= self.vertices.size:

            new_capacity = max(
                1024,
                self.vertices.size * 2,
            )

            new_array = np.empty(
                new_capacity,
                dtype=np.float32,
            )

            if self.count:

                new_array[:self.count] = \
                    self.vertices[:self.count]

            self.vertices = new_array

        self.vertices[self.count] = value

        self.count += 1
        
    # ---------------------------------------------------------

    def push2(
        self,
        x,
        y,
    ):

        self.push(x)
        self.push(y)