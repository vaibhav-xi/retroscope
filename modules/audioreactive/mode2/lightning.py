from __future__ import annotations

import math

from modules.audioreactive.native import lightning_bolt


class LightningField:

    def __init__(
        self,
        capacity: int,
        depth: int,
        random,
    ):

        self.capacity = capacity
        self.depth = depth
        self.random = random

        self._bolts = []

    # ---------------------------------------------------------

    def spawn(
        self,
        origin,
        count: int,
        min_length: float,
        max_length: float,
    ):

        for _ in range(count):

            if len(self._bolts) >= self.capacity:

                self._bolts.pop(0)

            angle = self.random.uniform(0.0, 2.0 * math.pi)

            length = self.random.uniform(min_length, max_length)

            self._bolts.append(
                {
                    "origin": origin,
                    "angle": angle,
                    "length": length,
                    "age": 0.0,
                    "lifetime": self.random.uniform(0.08, 0.18),
                }
            )

    # ---------------------------------------------------------

    def update(self, dt: float):

        for b in self._bolts:

            b["age"] += dt

        self._bolts = [
            b for b in self._bolts if b["age"] < b["lifetime"]
        ]

    # ---------------------------------------------------------

    def polylines(self):

        for b in self._bolts:

            yield lightning_bolt(
                b["origin"],
                b["angle"],
                b["length"],
                self.depth,
                random=self.random,
            )
