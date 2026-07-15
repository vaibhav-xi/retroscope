
from __future__ import annotations

import random as _random_module

from modules.audioreactive.native import RingField


class ShockwaveField:

    def __init__(self, capacity: int, segments: int, random=None):

        self.capacity = capacity
        self.segments = segments

        self._field = RingField(capacity, random=random or _random_module.Random())

    # ---------------------------------------------------------

    def spawn(self, strength: float, speed: float, wobble: float = 0.0):

        self._field.spawn(
            strength=strength,
            speed=speed,
            wobble=wobble,
            start_radius=6.0,
            lifetime_base=0.5,
            lifetime_coefficient=0.03,
            randomize_rotation=False,
            start_rotation=0.0,
        )

    # ---------------------------------------------------------

    def update(self, dt: float):

        self._field.update(dt)

    # ---------------------------------------------------------

    def kick(self, positions, center, gain: float = 1.0):

        return self._field.kick(positions, center, gain=gain, band=16.0)

    # ---------------------------------------------------------

    def rings(self, center):
        """
        Matches the original wobble formula exactly (wobble_scale=6.0,
        wobble_frequency=5.0), with rotation fixed at 0 for every ring.
        """

        return self._field.rings(
            center,
            self.segments,
            wobble_scale=6.0,
            wobble_frequency=5.0,
        )
