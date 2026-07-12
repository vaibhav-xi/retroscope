"""
RetroScope

Black Hole V2

Simulation Component

Every phenomenon inside the black hole simulation derives from
SimulationComponent.

Examples

- AccretionDisk
- EventHorizon
- PhotonRing
- Environment
- LensingField

Components own simulation state.

Components emit Renderables.

Components never know about Frame or Renderer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from render.renderable import Renderable


class SimulationComponent(ABC):

    # ---------------------------------------------------------

    @abstractmethod
    def initialize(
        self,
        context,
    ):
        """
        Called once.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def update(
        self,
        context,
    ):
        """
        Advance simulation.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def renderables(
        self,
    ) -> list[Renderable]:
        """
        Return every Renderable owned by this component.

        Components own their Renderables.

        The simulation simply collects them.
        """
        pass

    # ---------------------------------------------------------

    @abstractmethod
    def shutdown(
        self,
    ):
        """
        Cleanup.
        """
        pass