
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

        for branch in self.branches:

            ox, oy = branch["origin"]

            tx, ty = self._tip(branch)

            points = np.array(
                [[ox, oy], [tx, ty]],
                dtype=np.float32,
            )

            yield points, branch["depth"]

    # ---------------------------------------------------------

    def blossoms(self):

        for branch in self.branches:

            if not branch["bloomed"]:
                continue

            tx, ty = self._tip(branch)

            size = 5.0 * (0.8 ** branch["depth"])

            points = [(tx, ty)]

            for i in range(6):

                angle = branch["angle"] + (i / 6.0) * math.tau

                points.append(
                    (
                        tx + math.cos(angle) * size,
                        ty + math.sin(angle) * size,
                    )
                )

                points.append((tx, ty))

            yield (
                np.array(points, dtype=np.float32),
                branch["depth"],
            )