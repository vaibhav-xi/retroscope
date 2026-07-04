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

    def _check(self, where):

        err = glGetError()

        if err != GL_NO_ERROR:

            print(f"[GL ERROR] {where}: {hex(err)}")

    # ---------------------------------------------------------

    def update(self, vertices):

        vertices = np.array(
            vertices,
            dtype=np.float32,
        )

        self.count = len(vertices) // 5

        print(
            "Uploading",
            self.count,
            "vertices",
        )

        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.vbo,
        )

        self._check("BindBuffer(update)")

        glBufferData(

            GL_ARRAY_BUFFER,

            vertices.nbytes,

            vertices,

            GL_DYNAMIC_DRAW,

        )

        self._check("BufferData")

        #
        # Intentionally leave buffer bound.
        #

    # ---------------------------------------------------------

    def draw(self, shader):

        if self.count == 0:
            return

        self.vao.bind()

        self._check("VAO bind")

        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.vbo,
        )

        self._check("BindBuffer(draw)")

        #
        # Position
        #

        glEnableVertexAttribArray(0)

        self._check("EnableAttrib0")

        glVertexAttribPointer(

            0,

            2,

            GL_FLOAT,

            GL_FALSE,

            5 * 4,

            ctypes.c_void_p(0),

        )

        self._check("AttribPointer0")

        #
        # Color
        #

        glEnableVertexAttribArray(1)

        self._check("EnableAttrib1")

        glVertexAttribPointer(

            1,

            3,

            GL_FLOAT,

            GL_FALSE,

            5 * 4,

            ctypes.c_void_p(2 * 4),

        )

        self._check("AttribPointer1")

        print(
            "Drawing",
            self.count,
            "vertices",
        )

        glDrawArrays(

            GL_LINES,

            0,

            self.count,

        )

        self._check("DrawArrays")

        #
        # Leave attributes enabled for now.
        #