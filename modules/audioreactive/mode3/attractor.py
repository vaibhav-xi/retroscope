from __future__ import annotations

from modules.audioreactive.native import ChaosField


class DustAttractor:

    def __init__(self, capacity: int, random):

        self.capacity = capacity
        self.random = random

        self._field = ChaosField(capacity, random=random)

    # ---------------------------------------------------------

    def set_parameters(self, bass: float, mid: float, high: float):

        a = 1.2 + bass * 1.1
        b = -2.0 - mid * 0.9
        c = 2.1 + high * 1.1
        d = -1.7 - (bass * 0.3 + high * 0.6)

        self._field.set_parameters(a, b, c, d)

    # ---------------------------------------------------------

    def update(self, reseed_fraction: float = 0.02):
        """
        `dt` doesn't apply here - the chaos map advances one iteration
        per call regardless of frame timing, same as the original.
        The native ChaosField's `dt` parameter only decays `kick`
        (detonate()), which DustAttractor never uses, so passing 0.0
        is inert.
        """

        self._field.update(dt=0.0, reseed_fraction=reseed_fraction)

    # ---------------------------------------------------------

    def points(self, center, scale: float):

        return self._field.points(center, scale)
