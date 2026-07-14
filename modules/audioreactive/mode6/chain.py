from __future__ import annotations

import numpy as np


def lightning_bolt(p0, p1, depth: int, jitter: float, random):

    points = [
        np.asarray(p0, dtype=np.float32),
        np.asarray(p1, dtype=np.float32),
    ]

    for level in range(depth):

        current_jitter = jitter * (0.55 ** level)

        new_points = [points[0]]

        for i in range(len(points) - 1):

            a = points[i]
            b = points[i + 1]

            mid = (a + b) * 0.5

            if random is not None and current_jitter > 0.0:

                mid = mid + np.array(
                    [
                        random.uniform(-current_jitter, current_jitter),
                        random.uniform(-current_jitter, current_jitter),
                    ],
                    dtype=np.float32,
                )

            new_points.append(mid)
            new_points.append(b)

        points = new_points

    return np.array(points, dtype=np.float32)


class ChainFlashes:

    def __init__(self, capacity: int = 24):

        self.capacity = capacity
        self._items = []

    # ---------------------------------------------------------

    def spawn(self, points, lifetime: float = 0.35):

        if len(self._items) >= self.capacity:

            self._items.pop(0)

        self._items.append(
            {"points": points, "age": 0.0, "lifetime": lifetime}
        )

    # ---------------------------------------------------------

    def update(self, dt: float):

        for item in self._items:

            item["age"] += dt

        self._items = [
            item for item in self._items if item["age"] < item["lifetime"]
        ]

    # ---------------------------------------------------------

    def segments(self):

        for item in self._items:

            life = 1.0 - item["age"] / max(item["lifetime"], 1e-6)

            yield item["points"], life
