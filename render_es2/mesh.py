import ctypes
from array import array

from OpenGL.GL import *
import numpy as np
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
        
        self.vao.bind()

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        #
        # Position
        #

        glEnableVertexAttribArray(0)

        glVertexAttribPointer(
            0,
            2,
            GL_FLOAT,
            GL_FALSE,
            5 * 4,
            ctypes.c_void_p(0),
        )

        #
        # Color
        #

        glEnableVertexAttribArray(1)

        glVertexAttribPointer(
            1,
            3,
            GL_FLOAT,
            GL_FALSE,
            5 * 4,
            ctypes.c_void_p(2 * 4),
        )

        glDrawArrays(
            GL_LINES,
            0,
            self.count,
        )

        # glDisableVertexAttribArray(0)
        # glDisableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)