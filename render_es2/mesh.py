import ctypes

from OpenGL.GL import *
from render_es2.vao import VAO
from render_es2._native import gl_upload

class Mesh:

    def __init__(self):

        self.vao = VAO()

        self.vbo = glGenBuffers(1)

        self.count = 0

    # ---------------------------------------------------------

    def update(self, vertex_buffer):

        if vertex_buffer is None:
            return

        self.count = vertex_buffer.count // 2

        gl_upload(
            self.vbo,
            vertex_buffer,
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
        
        # print("draw", self.count)
        
        # print(
        #     "Mesh.draw",
        #     id(self),
        #     self.count,
        # )

        glDrawArrays(

            GL_TRIANGLES,

            0,

            self.count,

        )