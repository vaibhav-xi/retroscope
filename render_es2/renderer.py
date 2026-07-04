from pathlib import Path

from OpenGL.GL import *

from render_es2.shader import Shader
from render_es2.mesh import Mesh


class Renderer:

    def __init__(self):

        #
        # Clear color
        #

        glClearColor(
            0.0,
            0.0,
            0.0,
            1.0,
        )

        #
        # Load shaders
        #

        shader_dir = (
            Path(__file__).parent
            / "shaders"
        )

        vertex = (
            shader_dir / "simple.vert"
        ).read_text()

        fragment = (
            shader_dir / "simple.frag"
        ).read_text()

        self.shader = Shader(
            vertex,
            fragment,
        )

        #
        # Triangle
        #

        self.mesh = Mesh(
            [
                -0.6, -0.5,
                 0.6, -0.5,
                 0.0,  0.6,
            ]
        )

    # ---------------------------------------------------------

    def begin_frame(self):

        glClear(
            GL_COLOR_BUFFER_BIT
        )

        self.shader.use()

        self.mesh = Mesh(
            [
                -0.8, 0.0,
                0.8, 0.0,
            ]
        )

    # ---------------------------------------------------------

    def end_frame(self):

        pass