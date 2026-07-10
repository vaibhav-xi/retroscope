"""
RetroScope

Black Hole Lens Mathematics

Pure mathematical lens distortion.

This module knows nothing about

- Modules
- Renderables
- Frame
- OpenGL
- Geometry generation

It simply warps points.

Future visualizations may reuse these functions.
"""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np


EPSILON = 1e-6


# ----------------------------------------------------------------------
# Utility
# ----------------------------------------------------------------------

def distance(point: np.ndarray) -> float:
    """
    Euclidean distance from the origin.
    """

    return float(np.hypot(point[0], point[1]))


def normalize(point: np.ndarray) -> np.ndarray:
    """
    Safe vector normalization.
    """

    length = distance(point)

    if length < EPSILON:
        return np.zeros(2, dtype=np.float32)

    return point / length


# ----------------------------------------------------------------------
# Lens Strength
# ----------------------------------------------------------------------

def lens_strength(
    radius: float,
    strength: float,
) -> float:
    """
    Compute radial lens strength.

    Stronger near the center,
    weaker further away.
    """

    return strength / (radius * radius + EPSILON)


# ----------------------------------------------------------------------
# Point Distortion
# ----------------------------------------------------------------------

def distort_point(
    point: np.ndarray,
    strength: float,
) -> np.ndarray:
    """
    Apply simple radial gravitational lensing
    to a single point.
    """

    r = distance(point)

    if r < EPSILON:
        return point.copy()

    direction = normalize(point)

    offset = direction * lens_strength(r, strength)

    return point - offset


# ----------------------------------------------------------------------
# Polyline Distortion
# ----------------------------------------------------------------------

def distort_polyline(
    points: np.ndarray,
    strength: float,
) -> np.ndarray:
    """
    Distort every point in a polyline.
    """

    warped = np.empty_like(points)

    for i, point in enumerate(points):

        warped[i] = distort_point(
            point,
            strength,
        )

    return warped


# ----------------------------------------------------------------------
# Multiple Polylines
# ----------------------------------------------------------------------

def distort_polylines(
    polylines: Iterable[np.ndarray],
    strength: float,
):
    """
    Yield distorted copies of many polylines.
    """

    for polyline in polylines:

        yield distort_polyline(
            polyline,
            strength,
        )


# ----------------------------------------------------------------------
# Event Horizon Test
# ----------------------------------------------------------------------

def inside_event_horizon(
    point: np.ndarray,
    radius: float,
) -> bool:
    """
    Determine whether a point lies
    inside the event horizon.
    """

    return distance(point) <= radius


# ----------------------------------------------------------------------
# Photon Orbit
# ----------------------------------------------------------------------

def photon_orbit_radius(
    event_horizon_radius: float,
) -> float:
    """
    Approximate photon orbit radius.

    Purely artistic, not physically accurate.
    """

    return event_horizon_radius * 1.5


# ----------------------------------------------------------------------
# Warp Factor
# ----------------------------------------------------------------------

def warp_factor(
    point: np.ndarray,
    strength: float,
    event_horizon_radius: float,
) -> float:
    """
    Smooth warp factor useful for
    animation and visual effects.
    """

    r = distance(point)

    if r < event_horizon_radius:
        return 1.0

    x = (r - event_horizon_radius) / event_horizon_radius

    return strength / (1.0 + x * x)