import ctypes

from OpenGL.GL import *
from render_es2.vao import VAO

class Mesh:

    def __init__(self):

        self.vao = VAO()

        self.vbo = glGenBuffers(1)

        self.count = 0

    # ---------------------------------------------------------

    def update(self, vertex_buffer):

        if vertex_buffer is None:
            return

        vertices = vertex_buffer.vertices[
            :vertex_buffer.count
        ]
        
        # print(
        #     "count =", vertex_buffer.count,
        #     "array =", len(vertex_buffer.vertices),
        # )

        self.count = vertex_buffer.count // 2
        
        # print(
        #     "Mesh.update",
        #     id(self),
        #     id(vertex_buffer),
        #     vertex_buffer.count,
        # )
        
        # print(vertices[:12])
        
        # print(
        #     type(vertices),
        #     len(vertices),
        # )
        
        # print(
        #     vertices[:12]
        # )

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