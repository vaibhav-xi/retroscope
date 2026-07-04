from pathlib import Path

from OpenGL.GL import *

from render_es2.shader import Shader
from render_es2.geometry_builder import GeometryBuilder
from render_es2.passes.geometry import GeometryPass

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
        
        self.geometry_pass = GeometryPass(
            self.shader,
        )
        
    def render(self, frame):

        glClear(GL_COLOR_BUFFER_BIT)

        packet = GeometryBuilder.build(frame)

        self.geometry_pass.execute(
            packet
        )