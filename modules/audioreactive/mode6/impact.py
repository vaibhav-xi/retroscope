
from __future__ import annotations

import math

import numpy as np


class ImpactSystem:

    def __init__(self):

        self.shake_offset = np.zeros(2, dtype=np.float32)
        self.shake_velocity = np.zeros(2, dtype=np.float32)

        self.node_impulse = np.zeros(12, dtype=np.float32)
        self.node_impulse_velocity = np.zeros(12, dtype=np.float32)

        self.scale_pulse = 1.0
        self.scale_velocity = 0.0

        self.spin_velocity = 0.0

        self.flash = 0.0

    # ---------------------------------------------------------

    def shake(self, strength: float, random):

        angle = random.uniform(0.0, 2.0 * math.pi)

        self.shake_velocity[0] += math.cos(angle) * strength
        self.shake_velocity[1] += math.sin(angle) * strength

    # ---------------------------------------------------------

    def kick_node(self, pitch_class: int, strength: float):

        self.node_impulse_velocity[pitch_class % 12] += strength

    # ---------------------------------------------------------

    def kick_all_nodes(self, strengths):

        self.node_impulse_velocity += strengths

    # ---------------------------------------------------------

    def kick_scale(self, strength: float):

        self.scale_velocity += strength

    # ---------------------------------------------------------

    def kick_spin(self, strength: float):

        self.spin_velocity += strength

    # ---------------------------------------------------------

    def ignite_flash(self, strength: float):

        self.flash = max(self.flash, strength)

    # ---------------------------------------------------------

    def update(self, dt: float):

        self.shake_velocity += -self.shake_offset * 90.0 * dt
        self.shake_velocity *= math.exp(-dt * 10.0)
        self.shake_offset += self.shake_velocity * dt

        self.node_impulse_velocity += -self.node_impulse * 40.0 * dt
        self.node_impulse_velocity *= math.exp(-dt * 6.0)
        self.node_impulse += self.node_impulse_velocity * dt

        self.scale_velocity += (1.0 - self.scale_pulse) * 26.0 * dt
        self.scale_velocity *= math.exp(-dt * 5.0)
        self.scale_pulse += self.scale_velocity * dt

        self.spin_velocity *= math.exp(-dt * 1.5)

        self.flash *= math.exp(-dt * 6.0)
