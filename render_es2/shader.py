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

    def set_size(self, size):

        self.native.set_size(
            float(size)
        )

    # -------------------------------------------------

    def set_intensity(self, intensity):

        self.native.set_intensity(
            float(intensity)
        )

    # -------------------------------------------------

    def _desktop_vertex(self, src):

        return (
            "#version 410 core\n"
            "layout(location=0) in vec2 a_position;\n"
            "layout(location=1) in vec3 a_texcoord;\n"
            "out vec3 v_texcoord;\n"
            "void main(){\n"
            "    v_texcoord = a_texcoord;\n"
            "    gl_Position = vec4(a_position, 0.0, 1.0);\n"
            "}"
        )

    # -------------------------------------------------

    def _desktop_fragment(self, src):

        return (
            "#version 410 core\n"
            "uniform vec3 u_color;\n"
            "uniform float u_alpha;\n"
            "uniform float u_size;\n"
            "uniform float u_intensity;\n"
            "in vec3 v_texcoord;\n"
            "out vec4 FragColor;\n"
            "void main(){\n"
            "    float u = v_texcoord.x;\n"
            "    float v = v_texcoord.y;\n"
            "    float len = v_texcoord.z;\n"
            "    float sigma = max(u_size * 0.6, 0.5);\n"
            "    float perpendicular = exp(-(v*v) / (2.0*sigma*sigma));\n"
            "    float longitudinal = clamp(min(u, len - u) / sigma + 1.0, 0.0, 1.0);\n"
            "    float density = u_intensity / max(len, sigma);\n"
            "    float glow = clamp(perpendicular * mix(0.4, 1.0, longitudinal) * density, 0.0, 1.0);\n"
            "    FragColor = vec4(u_color, u_alpha * glow);\n"
            "}"
        )
