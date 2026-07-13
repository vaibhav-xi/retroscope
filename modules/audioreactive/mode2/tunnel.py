"""
RetroScope

Audio Reactive Mode 2 - Pulse Tunnel

Bass hits spawn a polygon "shell" that expands outward from the
core. Older shells recede and lose sides as they age, dissolving
into a rough low-poly outline instead of just vanishing (the
Material API has no alpha channel today, so "fading" has to be
done through geometry instead of transparency).

Structure-of-arrays, ring-buffer allocation - no per-frame
allocation, safe for a Raspberry Pi 3B.

Pure simulation.
No renderer.
No OpenGL.
"""

from __future__ import annotations

import math

import numpy as np


class PulseTunnel:

    def __init__(
        self,
        capacity: int,
        sides: int,
        random,
    ):

        self.capacity = capacity
        self.sides = sides
        self.random = random

        self.radius = np.zeros(capacity, dtype=np.float32)
        self.speed = np.zeros(capacity, dtype=np.float32)
        self.rotation = np.zeros(capacity, dtype=np.float32)
        self.spin = np.zeros(capacity, dtype=np.float32)
        self.age = np.zeros(capacity, dtype=np.float32)
        self.lifetime = np.ones(capacity, dtype=np.float32)
        self.alive = np.zeros(capacity, dtype=bool)

        self._cursor = 0

    # ---------------------------------------------------------

    def spawn(self, strength: float = 1.0):

        i = self._cursor

        self._cursor = (self._cursor + 1) % self.capacity

        self.radius[i] = 12.0
        self.speed[i] = 160.0 + strength * 220.0
        self.rotation[i] = self.random.uniform(0.0, 2.0 * math.pi)
        self.spin[i] = self.random.uniform(-1.2, 1.2)
        self.age[i] = 0.0
        self.lifetime[i] = 0.9 + strength * 0.5
        self.alive[i] = True

    # ---------------------------------------------------------

    def update(self, dt: float):

        active = self.alive

        self.age[active] += dt

        expired = self.alive & (self.age >= self.lifetime)

        self.alive[expired] = False

        active = self.alive

        self.radius[active] += self.speed[active] * dt

        self.rotation[active] += self.spin[active] * dt

    # ---------------------------------------------------------

    def shells(self, center):

        cx, cy = center

        for i in np.nonzero(self.alive)[0]:

            life = 1.0 - (
                self.age[i] / max(self.lifetime[i], 1e-6)
            )

            visible_sides = max(
                3,
                int(self.sides * min(life * 1.4, 1.0)),
            )

            angles = self.rotation[i] + np.linspace(
                0.0,
                2.0 * math.pi,
                visible_sides + 1,
            )

            x = cx + self.radius[i] * np.cos(angles)
            y = cy + self.radius[i] * np.sin(angles)

            points = np.column_stack([x, y]).astype(np.float32)

            yield points, life
