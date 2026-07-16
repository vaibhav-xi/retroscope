from __future__ import annotations

import math

import numpy as np

from .theory import ALL_EDGES, edge_consonance, node_angle

_EDGE_A = np.array([a for a, b in ALL_EDGES], dtype=np.int64)
_EDGE_B = np.array([b for a, b in ALL_EDGES], dtype=np.int64)

_EDGE_CONSONANCE = np.array(
    [edge_consonance(a, b) for a, b in ALL_EDGES],
    dtype=np.float32,
)


def lattice_edges(chroma, positions):

    brightness = (
        chroma[_EDGE_A] * chroma[_EDGE_B] * _EDGE_CONSONANCE
    ).astype(np.float32)

    points = np.stack(
        [positions[_EDGE_A], positions[_EDGE_B]],
        axis=1,
    ).astype(np.float32)

    return points, brightness


def node_pulse(pitch_class, positions, energy, base_size, gain, sides=6):

    cx, cy = positions[pitch_class]

    size = base_size + energy * gain

    angles = np.linspace(0.0, 2.0 * math.pi, sides, endpoint=False)

    x = cx + size * np.cos(angles)
    y = cy + size * np.sin(angles)

    points = np.column_stack([x, y]).astype(np.float32)

    return np.vstack([points, points[0]])


def chord_polygon(chord_tones, positions):

    points = np.array(
        [positions[pc] for pc in chord_tones],
        dtype=np.float32,
    )

    return np.vstack([points, points[0]])


def key_halo(tonic, center, radius, rotation, confidence, segments=40):

    cx, cy = center

    span = (0.12 + confidence * 0.55) * 2.0 * math.pi

    center_angle = node_angle(tonic, rotation)

    angles = np.linspace(
        center_angle - span * 0.5,
        center_angle + span * 0.5,
        segments,
    )

    x = cx + radius * np.cos(angles)
    y = cy + radius * np.sin(angles)

    return np.column_stack([x, y]).astype(np.float32)
