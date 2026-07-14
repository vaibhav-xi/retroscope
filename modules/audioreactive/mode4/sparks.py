
from __future__ import annotations

import math

import numpy as np


class CometSparks:

    def __init__(self, capacity: int, random):

        self.capacity = capacity
        self.random = random

        self.origin_x = np.zeros(capacity, dtype=np.float32)
        self.origin_y = np.zeros(capacity, dtype=np.float32)
        self.angle = np.zeros(capacity, dtype=np.float32)
        self.distance = np.zeros(capacity, dtype=np.float32)
        self.speed = np.zeros(capacity, dtype=np.float32)
        self.age = np.zeros(capacity, dtype=np.float32)
        self.lifetime = np.ones(capacity, dtype=np.float32)
        self.alive = np.zeros(capacity, dtype=bool)

        self._cursor = 0

    # ---------------------------------------------------------

    def eject(
        self,
        origin,
        back_direction,
        count: int,
        speed_scale: float = 1.0,
        spread: float = math.pi / 6.0,
    ):

        ox, oy = origin
        bx, by = back_direction

        base_angle = math.atan2(by, bx)

        for _ in range(count):

            i = self._cursor

            self._cursor = (self._cursor + 1) % self.capacity

            self.origin_x[i] = ox
            self.origin_y[i] = oy
            self.angle[i] = base_angle + self.random.uniform(
                -spread, spread
            )
            self.distance[i] = 0.0
            self.speed[i] = (
                self.random.uniform(80.0, 220.0) * speed_scale
            )
            self.age[i] = 0.0
            self.lifetime[i] = self.random.uniform(0.15, 0.4)
            self.alive[i] = True

    # ---------------------------------------------------------

    def update(self, dt: float):

        active = self.alive

        self.age[active] += dt

        expired = self.alive & (self.age >= self.lifetime)

        self.alive[expired] = False

        active = self.alive

        self.distance[active] += self.speed[active] * dt

    # ---------------------------------------------------------

    def points(self):

        active = self.alive

        x = (
            self.origin_x[active]
            + self.distance[active] * np.cos(self.angle[active])
        )

        y = (
            self.origin_y[active]
            + self.distance[active] * np.sin(self.angle[active])
        )

        lifetime = np.maximum(self.lifetime[active], 1e-6)

        life = 1.0 - (self.age[active] / lifetime)

        return (
            np.column_stack([x, y]).astype(np.float32),
            life,
        )