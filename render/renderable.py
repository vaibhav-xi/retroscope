"""
RetroScope

Renderable

A Renderable groups one or more primitives into a single
renderable object.

Future responsibilities:

- Material
- Static/Dynamic
- Dirty flag
- Visibility
- GPU mesh cache
"""

from dataclasses import dataclass, field

from render.primitives import Primitive


@dataclass
class Renderable:

    primitives: list[Primitive] = field(
        default_factory=list
    )

    is_dynamic: bool = True

    is_visible: bool = True

    is_dirty: bool = True

    # ---------------------------------------------------------

    @classmethod
    def from_primitive(
        cls,
        primitive: Primitive,
    ):

        renderable = cls()

        renderable.primitives.append(
            primitive
        )

        return renderable

    # ---------------------------------------------------------

    def add(
        self,
        primitive: Primitive,
    ):

        self.primitives.append(
            primitive
        )

        self.is_dirty = True