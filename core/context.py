"""
RetroScope

Engine Context

The Context object contains the shared runtime state of the
RetroScope engine.

Every subsystem receives the same Context instance.

The Context NEVER imports pygame.

The Context NEVER contains rendering code.

Subsystems may extend the Context during initialization
(e.g. Audio, Web UI, Input), but every extension should be
its own object.
"""

from dataclasses import dataclass, field
import random as pyrandom
import time


# ==========================================================
# Context
# ==========================================================

@dataclass
class Context:
    """
    Shared engine runtime state.
    """

    #
    # Engine state
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
    # Theme
    #

    theme: str = "oscilloscope"

    #
    # Shared services
    #

    random: pyrandom.Random = field(
        default_factory=pyrandom.Random
    )

    #
    # Internal timer
    #

    _last_time: float = field(
        default_factory=time.perf_counter,
        init=False,
        repr=False,
    )

    # -----------------------------------------------------

    def update(self) -> None:
        """
        Update engine timing.
        Called once every frame.
        """

        now = time.perf_counter()

        self.delta_time = now - self._last_time

        self.elapsed_time += self.delta_time

        self.frame += 1

        self._last_time = now

    # -----------------------------------------------------

    def set_fps(self, fps: float) -> None:
        """
        Updated by the engine once per frame.
        """

        self.fps = fps