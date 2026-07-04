from dataclasses import dataclass, field

from render_es2.mesh import Mesh

from render_es2.material import Material

@dataclass
class RenderCommand:

    vertices: list[float]

    material: Material

    mesh: Mesh = field(
        default_factory=Mesh
    )

    dynamic: bool = True


@dataclass
class RenderPacket:

    commands: list[RenderCommand] = field(
        default_factory=list
    )

    def add(self, command):

        self.commands.append(command)