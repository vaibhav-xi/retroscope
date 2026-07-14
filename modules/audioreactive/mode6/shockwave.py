
from __future__ import annotations

import math

import numpy as np


class BlastField:

    def __init__(self, capacity: int, segments: int):

        self.capacity = capacity
        self.segments = segments

        self.radius = np.zeros(capacity, dtype=np.float32)
        self.speed = np.zeros(capacity, dtype=np.float32)
        self.strength = np.zeros(capacity, dtype=np.float32)
        self.wobble = np.zeros(capacity, dtype=np.float32)
        self.age = np.zeros(capacity, dtype=np.float32)
        self.lifetime = np.ones(capacity, dtype=np.float32)
        self.alive = np.zeros(capacity, dtype=bool)

        self._cursor = 0

    # ---------------------------------------------------------

    def spawn(self, strength: float, speed: float, wobble: float = 0.0, start_radius: float = 6.0):

        i = self._cursor

        self._cursor = (self._cursor + 1) % self.capacity

        self.radius[i] = start_radius
        self.speed[i] = speed
        self.strength[i] = strength
        self.wobble[i] = wobble
        self.age[i] = 0.0
        self.lifetime[i] = 0.4 + strength * 0.025
        self.alive[i] = True

    # ---------------------------------------------------------

    def update(self, dt: float):

        active = self.alive

        self.age[active] += dt

        expired = self.alive & (self.age >= self.lifetime)

        self.alive[expired] = False

        active = self.alive

        self.radius[active] += self.speed[active] * dt

    # ---------------------------------------------------------

    def rings(self, center):

        cx, cy = center

        for i in np.nonzero(self.alive)[0]:

            life = 1.0 - (
                self.age[i] / max(self.lifetime[i], 1e-6)
            )

            angles = np.linspace(
                0.0,
                2.0 * math.pi,
                self.segments + 1,
            )

            wobble_amount = self.wobble[i] * 8.0 * life

            radius = self.radius[i] + wobble_amount * np.sin(angles * 6.0)

            x = cx + radius * np.cos(angles)
            y = cy + radius * np.sin(angles)

            points = np.column_stack([x, y]).astype(np.float32)

            yield points, life
