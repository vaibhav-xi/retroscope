
from __future__ import annotations

import numpy as np


class InfernoField:

    def __init__(self, capacity: int, random):

        self.capacity = capacity
        self.random = random

        self.x = np.zeros(capacity, dtype=np.float32)
        self.y = np.zeros(capacity, dtype=np.float32)

        self._seed(np.ones(capacity, dtype=bool))

        self.a = 1.0
        self.b = -1.8
        self.c = 1.8
        self.d = -1.4

        self._kick = 0.0

    # ---------------------------------------------------------

    def _seed(self, mask):

        count = int(mask.sum())

        if count == 0:
            return

        self.x[mask] = np.array(
            [self.random.uniform(-1.5, 1.5) for _ in range(count)],
            dtype=np.float32,
        )

        self.y[mask] = np.array(
            [self.random.uniform(-1.5, 1.5) for _ in range(count)],
            dtype=np.float32,
        )

    # ---------------------------------------------------------

    def set_parameters(self, tension: float, chord_energy: float):

        self.a = 1.0 + tension * 2.6
        self.b = -1.7 - chord_energy * 1.3
        self.c = 1.7 + tension * 2.2
        self.d = -1.4 - (tension * 0.9 + chord_energy * 0.6)

    # ---------------------------------------------------------

    def detonate(self, strength: float):

        self._kick = max(self._kick, strength)

    # ---------------------------------------------------------

    def update(self, dt: float, reseed_fraction: float = 0.02):

        self._kick *= np.exp(-dt * 3.0)

        x, y = self.x, self.y

        new_x = np.sin(self.a * y) - np.cos(self.b * x)
        new_y = np.sin(self.c * x) - np.cos(self.d * y)

        self.x = new_x.astype(np.float32)
        self.y = new_y.astype(np.float32)

        reseed_count = max(1, int(self.capacity * reseed_fraction))

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

        effective_scale = scale * (1.0 + self._kick)

        px = cx + self.x * effective_scale
        py = cy + self.y * effective_scale

        return np.column_stack([px, py]).astype(np.float32)
