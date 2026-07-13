from __future__ import annotations

import numpy as np


class EmberField:

    def __init__(
        self,
        capacity: int,
        inner_radius: float,
        random,
    ):

        self.capacity = capacity
        self.inner_radius = inner_radius
        self.random = random

        self.angle = np.zeros(capacity, dtype=np.float32)
        self.radius = np.zeros(capacity, dtype=np.float32)
        self.speed = np.zeros(capacity, dtype=np.float32)
        self.drift = np.zeros(capacity, dtype=np.float32)
        self.age = np.zeros(capacity, dtype=np.float32)
        self.lifetime = np.ones(capacity, dtype=np.float32)
        self.alive = np.zeros(capacity, dtype=bool)

        self._cursor = 0

    # ---------------------------------------------------------

    def spawn(self, count: int):
        """
        Spawn up to `count` new embers at the core, recycling the
        oldest slots first (ring buffer - no allocation).
        """

        for _ in range(count):

            i = self._cursor

            self._cursor = (self._cursor + 1) % self.capacity

            self.angle[i] = self.random.uniform(0.0, 2.0 * np.pi)
            self.radius[i] = self.inner_radius
            self.speed[i] = self.random.uniform(40.0, 140.0)
            self.drift[i] = self.random.uniform(-0.6, 0.6)
            self.age[i] = 0.0
            self.lifetime[i] = self.random.uniform(0.6, 1.6)
            self.alive[i] = True

    # ---------------------------------------------------------

    def update(self, dt: float):

        active = self.alive

        self.age[active] += dt

        expired = self.alive & (self.age >= self.lifetime)

        self.alive[expired] = False

        active = self.alive

        self.radius[active] += self.speed[active] * dt
        self.angle[active] += self.drift[active] * dt

    # ---------------------------------------------------------

    def points(self):
        """
        Returns:
            positions - (N, 2) array of currently alive embers,
                        centered on the origin.
            life      - (N,) array of remaining life, 1.0 (just
                        spawned) down to 0.0 (about to die).
        """

        active = self.alive

        angle = self.angle[active]
        radius = self.radius[active]

        x = radius * np.cos(angle)
        y = radius * np.sin(angle)

        lifetime = np.maximum(self.lifetime[active], 1e-6)

        life = 1.0 - (self.age[active] / lifetime)

        return (
            np.column_stack([x, y]).astype(np.float32),
            life,
        )