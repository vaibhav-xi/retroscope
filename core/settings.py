"""
RetroScope

Typed Engine Settings

Provides a typed interface on top of the ParameterRegistry.

The ParameterRegistry remains the single source of truth.
"""

from __future__ import annotations

from core.parameters import ParameterRegistry


# ==========================================================
# Wave Settings
# ==========================================================

class WaveSettings:

    def __init__(self, registry: ParameterRegistry):

        self._registry = registry

    # -----------------------------------------------------

    @property
    def frequency(self) -> float:

        return self._registry.get(
            "wave.frequency",
            2.0,
        )

    @frequency.setter
    def frequency(
        self,
        value: float,
    ):

        self._registry.set(
            "wave.frequency",
            value,
        )

    # -----------------------------------------------------

    @property
    def amplitude(self) -> float:

        return self._registry.get(
            "wave.amplitude",
            0.30,
        )

    @amplitude.setter
    def amplitude(
        self,
        value: float,
    ):

        self._registry.set(
            "wave.amplitude",
            value,
        )

    # -----------------------------------------------------

    @property
    def speed(self) -> float:

        return self._registry.get(
            "wave.speed",
            1.0,
        )

    @speed.setter
    def speed(
        self,
        value: float,
    ):

        self._registry.set(
            "wave.speed",
            value,
        )


# ==========================================================
# Root Settings
# ==========================================================

class Settings:

    def __init__(self, registry: ParameterRegistry):

        self.wave = WaveSettings(
            registry
        )