"""
RetroScope

Module Manager

Owns all simulation modules.

Responsibilities
----------------
- Register modules
- Unregister modules
- Initialize modules
- Update modules
- Collect render data
- Shutdown modules

The manager NEVER imports pygame.
"""

from typing import List

from core.module import Module


class Manager:
    """
    Owns every active module.
    """

    def __init__(self):

        self._modules: List[Module] = []

    # ---------------------------------------------------------
    # Registration
    # ---------------------------------------------------------

    def register(self, module: Module) -> None:
        """
        Register a module.
        """

        self._modules.append(module)

    # ---------------------------------------------------------

    def unregister(self, module: Module) -> None:
        """
        Remove a module.
        """

        if module in self._modules:
            self._modules.remove(module)

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def initialize(self, context) -> None:
        """
        Initialize all modules.
        """

        for module in self._modules:

            if module.enabled:

                module.initialize(context)

    # ---------------------------------------------------------

    def update(self, context) -> None:
        """
        Update every active module.
        """

        for module in self._modules:

            if module.enabled:

                module.update(context)

    # ---------------------------------------------------------

    def emit(self, frame) -> None:
        """
        Ask every active module to emit render primitives.
        """

        for module in self._modules:

            if module.enabled:

                module.emit(frame)

    # ---------------------------------------------------------

    def shutdown(self) -> None:
        """
        Shutdown every module.
        """

        for module in self._modules:

            module.shutdown()

    # ---------------------------------------------------------

    @property
    def modules(self):
        """
        Read-only access to registered modules.
        """

        return tuple(self._modules)