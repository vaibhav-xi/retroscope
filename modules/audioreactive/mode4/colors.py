
from __future__ import annotations

import colorsys


def hsv(hue: float, saturation: float, value: float):
    """
    hue in 0..1 (wraps automatically), saturation/value in 0..1.
    """

    hue = hue % 1.0

    return colorsys.hsv_to_rgb(hue, saturation, value)
