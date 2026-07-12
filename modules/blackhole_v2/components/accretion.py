"""
RetroScope

Black Hole V2

Accretion Disk

Simulates the glowing plasma orbiting the event horizon.

The particle system is private.

The component exposes only Renderables.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from render.renderable import Renderable
from render.primitives import Polyline
from render_es2.material import Material

from .component import SimulationComponent


# ==========================================================
# Private Particle
# ==========================================================

@dataclass(slots=True)
class _Particle:

    position: np.ndarray

    velocity: np.ndarray

    brightness: float

    lifetime: float

    age: float

    trail: list[np.ndarray]


# ==========================================================
# Accretion Disk
# ==========================================================

class AccretionDisk(SimulationComponent):

    def __init__(

        self,

        particle_count: int = 2500,

        inner_radius: float = 90.0,

        outer_radius: float = 260.0,

    ):

        self.particle_count = particle_count

        self.inner_radius = inner_radius

        self.outer_radius = outer_radius

        self.random = None

        self._particles: list[_Particle] = []

        #
        # ONE renderable.
        #

        self.renderable = Renderable(

            material=Material(

                color=(1.0, 0.85, 0.35),

                line_width=1.5,

            ),

            is_dynamic=True,

        )

    # ---------------------------------------------------------

    def initialize(

        self,

        context,

    ):

        self.random = context.random

        self._particles.clear()

        for _ in range(

            self.particle_count

        ):

            self._particles.append(

                self._spawn()

            )

    # ---------------------------------------------------------

    def _spawn(self):

        angle = self.random.uniform(

            0.0,

            math.tau,

        )

        radius = self.random.uniform(

            self.inner_radius,

            self.outer_radius,

        )

        position = np.array(

            [

                math.cos(angle) * radius,

                math.sin(angle) * radius,

            ],

            dtype=np.float32,

        )

        velocity = np.zeros(

            2,

            dtype=np.float32,

        )

        return _Particle(

            position=position,

            velocity=velocity,

            brightness=1.0,

            lifetime=self.random.uniform(

                8.0,

                20.0,

            ),

            age=0.0,

            trail=[],

        )

    # ---------------------------------------------------------

    def update(
        self,
        context,
    ):

        dt = context.delta_time

        for particle in self._particles:

            particle.age += dt

            #
            # Current position.
            #

            x, y = particle.position

            r = max(

                math.hypot(x, y),

                self.inner_radius,

            )

            #
            # Unit vectors.
            #

            radial = particle.position / r

            tangent = np.array(

                [

                    -radial[1],

                    radial[0],

                ],

                dtype=np.float32,

            )

            #
            # Keplerian rotation.
            #

            orbital_speed = (

                260.0 /

                math.sqrt(r)

            )

            orbital = (

                tangent *

                orbital_speed

            )

            #
            # Slow inward drift.
            #

            inward = (

                radial *

                -10.0

            )

            #
            # Organic turbulence.
            #

            angle = math.atan2(y, x)

            turbulence = (

                math.sin(

                    angle * 7.0 +

                    context.elapsed_time * 2.5

                )

                *

                math.cos(

                    r * 0.04 -

                    context.elapsed_time

                )

            )

            velocity = (

                orbital +

                inward +

                tangent * turbulence * 8.0

            )

            particle.velocity = velocity

            particle.position += (

                velocity * dt

            )

            #
            # Record trail.
            #

            particle.trail.append(

                particle.position.copy()

            )

            if len(

                particle.trail

            ) > 32:

                particle.trail.pop(0)

            #
            # Respawn.
            #

            if (

                r <= self.inner_radius

                or

                particle.age >= particle.lifetime

            ):

                replacement = self._spawn()

                particle.position = replacement.position
                particle.velocity = replacement.velocity
                particle.brightness = replacement.brightness
                particle.lifetime = replacement.lifetime
                particle.age = replacement.age
                particle.trail = replacement.trail

    # ---------------------------------------------------------

    def renderables(

        self,

    ):

        self.renderable.primitives.clear()

        #
        # Placeholder geometry.
        #

        for particle in self._particles:

            if len(

                particle.trail

            ) < 2:

                continue

            self.renderable.add(

                Polyline(

                    np.asarray(

                        particle.trail,

                        dtype=np.float32,

                    )

                )

            )

        return [

            self.renderable

        ]

    # ---------------------------------------------------------

    def shutdown(

        self,

    ):

        self._particles.clear()