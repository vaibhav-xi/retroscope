import ctypes

from OpenGL.GL import *
from render_es2.vao import VAO
from render_es2._native import (
    Mesh as NativeMesh,
    gl_upload,
)

class Mesh:

    def __init__(self):

        self.vao = VAO()

        self.native = NativeMesh()

        self.native.create()

        self.vbo = self.native.vbo

        self.count = 0

    # ---------------------------------------------------------

    def update(self, vertex_buffer):

        if vertex_buffer is None:
            return

        self.native.vertex_count = (
            vertex_buffer.count // 2
        )

        gl_upload(
            self.vbo,
            vertex_buffer,
        )

    # ---------------------------------------------------------

    def draw(self, shader):
        
        self.vao.bind()

        self.native.draw()