"""
RetroScope

Black Hole Photon Rings

Pure procedural generation of unstable photon rings.

No renderer.
No OpenGL.
No modules.

Only geometry.
"""

from __future__ import annotations

import math
from typing import List, Tuple

Point = Tuple[float, float]


# ----------------------------------------------------------------------
# Photon Ring
# ----------------------------------------------------------------------

def photon_ring(
    radius: float,
    segments: int,
    amplitude: float = 2.0,
    frequency: float = 8.0,
    phase: float = 0.0,
) -> List[Point]:
    """
    Generate one distorted photon ring.
    """

    points: List[Point] = []

    for i in range(segments + 1):

        t = i / segments

        angle = t * math.tau

        r = radius + amplitude * math.sin(
            frequency * angle + phase
        )

        points.append(
            (
                r * math.cos(angle),
                r * math.sin(angle),
            )
        )

    return points


# ----------------------------------------------------------------------
# Photon Rings
# ----------------------------------------------------------------------

def generate_photon_rings(
    radius: float,
    count: int,
    spacing: float,
    segments: int = 256,
    amplitude: float = 2.0,
    frequency: float = 8.0,
    phase: float = 0.0,
) -> List[List[Point]]:
    """
    Generate multiple concentric photon rings.
    """

    rings: List[List[Point]] = []

    for i in range(count):

        rings.append(

            photon_ring(

                radius=radius + spacing * i,

                segments=segments,

                amplitude=amplitude,

                frequency=frequency,

                phase=phase + i * 0.35,

            )

        )

    return rings