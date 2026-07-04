"""
RetroScope

Frame

A Frame represents everything that should appear on the screen
during one engine update.

Simulation modules never draw directly.

Instead, they emit render primitives into render layers.

The Renderer later converts those layers into GPU commands.

This file MUST NEVER import pygame.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Iterator, List

from render.primitives import Primitive


class Layer(Enum):
    """
    Rendering order.
    """

    BACKGROUND = auto()

    MAIN = auto()

    OVERLAY = auto()

    UI = auto()


@dataclass
class Frame:
    """
    Renderer-independent frame.

    Modules emit primitives into render layers.
    """

    layers: Dict[Layer, List[Primitive]] = field(
        default_factory=lambda: {
            Layer.BACKGROUND: [],
            Layer.MAIN: [],
            Layer.OVERLAY: [],
            Layer.UI: [],
        }
    )

    # ---------------------------------------------------------

    def add(
        self,
        primitive: Primitive,
        layer: Layer = Layer.MAIN,
    ) -> None:
        """
        Add a primitive to a render layer.
        """

        self.layers[layer].append(
            primitive
        )

    # ---------------------------------------------------------

    def primitives(self) -> Iterator[Primitive]:
        """
        Iterate over every primitive in render order.
        """

        for layer in Layer:

            yield from self.layers[layer]

    # ---------------------------------------------------------

    def clear(self) -> None:
        """
        Remove every primitive.
        """

        for primitives in self.layers.values():

            primitives.clear()

    # ---------------------------------------------------------

    def __len__(self) -> int:

        return sum(

            len(primitives)

            for primitives in self.layers.values()

        )

    # ---------------------------------------------------------

    def __iter__(self):

        return self.primitives()