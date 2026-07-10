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
from render_es2.material import Material
from render_es2.mesh import Mesh
from typing import Optional
from render.transform import Transform
from render_es2.geometry import Geometry

@dataclass
class Renderable:

    primitives: list[Primitive] = field(default_factory=list)

    material: Material = field(
        default_factory=lambda: Material(
            color=(0.0, 1.0, 0.4),
        )
    )
    
    mesh: Mesh = field(
        default_factory=Mesh
    )
    
    transform: Transform = field(
        default_factory=Transform
    )
    
    cached_geometry: Optional[Geometry] = None

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
        
    # ---------------------------------------------------------

    def clear(self):

        self.primitives.clear()

        self.is_dirty = True