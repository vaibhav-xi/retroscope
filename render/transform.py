"""
RetroScope

Transform

Represents the position, rotation and scale of a Renderable.

The transform is currently a data container only.

Future responsibilities:

- Matrix generation
- Parent/child transforms
- World transforms
- GPU uniform upload
"""

from dataclasses import dataclass


@dataclass
class Transform:
    """
    Spatial transform.
    """

    x: float = 0.0

    y: float = 0.0

    rotation: float = 0.0

    scale_x: float = 1.0

    scale_y: float = 1.0