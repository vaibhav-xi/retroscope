"""
RetroScope

Black Hole Plasma Simulation

Simulates plasma streamlines orbiting a black hole.

This module performs simulation only.

No rendering.
No geometry emission.
No OpenGL.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import List

from .projection import project_polyline

# ----------------------------------------------------------------------
# Plasma Particle
# ----------------------------------------------------------------------

@dataclass
class PlasmaParticle:

    radius: float

    angle: float

    angular_velocity: float

    length: float

    phase: float


# ----------------------------------------------------------------------
# Plasma System
# ----------------------------------------------------------------------

class PlasmaSystem:

    def __init__(
        self,
        inner_radius: float,
        outer_radius: float,
        count: int = 800,
        seed: int = 1,
    ):

        self.inner_radius = inner_radius
        self.outer_radius = outer_radius

        self.random = random.Random(seed)

        self.particles: List[PlasmaParticle] = []

        self._initialize(count)

    # ---------------------------------------------------------

    def _initialize(
        self,
        count: int,
    ):

        span = self.outer_radius - self.inner_radius

        for _ in range(count):

            radius = self.inner_radius + self.random.random() * span

            #
            # Keplerian approximation
            #

            omega = 4000.0 / (radius ** 1.5)

            self.particles.append(

                PlasmaParticle(

                    radius=radius,

                    angle=self.random.random() * math.tau,

                    angular_velocity=omega,

                    length=self.random.uniform(6.0, 18.0),

                    phase=self.random.random() * math.tau,

                )

            )

    # ---------------------------------------------------------

    def update(
        self,
        dt: float,
    ):

        for particle in self.particles:

            particle.angle += particle.angular_velocity * dt

            particle.phase += dt * 2.0

    # ---------------------------------------------------------

    def streamlines(
        self,
    ):
        """
        Yield short plasma streaks.

        Each streak consists of a few points trailing behind
        the particle's current orbit.
        """

        for particle in self.particles:

            points = []

            segments = 8

            for i in range(segments):

                t = i / (segments - 1)

                angle = (

                    particle.angle

                    - t * particle.length * 0.015

                )

                #
                # Small turbulence
                #

                radius = (

                    particle.radius

                    + math.sin(

                        particle.phase

                        + angle * 4.0

                    ) * 1.5

                )

                #
                # Disk inclination
                #

                inclination = 0.32

                x = radius * math.cos(angle)

                y = radius * math.sin(angle) * inclination

                points.append(

                    (

                        x,

                        y,

                    )

                )

            yield project_polyline(points)