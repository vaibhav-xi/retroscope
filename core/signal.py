"""
RetroScope

Signal Registry

The Signal Registry owns every signal available to the engine.

Signals are identified by name.

Modules never communicate directly.

Instead they publish and consume signals through this registry.
"""

from __future__ import annotations

from typing import Callable


class Signal:
    """
    Represents one mathematical signal.

    A signal is simply:

        value = f(t)
    """

    def __init__(
        self,
        name: str,
        function: Callable[[float], float],
    ):

        self.name = name

        self.function = function

    # ---------------------------------------------------------

    def sample(self, t: float) -> float:

        return self.function(t)


# =============================================================


class SignalRegistry:
    """
    Stores all engine signals.
    """

    def __init__(self):

        self._signals = {}

    # ---------------------------------------------------------

    def register(
        self,
        signal: Signal,
    ) -> None:

        self._signals[signal.name] = signal

    # ---------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:

        self._signals.pop(name, None)

    # ---------------------------------------------------------

    def get(
        self,
        name: str,
    ) -> Signal | None:

        return self._signals.get(name)

    # ---------------------------------------------------------

    def sample(
        self,
        name: str,
        t: float,
    ) -> float:

        signal = self.get(name)

        if signal is None:

            return 0.0

        return signal.sample(t)

    # ---------------------------------------------------------

    def clear(self):

        self._signals.clear()

    # ---------------------------------------------------------

    def names(self):

        return tuple(self._signals.keys())