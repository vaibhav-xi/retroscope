from dataclasses import dataclass, field

from render_es2.mesh import Mesh


@dataclass
class RenderCommand:

    vertices: list[float]

    color: tuple[float, float, float]

    mesh: Mesh = field(
        default_factory=Mesh
    )


@dataclass
class RenderPacket:

    commands: list[RenderCommand] = field(
        default_factory=list
    )

    def add(self, command):

        self.commands.append(command)