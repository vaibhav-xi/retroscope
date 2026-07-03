"""
RetroScope

Default Oscilloscope Theme

A Theme defines only visual appearance.

Themes NEVER contain rendering logic.

Themes NEVER contain simulation logic.
"""

from dataclasses import dataclass
from typing import Tuple


Color = Tuple[int, int, int]


@dataclass(frozen=True)
class OscilloscopeTheme:
    """
    Default RetroScope green CRT theme.
    """

    #
    # Background
    #

    background: Color = (0, 0, 0)

    #
    # Grid
    #

    grid_major: Color = (0, 55, 18)

    grid_minor: Color = (0, 28, 8)

    grid_center: Color = (0, 80, 25)

    #
    # Trace
    #

    trace_core: Color = (220, 255, 220)

    trace_main: Color = (60, 255, 120)

    trace_glow: Color = (0, 180, 70)

    #
    # Overlay
    #

    text: Color = (0, 255, 120)

    accent: Color = (0, 180, 80)