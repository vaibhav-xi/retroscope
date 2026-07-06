from dataclasses import dataclass, field

from render.renderable import Renderable
from typing import Optional
from render_es2.geometry import Geometry

@dataclass
class RenderCommand:

    renderable: Renderable

    geometry: Optional[Geometry]


@dataclass
class RenderPacket:

    commands: list[RenderCommand] = field(
        default_factory=list
    )

    def add(self, command):

        self.commands.append(command)