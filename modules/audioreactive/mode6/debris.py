
from __future__ import annotations

import math

import numpy as np


class Debris:

    def __init__(self, capacity: int, random, drag: float = 2.2):

        self.capacity = capacity
        self.random = random
        self.drag = drag

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

    def burst(
        self,
        origin,
        count: int,
        speed_range=(120.0, 420.0),
        lifetime_range=(0.3, 0.9),
        spread: float = 2.0 * math.pi,
        base_angle: float = 0.0,
    ):

        ox, oy = origin

        for _ in range(count):

            i = self._cursor

            self._cursor = (self._cursor + 1) % self.capacity

            self.origin_x[i] = ox
            self.origin_y[i] = oy

            self.angle[i] = base_angle + self.random.uniform(
                -spread * 0.5, spread * 0.5
            )

            self.distance[i] = 0.0
            self.speed[i] = self.random.uniform(*speed_range)
            self.age[i] = 0.0
            self.lifetime[i] = self.random.uniform(*lifetime_range)
            self.alive[i] = True

    # ---------------------------------------------------------

    def update(self, dt: float):

        active = self.alive

        self.age[active] += dt

        expired = self.alive & (self.age >= self.lifetime)

        self.alive[expired] = False

        active = self.alive

        self.speed[active] *= np.exp(-self.drag * dt)

        self.distance[active] += self.speed[active] * dt

    # ---------------------------------------------------------

    def segments(self):

        active = self.alive

        cos_a = np.cos(self.angle[active])
        sin_a = np.sin(self.angle[active])

        x = self.origin_x[active] + self.distance[active] * cos_a
        y = self.origin_y[active] + self.distance[active] * sin_a

        streak = 3.0 + self.speed[active] * 0.02

        tail_x = x - cos_a * streak
        tail_y = y - sin_a * streak

        lifetime = np.maximum(self.lifetime[active], 1e-6)

        life = 1.0 - (self.age[active] / lifetime)

        heads = np.column_stack([x, y]).astype(np.float32)
        tails = np.column_stack([tail_x, tail_y]).astype(np.float32)

        return heads, tails, life
