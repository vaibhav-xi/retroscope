import ctypes
import numpy as np

from OpenGL.GL import *


class Mesh:

    def __init__(self, vertices):

        self.vertices = np.array(vertices, dtype=np.float32)

        self.vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glBufferData(
            GL_ARRAY_BUFFER,
            self.vertices.nbytes,
            self.vertices,
            GL_STATIC_DRAW,
        )

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.count = len(vertices) // 2

    # ---------------------------------------------------------

    def draw(self, shader):

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
            0,
            ctypes.c_void_p(0),
        )

        # glDrawArrays(
        #     GL_TRIANGLES,
        #     0,
        #     self.count,
        # )
        
        glDrawArrays(
            GL_LINES,
            0,
            self.count,
        )

        glDisableVertexAttribArray(location)

        glBindBuffer(GL_ARRAY_BUFFER, 0)