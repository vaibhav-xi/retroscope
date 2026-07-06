"""
RetroScope

Geometry

Container for GPU-ready geometry.
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Geometry:

    vertices: list[float] = field(
        default_factory=list
    )

    indices: Optional[list[int]] = None

    topology: int = 0