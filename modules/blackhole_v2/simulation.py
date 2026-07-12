"""
RetroScope

Black Hole V2

Simulation

Owns every simulation component.

The simulation coordinates component lifecycle but contains
no simulation logic itself.
"""

from __future__ import annotations

from .components.component import SimulationComponent


class BlackHoleSimulation:

    def __init__(self):

        self._components: list[SimulationComponent] = []

    # ---------------------------------------------------------

    def add(
        self,
        component: SimulationComponent,
    ):

        self._components.append(
            component
        )

    # ---------------------------------------------------------

    def initialize(
        self,
        context,
    ):

        for component in self._components:

            component.initialize(
                context
            )

    # ---------------------------------------------------------

    def update(
        self,
        context,
    ):

        for component in self._components:

            component.update(
                context
            )

    # ---------------------------------------------------------

    def renderables(
        self,
    ):

        for component in self._components:

            yield from component.renderables()

    # ---------------------------------------------------------

    def shutdown(
        self,
    ):

        for component in self._components:

            component.shutdown()