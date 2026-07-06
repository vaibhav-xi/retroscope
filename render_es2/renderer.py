from pathlib import Path

from OpenGL.GL import *

from render_es2.shader import Shader
from render_es2.geometry_builder import GeometryBuilder
from render_es2.render_graph import RenderGraph
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
        
        self.shader.use()
        
        self.render_graph = RenderGraph()

        self.render_graph.add(

            GeometryPass(
                self.shader,
            )

        )
        
    def render(self, frame):

        glClear(GL_COLOR_BUFFER_BIT)

        packet = GeometryBuilder.build(frame)

        self.render_graph.execute(
            packet
        )