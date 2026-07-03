"""
RetroScope

Frame

A Frame represents everything that should appear on the screen
during one engine update.

Simulation modules never draw directly.

Instead, they add render primitives to the Frame.

The Renderer later converts these primitives into pixels.

This file MUST NEVER import pygame.
"""

from dataclasses import dataclass, field
from typing import List

from render.primitives import Primitive


@dataclass
class Frame:
    """
    Renderer-independent frame.

    The Frame is recreated (or cleared) every engine tick.
    Modules emit primitives into this object.
    """

    primitives: List[Primitive] = field(default_factory=list)

    # ---------------------------------------------------------

    def add(self, primitive: Primitive) -> None:
        """
        Add a render primitive.
        """

        self.primitives.append(primitive)

    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove every primitive from this frame.
        """

        self.primitives.clear()

    # ---------------------------------------------------------

    def __len__(self) -> int:

        return len(self.primitives)

    # ---------------------------------------------------------

    def __iter__(self):

        return iter(self.primitives)