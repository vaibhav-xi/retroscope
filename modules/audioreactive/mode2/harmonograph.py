"""
RetroScope

Audio Reactive Mode 2 - Harmonograph

A classic harmonograph / Lissajous curve, but its harmonic
amplitudes (and, gently, their ratios) are driven directly by
the music instead of being fixed constants:

    bass  -> amplitude of the slow, wide harmonic
    mid   -> amplitude + ratio of the middle harmonic
    high  -> amplitude + ratio of the fast, tight harmonic that
              adds jittery detail

Pure geometry.
No renderer.
No OpenGL.
"""

from __future__ import annotations

import numpy as np


def harmonograph_curve(
    bass: float,
    mid: float,
    high: float,
    phase: float,
    point_count: int,
    base_radius: float,
) -> np.ndarray:

    t = np.linspace(
        0.0,
        2.0 * np.pi,
        point_count,
        endpoint=False,
    )

    ratio_a = 1.0
    ratio_b = 2.0 + mid * 0.5
    ratio_c = 3.0 + high * 1.5

    amp_a = base_radius * (0.35 + bass * 0.65)
    amp_b = base_radius * (0.20 + mid * 0.55)
    amp_c = base_radius * (0.10 + high * 0.45)

    x = (
        amp_a * np.sin(ratio_a * t + phase)
        + amp_b * np.sin(ratio_b * t + phase * 1.7)
        + amp_c * np.sin(ratio_c * t + phase * 2.3)
    )

    y = (
        amp_a * np.cos(ratio_a * t + phase * 0.9)
        + amp_b * np.cos(ratio_b * t + phase * 1.3)
        + amp_c * np.cos(ratio_c * t + phase * 2.9)
    )

    points = np.column_stack([x, y]).astype(np.float32)

    #
    # Close the loop back to the first point.
    #

    points = np.vstack([points, points[0]])

    return points