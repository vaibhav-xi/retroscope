"""
RetroScope

Audio Reactive Mode 2 - Orbit Field

A ring of debris particles orbiting the core - distinct from
Mode 1's outward-bursting embers, this system drifts *around*
the core rather than away from it:

    bass  -> spawn count on each hit
    mid   -> orbital radius (the whole ring breathes together)
    high  -> orbital speed

Structure-of-arrays, fixed capacity, no per-frame allocation.

Pure simulation.
No renderer.
No OpenGL.
"""

from __future__ import annotations

import numpy as np


class OrbitField:

    def __init__(self, capacity: int, random):

        self.capacity = capacity
        self.random = random

        self.angle = np.zeros(capacity, dtype=np.float32)
        self.radius = np.zeros(capacity, dtype=np.float32)
        self.radius_bias = np.ones(capacity, dtype=np.float32)
        self.speed = np.zeros(capacity, dtype=np.float32)
        self.size = np.zeros(capacity, dtype=np.float32)
        self.alive = np.zeros(capacity, dtype=bool)

        self._cursor = 0

    # ---------------------------------------------------------

    def spawn(self, count: int, base_radius: float):

        for _ in range(count):

            i = self._cursor

            self._cursor = (self._cursor + 1) % self.capacity

            direction = 1.0 if self.random.random() < 0.5 else -1.0

            self.angle[i] = self.random.uniform(0.0, 2.0 * np.pi)
            self.radius_bias[i] = self.random.uniform(0.8, 1.2)
            self.radius[i] = base_radius * self.radius_bias[i]
            self.speed[i] = self.random.uniform(0.5, 1.6) * direction
            self.size[i] = self.random.uniform(3.0, 9.0)
            self.alive[i] = True

    # ---------------------------------------------------------

    def update(
        self,
        dt: float,
        radius_target: float,
        speed_scale: float,
    ):

        active = self.alive

        if not np.any(active):
            return

        self.angle[active] += (
            self.speed[active] * speed_scale * dt
        )

        target = radius_target * self.radius_bias[active]

        self.radius[active] += (
            target - self.radius[active]
        ) * 0.15

    # ---------------------------------------------------------

    def points(self, center):
        """
        Returns (positions, sizes) for every spawned particle,
        `positions` already in world space.
        """

        cx, cy = center

        active = self.alive

        x = cx + self.radius[active] * np.cos(self.angle[active])
        y = cy + self.radius[active] * np.sin(self.angle[active])

        return (
            np.column_stack([x, y]).astype(np.float32),
            self.size[active],
        )
