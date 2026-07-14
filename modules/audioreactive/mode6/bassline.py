from __future__ import annotations

import numpy as np


class BasslineSpiral:

    def __init__(self, capacity: int):

        self.capacity = capacity

        self._angles = np.zeros(capacity, dtype=np.float32)
        self._confidence = np.zeros(capacity, dtype=np.float32)

        self._write = 0
        self._filled = 0

    # ---------------------------------------------------------

    def push(self, angle: float, confidence: float):

        self._angles[self._write] = angle
        self._confidence[self._write] = confidence

        self._write = (self._write + 1) % self.capacity

        self._filled = min(self._filled + 1, self.capacity)

    # ---------------------------------------------------------

    def points(self, center, inner_radius: float, radius_step: float):

        if self._filled < 2:

            return np.zeros((0, 2), dtype=np.float32)

        if self._filled < self.capacity:

            angles = self._angles[: self._filled]
            confidence = self._confidence[: self._filled]

        else:

            angles = np.concatenate(
                (self._angles[self._write:], self._angles[: self._write])
            )

            confidence = np.concatenate(
                (
                    self._confidence[self._write:],
                    self._confidence[: self._write],
                )
            )

        cx, cy = center

        count = len(angles)

        radii = (
            inner_radius
            + np.arange(count, dtype=np.float32) * radius_step
        )

        radii *= 0.3 + 0.7 * confidence

        x = cx + radii * np.cos(angles)
        y = cy + radii * np.sin(angles)

        return np.column_stack([x, y]).astype(np.float32)
