from render_es2.render_pass import RenderPass
from OpenGL.GL import (
    glLineWidth,
    glBlendFunc,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_ONE,
)

class GeometryPass(RenderPass):

    def __init__(self, shader):

        self.shader = shader

    # ---------------------------------------------------------

    def execute(self, packet):

        self.shader.use()

        for command in packet.commands:

            renderable = command.renderable

            if command.geometry is not None:

                if renderable.is_dynamic:

                    renderable.mesh.update(
                        command.geometry.vertex_buffer
                    )

                elif renderable.is_dirty:

                    renderable.mesh.update(
                        command.geometry.vertex_buffer
                    )

                    renderable.is_dirty = False

            #
            # Bind material.
            #

            self.shader.set_color(
                renderable.material.color
            )

            self.shader.set_alpha(
                renderable.material.alpha
            )

            if renderable.material.additive:

                glBlendFunc(GL_SRC_ALPHA, GL_ONE)

            else:

                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            #
            # Draw.
            #

            renderable.mesh.draw(
                self.shader
            )
