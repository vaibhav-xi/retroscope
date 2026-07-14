
from __future__ import annotations

import numpy as np


class PulseComet:

    def __init__(self, trail_length: int):

        self.trail_length = trail_length

        self.history = np.zeros((trail_length, 2), dtype=np.float32)

        self._filled = 0
        self._cursor = 0

        self.t = 0.0

    # ---------------------------------------------------------

    def update(
        self,
        dt: float,
        bass: float,
        mid: float,
        high: float,
        center,
    ):

        cx, cy = center

        speed = 0.6 + mid * 1.2 + high * 1.6

        self.t += dt * speed

        ratio_a = 3.0 + mid * 2.0
        ratio_b = 2.0 + high * 3.0

        radius = 70.0 + bass * 90.0

        x = cx + radius * np.sin(ratio_a * self.t)
        y = cy + radius * np.sin(ratio_b * self.t + 1.3)

        self.history[self._cursor] = (x, y)

        self._cursor = (self._cursor + 1) % self.trail_length

        self._filled = min(self._filled + 1, self.trail_length)

    # ---------------------------------------------------------

    def trail(self) -> np.ndarray:

        if self._filled < self.trail_length:

            return self.history[: self._filled]

        return np.concatenate(
            [
                self.history[self._cursor :],
                self.history[: self._cursor],
            ]
        )
