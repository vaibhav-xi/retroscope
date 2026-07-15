from __future__ import annotations

import math

from modules.audioreactive.native import BurstField


class CometSparks:

    def __init__(self, capacity: int, random):

        self.capacity = capacity
        self.random = random

        self._field = BurstField(capacity, drag=0.0, random=random)

    # ---------------------------------------------------------

    def eject(
        self,
        origin,
        back_direction,
        count: int,
        speed_scale: float = 1.0,
        spread: float = math.pi / 6.0,
    ):

        bx, by = back_direction

        base_angle = math.atan2(by, bx)

        self._field.spawn(
            count,
            origin=origin,
            angle_range=(base_angle - spread, base_angle + spread),
            speed_range=(80.0 * speed_scale, 220.0 * speed_scale),
            lifetime_range=(0.15, 0.4),
        )

    # ---------------------------------------------------------

    def update(self, dt: float):

        self._field.update(dt)

    # ---------------------------------------------------------

    def points(self):
        """Matches the original 2-tuple (positions, life) API - BurstField
        returns a 4-tuple, truncated here."""

        positions, life, angle, speed = self._field.points()

        return positions, life
