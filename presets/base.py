"""
RetroScope

Preset Base Class

A preset configures the engine into a particular state.

A preset may change:

- Theme
- Parameters
- Signals

Presets NEVER perform rendering.
Presets NEVER update every frame.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Preset(ABC):
    """
    Base class for every RetroScope preset.
    """

    def __init__(self, name: str):

        self.name = name

    # ---------------------------------------------------------

    @abstractmethod
    def apply(self, context) -> None:
        """
        Apply this preset to the engine.

        Implementations may modify:

            context.theme
            context.parameters
            context.signals
        """
        pass

    # ---------------------------------------------------------

    def __str__(self) -> str:

        return self.name