from pathlib import Path

from OpenGL.GL import *

from render_es2.shader import Shader
from render_es2.mesh import Mesh
from render_es2.geometry import Geometry


class Renderer:

    def __init__(self):

        glClearColor(
            0.0,
            0.0,
            0.0,
            1.0,
        )

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

    # -------------------------------------------------

    def render(self, frame):

        glClear(GL_COLOR_BUFFER_BIT)

        self.shader.use()

        vertices = Geometry.build(frame)

        #
        # Nothing to draw.
        #

        if len(vertices) < 4:
            return

        mesh = Mesh(vertices)

        mesh.draw(self.shader)