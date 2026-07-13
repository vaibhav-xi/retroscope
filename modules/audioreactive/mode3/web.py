
from __future__ import annotations

import math

import numpy as np


def _spoke_lengths(spectrum, spoke_count):

    n = len(spectrum)

    idx = np.linspace(
        0,
        n,
        spoke_count,
        endpoint=False,
    ).astype(int) % n

    return spectrum[idx]


def web_rings(
    center,
    spectrum,
    ring_count: int,
    spoke_count: int,
    base_radius: float,
    radius_step: float,
    amplitude: float,
    rotation: float,
):

    cx, cy = center

    lengths = _spoke_lengths(spectrum, spoke_count)

    for r in range(ring_count):

        direction = 1.0 if r % 2 == 0 else -1.0

        ring_rotation = (
            rotation * direction
            + (math.pi / spoke_count) * r
        )

        angles = ring_rotation + np.linspace(
            0.0,
            2.0 * math.pi,
            spoke_count,
            endpoint=False,
        )

        radius = (
            base_radius
            + radius_step * r
            + lengths * amplitude * (1.0 - r * 0.12)
        )

        x = cx + radius * np.cos(angles)
        y = cy + radius * np.sin(angles)

        points = np.column_stack([x, y]).astype(np.float32)

        points = np.vstack([points, points[0]])

        yield points


def web_spokes(
    center,
    spectrum,
    ring_count: int,
    spoke_count: int,
    base_radius: float,
    radius_step: float,
    amplitude: float,
    rotation: float,
):

    cx, cy = center

    lengths = _spoke_lengths(spectrum, spoke_count)

    angles = rotation + np.linspace(
        0.0,
        2.0 * math.pi,
        spoke_count,
        endpoint=False,
    )

    inner_radius = base_radius

    outer_radius = (
        base_radius
        + radius_step * (ring_count - 1)
        + lengths * amplitude
    )

    for i in range(spoke_count):

        x0 = cx + inner_radius * math.cos(angles[i])
        y0 = cy + inner_radius * math.sin(angles[i])

        x1 = cx + outer_radius[i] * math.cos(angles[i])
        y1 = cy + outer_radius[i] * math.sin(angles[i])

        yield np.array(
            [[x0, y0], [x1, y1]],
            dtype=np.float32,
        )
