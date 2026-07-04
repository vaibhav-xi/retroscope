from pathlib import Path

from OpenGL.GL import *

from render_es2.shader import Shader
from render_es2.mesh import Mesh
from render_es2.geometry_builder import GeometryBuilder


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

        #
        # Create ONE mesh forever
        #

        self.mesh = Mesh()
        
    def render(self, frame):

        glClear(GL_COLOR_BUFFER_BIT)

        self.shader.use()

        packet = GeometryBuilder.build(frame)

        for command in packet.commands:

            if len(command.vertices) < 4:
                continue

            self.mesh.update(command.vertices)

            self.mesh.draw(self.shader)