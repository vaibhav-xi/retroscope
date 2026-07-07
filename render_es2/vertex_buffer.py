"""
RetroScope

Vertex Buffer

CPU-side vertex storage.

Builders write vertices here.

Meshes upload them to the GPU.
"""

import numpy as np

class VertexBuffer:

    def __init__(self):

        self.vertices = np.empty(
            0,
            dtype=np.float32,
        )

        self.count = 0

    # ---------------------------------------------------------
    
    def __repr__(self):

        return (
            f"<VertexBuffer "
            f"id={id(self)} "
            f"count={self.count}>"
        )
        
    # ---------------------------------------------------------

    @classmethod
    def from_vertices(
        cls,
        vertices,
    ):

        vb = cls()

        vb.vertices = np.asarray(
            vertices,
            dtype=np.float32,
        )

        vb.count = len(vb.vertices)

        return vb

    # ---------------------------------------------------------

    def clear(self):

        self.count = 0

    # ---------------------------------------------------------

    def reserve(
        self,
        capacity,
    ):

        if self.vertices.size >= capacity:
            return

        new_vertices = np.empty(
            capacity,
            dtype=np.float32,
        )

        if self.count:
            new_vertices[:self.count] = \
                self.vertices[:self.count]

        self.vertices = new_vertices

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

    def ensure_capacity(
        self,
        additional,
    ):

        required = self.count + additional

        if required <= self.vertices.size:
            return

        new_capacity = max(

            required,

            max(
                1024,
                self.vertices.size * 2,
            ),

        )

        new_vertices = np.empty(

            new_capacity,

            dtype=np.float32,

        )

        if self.count:

            new_vertices[:self.count] = \
                self.vertices[:self.count]

        self.vertices = new_vertices

    # ---------------------------------------------------------

    def push(
        self,
        value,
    ):

        self.ensure_capacity(1)

        self.vertices[
            self.count
        ] = value

        self.count += 1

    # ---------------------------------------------------------

    def push2(
        self,
        x,
        y,
    ):

        self.ensure_capacity(2)

        self.vertices[
            self.count
        ] = x

        self.vertices[
            self.count + 1
        ] = y

        self.count += 2

    # ---------------------------------------------------------

    def data(self):

        return self.vertices

    # ---------------------------------------------------------

    def set_count(
        self,
        count,
    ):

        self.count = count