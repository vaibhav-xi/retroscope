from __future__ import annotations

from modules.audioreactive.native import RingField


class PulseTunnel:

    def __init__(
        self,
        capacity: int,
        sides: int,
        random,
    ):

        self.capacity = capacity
        self.sides = sides
        self.random = random

        self._field = RingField(capacity, random=random)

    # ---------------------------------------------------------

    def spawn(self, strength: float = 1.0):

        self._field.spawn(
            strength=strength,
            speed=160.0 + strength * 220.0,
            wobble=0.0,
            start_radius=12.0,
            spin_range=(-1.2, 1.2),
            lifetime_base=0.9,
            lifetime_coefficient=0.5,
        )

    # ---------------------------------------------------------

    def update(self, dt: float):

        self._field.update(dt)

    # ---------------------------------------------------------

    def shells(self, center):

        return self._field.shells(center, self.sides)
