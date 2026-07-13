"""
RetroScope

Audio Reactive Mode 2 - Lightning

Treble transients spawn short-lived jagged bolts, built with
recursive midpoint displacement (a tiny fractal), radiating
outward from the core.

Bolts are cheap: each one only exists for a handful of frames
and recursion depth is capped, so a burst of hi-hats never costs
more than a few dozen extra points - safe for a Raspberry Pi 3B.

Pure simulation.
No renderer.
No OpenGL.
"""

from __future__ import annotations

import math

import numpy as np


def _displace(p0, p1, depth, jitter, random, out):

    if depth <= 0:

        out.append(p1)

        return

    mx = (p0[0] + p1[0]) * 0.5
    my = (p0[1] + p1[1]) * 0.5

    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]

    length = math.hypot(dx, dy)

    if length > 1e-6:

        nx, ny = -dy / length, dx / length

    else:

        nx, ny = 0.0, 0.0

    offset = random.uniform(-jitter, jitter)

    mid = (mx + nx * offset, my + ny * offset)

    _displace(p0, mid, depth - 1, jitter * 0.55, random, out)

    _displace(mid, p1, depth - 1, jitter * 0.55, random, out)


def bolt(
    origin,
    angle: float,
    length: float,
    depth: int,
    random,
) -> np.ndarray:

    tip = (
        origin[0] + math.cos(angle) * length,
        origin[1] + math.sin(angle) * length,
    )

    points = [origin]

    _displace(origin, tip, depth, length * 0.18, random, points)

    return np.array(points, dtype=np.float32)


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

            yield bolt(
                b["origin"],
                b["angle"],
                b["length"],
                self.depth,
                self.random,
            )
