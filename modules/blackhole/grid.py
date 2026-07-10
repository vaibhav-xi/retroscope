"""
RetroScope

Black Hole Gravitational Grid

Generates a Cartesian grid and applies
gravitational lens distortion.
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np

from .lens import distort_polyline

Point = Tuple[float, float]


def generate_lensing_grid(
    extent: float,
    spacing: float,
    strength: float,
) -> List[List[Point]]:
    """
    Generate a warped Cartesian grid.
    """

    lines: List[List[Point]] = []

    #
    # Horizontal
    #

    y = -extent

    while y <= extent:

        line = []

        x = -extent

        while x <= extent:

            line.append((x, y))

            x += spacing

        warped = distort_polyline(
            np.asarray(line, dtype=np.float32),
            strength,
        )

        lines.append(warped.tolist())

        y += spacing

    #
    # Vertical
    #

    x = -extent

    while x <= extent:

        line = []

        y = -extent

        while y <= extent:

            line.append((x, y))

            y += spacing

        warped = distort_polyline(
            np.asarray(line, dtype=np.float32),
            strength,
        )

        lines.append(warped.tolist())

        x += spacing

    return lines