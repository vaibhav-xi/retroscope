from render_es2.render_pass import RenderPass


class GeometryPass(RenderPass):

    def __init__(
        self,
        shader,
    ):

        self.shader = shader

    # ---------------------------------------------

    def execute(
        self,
        packet,
    ):

        self.shader.use()

        for command in packet.commands:

            if command.dynamic:

                command.mesh.update(
                    command.vertices
                )

            command.mesh.draw(
                self.shader
            )