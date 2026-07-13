"""
RetroScope

Audio Reactive Mode 2 - Kaleidoscope

Nested, counter-rotating polygon/petal rings.

Each ring is a single closed polyline sampled from a
star/flower function, so vertex count per ring stays constant
while the music only changes shape and radius - point count,
and therefore draw cost, never scales with the music.

Pure geometry.
No renderer.
No OpenGL.
"""

from __future__ import annotations

import math

import numpy as np


def petal_ring(
    center,
    base_radius: float,
    petal_amplitude: float,
    petal_count: float,
    rotation: float,
    segments: int,
) -> np.ndarray:

    cx, cy = center

    angles = rotation + np.linspace(
        0.0,
        2.0 * math.pi,
        segments,
        endpoint=False,
    )

    radius = base_radius + petal_amplitude * np.sin(
        angles * petal_count
    )

    x = cx + radius * np.cos(angles)
    y = cy + radius * np.sin(angles)

    points = np.column_stack([x, y]).astype(np.float32)

    points = np.vstack([points, points[0]])

    return points


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
