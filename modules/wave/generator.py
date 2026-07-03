"""
RetroScope

Signal Generator

The SignalGenerator is responsible for producing normalized
waveform samples.

A sample is always in the range:

    -1.0 ... +1.0

The generator itself knows nothing about rendering.
"""

from __future__ import annotations

from math import pi, sin
from typing import Callable

import random


class SignalGenerator:
    """
    Generic signal generator.
    """

    def __init__(self):

        #
        # Signal function
        #

        self._function: Callable[[float], float] = self._sine

        #
        # Parameters
        #

        self.frequency = 2.0

        self.amplitude = 1.0

        self.phase = 0.0

    # ---------------------------------------------------------

    def set_function(
        self,
        function: Callable[[float], float],
    ) -> None:

        self._function = function

    # ---------------------------------------------------------

    def sample(self, t: float) -> float:
        """
        Return one normalized sample.
        """

        value = self._function(t)

        return self.amplitude * value

    # =========================================================
    # Built-in Signals
    # =========================================================

    def _sine(self, t: float) -> float:

        return sin(
            (2.0 * pi * self.frequency * t)
            + self.phase
        )

    # ---------------------------------------------------------

    def square(self, t: float) -> float:

        return 1.0 if self._sine(t) >= 0 else -1.0

    # ---------------------------------------------------------

    def triangle(self, t: float) -> float:

        x = (t * self.frequency + self.phase) % 1.0

        return 4.0 * abs(x - 0.5) - 1.0

    # ---------------------------------------------------------

    def saw(self, t: float) -> float:

        x = (t * self.frequency + self.phase) % 1.0

        return (x * 2.0) - 1.0

    # ---------------------------------------------------------

    def noise(self, t: float) -> float:

        _ = t

        return random.uniform(-1.0, 1.0)