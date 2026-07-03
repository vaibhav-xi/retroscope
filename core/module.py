"""
RetroScope

Module Interface

Every RetroScope module derives from Module.
"""

from abc import ABC, abstractmethod


class Module(ABC):

    def __init__(self, name: str):

        self.name = name
        self.enabled = True

    # ---------------------------------------------------------

    def enable(self):

        self.enabled = True

    # ---------------------------------------------------------

    def disable(self):

        self.enabled = False

    # ---------------------------------------------------------

    @abstractmethod
    def initialize(self, context):
        """
        Called once.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def update(self, context):
        """
        Update simulation.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def emit(self, context, frame):
        """
        Emit render primitives.

        Context is read-only.
        Frame is write-only.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def shutdown(self):
        pass