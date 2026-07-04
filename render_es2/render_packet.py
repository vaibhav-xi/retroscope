from dataclasses import dataclass, field


@dataclass
class RenderCommand:

    vertices: list[float]

    color: tuple[float, float, float]


@dataclass
class RenderPacket:

    commands: list[RenderCommand] = field(
        default_factory=list
    )

    def add(self, command):

        self.commands.append(command)