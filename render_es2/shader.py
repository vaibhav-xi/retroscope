from OpenGL.GL import *

from render_es2._native import Shader as NativeShader
from render_es2.platform_gl import IS_DESKTOP_GL


class Shader:

    def __init__(self, vertex_src, fragment_src):

        if IS_DESKTOP_GL:

            vertex_src = self._desktop_vertex(vertex_src)
            fragment_src = self._desktop_fragment(fragment_src)

        self.native = NativeShader()

        self.native.create(
            vertex_src,
            fragment_src,
        )

    # -------------------------------------------------

    def use(self):

        self.native.use()

    # -------------------------------------------------

    def set_color(self, color):

        self.native.set_color(
            color[0],
            color[1],
            color[2],
        )

    # -------------------------------------------------

    def set_alpha(self, alpha):

        self.native.set_alpha(
            float(alpha)
        )

    # -------------------------------------------------

    def _desktop_vertex(self, src):

        return (
            "#version 410 core\n"
            "layout(location=0) in vec2 a_position;\n"
            "void main(){\n"
            "    gl_Position = vec4(a_position, 0.0, 1.0);\n"
            "}"
        )

    # -------------------------------------------------

    def _desktop_fragment(self, src):

        return (
            "#version 410 core\n"
            "uniform vec3 u_color;\n"
            "uniform float u_alpha;\n"
            "out vec4 FragColor;\n"
            "void main(){\n"
            "    FragColor = vec4(u_color, u_alpha);\n"
            "}"
        )
