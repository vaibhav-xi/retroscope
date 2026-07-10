"""
RetroScope

Black Hole Accretion Disk

Pure procedural generation of accretion disk streamlines.

No renderer.
No module.
No frame.
No OpenGL.

Only geometry.
"""

from __future__ import annotations

import math
from typing import List, Tuple

Point = Tuple[float, float]


# ----------------------------------------------------------------------
# Spiral
# ----------------------------------------------------------------------

def spiral(
    inner_radius: float,
    outer_radius: float,
    turns: float,
    segments: int,
    rotation: float = 0.0,
) -> List[Point]:
    """
    Generate one Archimedean spiral.
    """

    points: List[Point] = []

    total_angle = turns * math.tau

    for i in range(segments + 1):

        t = i / segments

        angle = rotation + total_angle * t

        radius = inner_radius + (
            outer_radius - inner_radius
        ) * t

        points.append(
            (
                radius * math.cos(angle),
                radius * math.sin(angle),
            )
        )

    return points


# ----------------------------------------------------------------------
# Spiral Arm
# ----------------------------------------------------------------------

def spiral_arm(
    inner_radius: float,
    outer_radius: float,
    turns: float,
    segments: int,
    rotation: float,
) -> List[Point]:
    """
    Alias for readability.
    """

    return spiral(
        inner_radius=inner_radius,
        outer_radius=outer_radius,
        turns=turns,
        segments=segments,
        rotation=rotation,
    )


# ----------------------------------------------------------------------
# Disk
# ----------------------------------------------------------------------

def generate_disk(
    inner_radius: float,
    outer_radius: float,
    arms: int,
    turns: float,
    rotation: float,
    segments: int = 400,
) -> List[List[Point]]:
    """
    Generate an entire accretion disk.

    Returns a list of spiral streamlines.
    """

    disk: List[List[Point]] = []

    for arm in range(arms):

        angle = (arm / arms) * math.tau

        disk.append(

            spiral_arm(

                inner_radius=inner_radius,

                outer_radius=outer_radius,

                turns=turns,

                segments=segments,

                rotation=rotation + angle,

            )

        )

    return disk