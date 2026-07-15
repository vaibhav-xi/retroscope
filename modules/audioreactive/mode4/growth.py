
from __future__ import annotations

import math

import numpy as np


class GrowthTree:

    def __init__(
        self,
        capacity: int,
        max_depth: int,
        random,
    ):

        self.capacity = capacity
        self.max_depth = max_depth
        self.random = random

        self.branches = []

        for _ in range(3):

            self._spawn(
                origin=(0.0, 0.0),
                angle=self.random.uniform(0.0, 2.0 * math.pi),
                depth=0,
            )

    # ---------------------------------------------------------

    def _spawn(self, origin, angle, depth):

        if depth > self.max_depth:
            return

        if len(self.branches) >= self.capacity:
            self.branches.pop(0)

        target_length = self.random.uniform(24.0, 52.0) * (
            0.75 ** depth
        )

        self.branches.append(
            {
                "origin": origin,
                "angle": angle,
                "length": 0.0,
                "target_length": target_length,
                "depth": depth,
                "growing": True,
                "bloomed": False,
            }
        )

    # ---------------------------------------------------------

    def _tip(self, branch):

        ox, oy = branch["origin"]

        x = ox + math.cos(branch["angle"]) * branch["length"]
        y = oy + math.sin(branch["angle"]) * branch["length"]

        return (x, y)

    # ---------------------------------------------------------

    def update(
        self,
        dt: float,
        ambient_rate: float,
        spawn_chance: float,
    ):

        for branch in self.branches:

            if branch["growing"]:

                branch["length"] = min(
                    branch["length"] + ambient_rate * dt,
                    branch["target_length"],
                )

                if branch["length"] >= branch["target_length"]:

                    branch["growing"] = False

                    if branch["depth"] >= 1:
                        branch["bloomed"] = True

        if self.branches and self.random.random() < spawn_chance:

            self.fork(count=1)

    # ---------------------------------------------------------

    def spurt(self, amount: float):
        """
        Bass hit: every currently-growing tip lurches forward.
        """

        for branch in self.branches:

            if branch["growing"]:

                branch["length"] = min(
                    branch["length"] + amount,
                    branch["target_length"],
                )

                if branch["length"] >= branch["target_length"]:

                    branch["growing"] = False

                    if branch["depth"] >= 1:
                        branch["bloomed"] = True

    # ---------------------------------------------------------

    def fork(self, count: int = 1):
        """
        Treble hit (or ambient trickle): sprout `count` new
        branches from random existing tips.
        """

        if not self.branches:
            return

        parents = self.random.sample(
            self.branches,
            min(count, len(self.branches)),
        )

        for parent in parents:

            tip = self._tip(parent)

            spread = self.random.uniform(-0.9, 0.9)

            self._spawn(
                origin=tip,
                angle=parent["angle"] + spread,
                depth=parent["depth"] + 1,
            )

    # ---------------------------------------------------------

    def segments(self):

        n = len(self.branches)

        if n == 0:

            return np.zeros((0, 2, 2), dtype=np.float32)

        points = np.empty((n, 2, 2), dtype=np.float32)

        for i, branch in enumerate(self.branches):

            ox, oy = branch["origin"]
            tx, ty = self._tip(branch)

            points[i, 0, 0] = ox
            points[i, 0, 1] = oy
            points[i, 1, 0] = tx
            points[i, 1, 1] = ty

        return points

    # ---------------------------------------------------------

    def blossoms(self):

        bloomed = [b for b in self.branches if b["bloomed"]]

        n = len(bloomed)

        if n == 0:

            return np.zeros((0, 13, 2), dtype=np.float32)

        points = np.empty((n, 13, 2), dtype=np.float32)

        for i, branch in enumerate(bloomed):

            tx, ty = self._tip(branch)

            size = 5.0 * (0.8 ** branch["depth"])

            points[i, 0, 0] = tx
            points[i, 0, 1] = ty

            for k in range(6):

                angle = branch["angle"] + (k / 6.0) * math.tau

                points[i, 1 + k * 2, 0] = tx + math.cos(angle) * size
                points[i, 1 + k * 2, 1] = ty + math.sin(angle) * size

                points[i, 2 + k * 2, 0] = tx
                points[i, 2 + k * 2, 1] = ty

        return points