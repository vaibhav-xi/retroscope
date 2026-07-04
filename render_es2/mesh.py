import ctypes
from array import array

from OpenGL.GL import *
import numpy as np

class Mesh:

    def __init__(self):

        self.vbo = glGenBuffers(1)
        self.count = 0

    # ---------------------------------------------------------

    def update(self, vertices):

        vertices = np.array(
            vertices,
            dtype=np.float32,
        )

        self.count = len(vertices) // 5

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glBufferData(
            GL_ARRAY_BUFFER,
            vertices.nbytes,
            vertices,
            GL_DYNAMIC_DRAW,
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)

    # ---------------------------------------------------------

    def draw(self, shader):

        if self.count == 0:
            return

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        location = glGetAttribLocation(
            shader.program,
            "a_position",
        )

        glEnableVertexAttribArray(location)

        glVertexAttribPointer(
            location,
            2,
            GL_FLOAT,
            GL_FALSE,
            5 * 4,
            ctypes.c_void_p(0),
        )

        glDrawArrays(
            GL_LINES,
            0,
            self.count,
        )

        glDisableVertexAttribArray(location)

        glBindBuffer(GL_ARRAY_BUFFER, 0)