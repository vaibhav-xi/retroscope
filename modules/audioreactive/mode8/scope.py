from __future__ import annotations

import numpy as np


def downsample(samples, target_points: int):

    n = len(samples)

    if n <= target_points:

        return samples

    indices = np.linspace(0, n - 1, target_points).astype(np.int64)

    return samples[indices]


def graticule_lines(rect, cols: int = 10, rows: int = 8):

    x0, y0, x1, y1 = rect

    for col in range(cols + 1):

        x = x0 + (x1 - x0) * (col / cols)

        is_center = col == cols // 2

        yield (
            np.array([[x, y0], [x, y1]], dtype=np.float32),
            is_center,
        )

    for row in range(rows + 1):

        y = y0 + (y1 - y0) * (row / rows)

        is_center = row == rows // 2

        yield (
            np.array([[x0, y], [x1, y]], dtype=np.float32),
            is_center,
        )


def minor_ticks(rect, cols: int, rows: int, tick_size: float = 3.0):

    x0, y0, x1, y1 = rect

    for col in range(cols):

        x = x0 + (x1 - x0) * ((col + 0.5) / cols)

        yield np.array([[x, y0], [x, y0 + tick_size]], dtype=np.float32)
        yield np.array([[x, y1 - tick_size], [x, y1]], dtype=np.float32)

    for row in range(rows):

        y = y0 + (y1 - y0) * ((row + 0.5) / rows)

        yield np.array([[x0, y], [x0 + tick_size, y]], dtype=np.float32)
        yield np.array([[x1 - tick_size, y], [x1, y]], dtype=np.float32)


def waveform_trace(samples, rect, gain: float = 1.0):

    x0, y0, x1, y1 = rect

    n = len(samples)

    if n < 2:

        return np.zeros((0, 2), dtype=np.float32)

    cy = (y0 + y1) * 0.5
    half_height = (y1 - y0) * 0.5

    x = np.linspace(x0, x1, n)

    y = cy - np.clip(samples * gain, -1.0, 1.0) * half_height

    return np.column_stack([x, y]).astype(np.float32)
