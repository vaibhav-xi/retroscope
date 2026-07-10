"""
RetroScope

Black Hole Event Horizon

Pure geometry generation for the event horizon.

No renderer.
No modules.
No OpenGL.
"""

from __future__ import annotations

import math
from typing import List, Tuple

Point = Tuple[float, float]


def generate_event_horizon(
    radius: float,
    segments: int = 256,
) -> List[Point]:
    """
    Generate a circular event horizon.
    """

    points: List[Point] = []

    for i in range(segments + 1):

        angle = (i / segments) * math.tau

        points.append(
            (
                radius * math.cos(angle),
                radius * math.sin(angle),
            )
        )

    return points