"""
RetroScope

Renderable

A Renderable groups one or more primitives into a single
renderable object.

Future responsibilities:

- Static/Dynamic
- Dirty flag
- Material
- Visibility
- GPU mesh
"""

from dataclasses import dataclass, field

from render_backup.primitives import Primitive


@dataclass
class Renderable:

    primitives: list[Primitive] = field(
        default_factory=list
    )

    dynamic: bool = True

    visible: bool = True

    # ---------------------------------------------------------

    def add(self, primitive: Primitive):

        self.primitives.append(
            primitive
        )