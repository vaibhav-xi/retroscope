from dataclasses import dataclass, field

from render.renderable import Renderable

from typing import Optional

@dataclass
class RenderCommand:

    renderable: Renderable

    vertices: Optional[list[float]]


@dataclass
class RenderPacket:

    commands: list[RenderCommand] = field(
        default_factory=list
    )

    def add(self, command):

        self.commands.append(command)