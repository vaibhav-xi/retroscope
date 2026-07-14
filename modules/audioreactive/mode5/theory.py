
from __future__ import annotations

import math

import numpy as np

CIRCLE_OF_FIFTHS_POSITION = (
    0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5,
)

NOTE_NAMES = (
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B",
)

_INTERVAL_CONSONANCE = (
    1.00,  # 0  unison / octave
    0.05,  # 1  minor 2nd / major 7th
    0.25,  # 2  major 2nd / minor 7th
    0.65,  # 3  minor 3rd / major 6th
    0.75,  # 4  major 3rd / minor 6th
    0.90,  # 5  perfect 4th / perfect 5th
    0.10,  # 6  tritone
)


def interval_class(a: int, b: int) -> int:
    """
    Distance between two pitch classes, folded into 0..6.
    """

    diff = abs(a - b) % 12

    return min(diff, 12 - diff)


def edge_consonance(a: int, b: int) -> float:

    return _INTERVAL_CONSONANCE[interval_class(a, b)]


# ==========================================================
# Node Layout
# ==========================================================


def node_angle(pitch_class: int, rotation: float = 0.0) -> float:

    position = CIRCLE_OF_FIFTHS_POSITION[pitch_class % 12]

    return (
        rotation
        + (position / 12.0) * 2.0 * math.pi
        - math.pi / 2.0
    )


def node_position(pitch_class: int, center, radius: float, rotation: float = 0.0):

    angle = node_angle(pitch_class, rotation)

    cx, cy = center

    return (
        cx + radius * math.cos(angle),
        cy + radius * math.sin(angle),
    )


def node_positions(center, radius: float, rotation: float = 0.0) -> np.ndarray:

    positions = np.zeros((12, 2), dtype=np.float32)

    for pitch_class in range(12):

        positions[pitch_class] = node_position(
            pitch_class,
            center,
            radius,
            rotation,
        )

    return positions


ALL_EDGES = tuple(
    (a, b)
    for a in range(12)
    for b in range(a + 1, 12)
)
