"""
RetroScope

Black Hole Projection

Projects local black hole geometry into the observer's view.

This is NOT rendering.

It is part of the simulation.

Input:
    Local-space points.

Output:
    Observer-space points.
"""

from __future__ import annotations

import math
from typing import Tuple

Point = Tuple[float, float]


# ---------------------------------------------------------
# Disk Projection
# ---------------------------------------------------------

def project_point(
    point: Point,
    inclination: float = 0.32,
    lens_strength: float = 40.0,
) -> Point:
    """
    Project one point of the accretion disk.

    The disk is first inclined and then the
    far side is lifted by an approximation of
    gravitational lensing.
    """

    x, y = point

    #
    # Inclination
    #

    y *= inclination

    #
    # Radius
    #

    r = math.hypot(x, y)

    if r < 1e-5:
        return x, y

    #
    # Approximate lens lift.
    #
    # The rear side of the disk is bent upward.
    #

    if y < 0.0:

        t = max(0.0, 1.0 - r / 260.0)

        lift = lens_strength * (t * t)

        y -= lift

    return x, y


# ---------------------------------------------------------
# Polyline
# ---------------------------------------------------------

def project_polyline(
    points,
    inclination: float = 0.32,
    lens_strength: float = 40.0,
):
    """
    Project an entire polyline.
    """

    return [

        project_point(

            p,

            inclination,

            lens_strength,

        )

        for p in points

    ]