from __future__ import annotations

import numpy as np


def spectrum_ring(
    magnitudes: np.ndarray,
    base_radius: float,
    amplitude: float,
    rotation: float = 0.0,
    mirror: bool = True,
) -> np.ndarray:

    values = magnitudes

    if mirror:
        values = np.concatenate([values, values[::-1]])

    count = len(values)

    angles = rotation + (np.arange(count) / count) * (2.0 * np.pi)

    radius = base_radius + values * amplitude

    x = radius * np.cos(angles)
    y = radius * np.sin(angles)

    points = np.column_stack([x, y]).astype(np.float32)

    points = np.vstack([points, points[0]])

    return points