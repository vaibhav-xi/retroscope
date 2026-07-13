from __future__ import annotations

import numpy as np


class DustAttractor:

    def __init__(self, capacity: int, random):

        self.capacity = capacity
        self.random = random

        self.x = np.zeros(capacity, dtype=np.float32)
        self.y = np.zeros(capacity, dtype=np.float32)

        self._seed(np.ones(capacity, dtype=bool))

        self.a = 1.4
        self.b = -2.3
        self.c = 2.4
        self.d = -2.1

    # ---------------------------------------------------------

    def _seed(self, mask):

        count = int(mask.sum())

        if count == 0:
            return

        self.x[mask] = np.array(
            [
                self.random.uniform(-1.5, 1.5)
                for _ in range(count)
            ],
            dtype=np.float32,
        )

        self.y[mask] = np.array(
            [
                self.random.uniform(-1.5, 1.5)
                for _ in range(count)
            ],
            dtype=np.float32,
        )

    # ---------------------------------------------------------

    def set_parameters(self, bass: float, mid: float, high: float):

        self.a = 1.2 + bass * 1.1
        self.b = -2.0 - mid * 0.9
        self.c = 2.1 + high * 1.1
        self.d = -1.7 - (bass * 0.3 + high * 0.6)

    # ---------------------------------------------------------

    def update(self, reseed_fraction: float = 0.02):

        x, y = self.x, self.y

        new_x = np.sin(self.a * y) - np.cos(self.b * x)
        new_y = np.sin(self.c * x) - np.cos(self.d * y)

        self.x = new_x.astype(np.float32)
        self.y = new_y.astype(np.float32)

        #
        # Continuously "rain" a small fraction of fresh points in,
        # so the cloud never fully settles onto one thin orbit.
        #

        reseed_count = max(
            1,
            int(self.capacity * reseed_fraction),
        )

        indices = self.random.sample(
            range(self.capacity),
            min(reseed_count, self.capacity),
        )

        mask = np.zeros(self.capacity, dtype=bool)
        mask[indices] = True

        self._seed(mask)

    # ---------------------------------------------------------

    def points(self, center, scale: float):

        cx, cy = center

        px = cx + self.x * scale
        py = cy + self.y * scale

        return np.column_stack([px, py]).astype(np.float32)
