import ctypes

import numpy as np

from OpenGL.GL import *

from render_es2.vao import VAO


class Mesh:

    def __init__(self):

        self.vao = VAO()

        self.vbo = glGenBuffers(1)

        self.count = 0

    # ---------------------------------------------------------

    def update(self, vertices):

        vertices = np.array(
            vertices,
            dtype=np.float32,
        )

        self.count = len(vertices) // 2

        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.vbo,
        )

        glBufferData(

            GL_ARRAY_BUFFER,

            vertices.nbytes,

            vertices,

            GL_DYNAMIC_DRAW,

        )

    # ---------------------------------------------------------

    def draw(self, shader):

        if self.count == 0:
            return

        self.vao.bind()

        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.vbo,
        )

        glEnableVertexAttribArray(0)

        glVertexAttribPointer(

            0,

            2,

            GL_FLOAT,

            GL_FALSE,

            0,

            ctypes.c_void_p(0),

        )

        glDrawArrays(

            GL_LINES,

            0,

            self.count,

        )