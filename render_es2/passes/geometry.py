from render_es2.render_pass import RenderPass
from OpenGL.GL import glLineWidth

class GeometryPass(RenderPass):

    def __init__(self, shader):

        self.shader = shader

    # ---------------------------------------------------------

    def execute(self, packet):

        self.shader.use()

        for command in packet.commands:

            renderable = command.renderable

            #
            # Upload only when needed.
            #

            if command.geometry is not None:

                if renderable.is_dynamic:

                    renderable.mesh.update(
                        command.geometry.vertices
                    )

                elif renderable.is_dirty:

                    renderable.mesh.update(
                        command.geometry.vertices
                    )

                    renderable.is_dirty = False

            #
            # Bind material.
            #

            self.shader.set_color(
                renderable.material.color
            )
            
            #
            # Line width.
            #
            # Note:
            # Many OpenGL ES 2.0 drivers clamp this to 1.0.
            # We keep it here so the Material API stays stable
            # when we later render thick lines as quads.
            #

            # glLineWidth(
            #     renderable.material.line_width
            # )

            #
            # Draw.
            #

            renderable.mesh.draw(
                self.shader
            )