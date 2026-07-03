"""
RetroScope

Module Interface

Every simulation inside RetroScope derives from Module.

A Module owns its own simulation state.

A Module NEVER imports pygame.

A Module NEVER performs rendering directly.

A Module ONLY:

    1. Updates its internal simulation.
    2. Emits render primitives into the Frame.
"""

from abc import ABC, abstractmethod


class Module(ABC):
    """
    Base class for every RetroScope module.

    Examples
    --------
    WaveModule
    SandModule
    FFTModule
    ParticleModule
    GalaxyModule
    GridModule
    OverlayModule
    """

    def __init__(self, name: str):

        self.name = name

        self.enabled = True

    # ---------------------------------------------------------

    def enable(self):

        """Enable the module."""

        self.enabled = True

    # ---------------------------------------------------------

    def disable(self):

        """Disable the module."""

        self.enabled = False

    # ---------------------------------------------------------

    @abstractmethod
    def initialize(self, context):
        """
        Called once when the module is loaded.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def update(self, context):
        """
        Advance the simulation.

        Called once every frame.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def emit(self, frame):
        """
        Emit render primitives into the Frame.

        The module MUST NOT render directly.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def shutdown(self):
        """
        Called before the module is unloaded.
        """
        pass