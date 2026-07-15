
from __future__ import annotations

import numpy as np

from modules.audioreactive.native import radial_ring


def petal_ring(
    center,
    base_radius: float,
    petal_amplitude: float,
    petal_count: float,
    rotation: float,
    segments: int,
) -> np.ndarray:

    #
    # Computed with the rotation already baked in, matching the
    # original exactly - the petal pattern's phase and its on-screen
    # position rotate together, not independently.
    #

    angles = rotation + np.linspace(
        0.0,
        2.0 * np.pi,
        segments,
        endpoint=False,
    )

    radius = base_radius + petal_amplitude * np.sin(
        angles * petal_count
    )

    return radial_ring(
        radius,
        base_angle=rotation,
        center=center,
    )


def kaleidoscope_layers(
    center,
    layer_count: int,
    base_radius: float,
    radius_step: float,
    petal_amplitude: float,
    petal_count: float,
    rotation: float,
    segments: int,
):

    for i in range(layer_count):

        direction = 1.0 if i % 2 == 0 else -1.0

        yield petal_ring(
            center=center,
            base_radius=base_radius + radius_step * i,
            petal_amplitude=petal_amplitude,
            petal_count=petal_count + i,
            rotation=rotation * direction,
            segments=segments,
        )
