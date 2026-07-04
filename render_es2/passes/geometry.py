from render_es2.render_pass import RenderPass


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

            if renderable.is_dynamic:

                renderable.mesh.update(
                    command.vertices
                )

            elif renderable.is_dirty:

                renderable.mesh.update(
                    command.vertices
                )

                renderable.is_dirty = False

            #
            # Bind material.
            #

            self.shader.set_color(
                renderable.material.color
            )

            #
            # Draw.
            #

            renderable.mesh.draw(
                self.shader
            )