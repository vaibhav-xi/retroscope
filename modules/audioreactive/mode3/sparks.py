from __future__ import annotations

import math

from modules.audioreactive.native import BurstField


class SparkBurst:

    def __init__(self, capacity: int, random):

        self.capacity = capacity
        self.random = random

        self._field = BurstField(capacity, drag=0.0, random=random)

    # ---------------------------------------------------------

    def burst(self, origin, count: int, speed_scale: float = 1.0):

        #
        # speed_scale multiplying the *sampled* speed is equivalent to
        # multiplying the sampling range's bounds by the same (always
        # positive) factor - same distribution, same result.
        #

        self._field.spawn(
            count,
            origin=origin,
            angle_range=(0.0, 2.0 * math.pi),
            speed_range=(80.0 * speed_scale, 220.0 * speed_scale),
            lifetime_range=(0.15, 0.4),
        )

    # ---------------------------------------------------------

    def update(self, dt: float):

        self._field.update(dt)

    # ---------------------------------------------------------

    def points(self):

        positions, life, angle, speed = self._field.points()

        return positions, life
