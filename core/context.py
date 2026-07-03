"""
RetroScope

Engine Context

Shared runtime state for the engine.
"""

from dataclasses import dataclass, field
import random as pyrandom
import time

from themes.oscilloscope import OscilloscopeTheme


@dataclass
class Context:
    """
    Shared engine runtime state.
    """

    #
    # Engine
    #

    running: bool = True
    paused: bool = False

    #
    # Timing
    #

    frame: int = 0
    delta_time: float = 0.0
    elapsed_time: float = 0.0
    fps: float = 0.0

    #
    # Active Theme
    #

    theme: OscilloscopeTheme = field(
        default_factory=OscilloscopeTheme
    )

    #
    # Random Generator
    #

    random: pyrandom.Random = field(
        default_factory=pyrandom.Random
    )

    #
    # Internal Timer
    #

    _last_time: float = field(
        default_factory=time.perf_counter,
        init=False,
        repr=False,
    )

    # ---------------------------------------------------------

    def update(self) -> None:

        now = time.perf_counter()

        self.delta_time = now - self._last_time

        self.elapsed_time += self.delta_time

        self.frame += 1

        self._last_time = now

    # ---------------------------------------------------------

    def set_fps(self, fps: float) -> None:

        self.fps = fps