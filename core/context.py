"""
RetroScope

Engine Context

Shared runtime state for the engine.
"""

from dataclasses import dataclass, field
import random as pyrandom
import time

from themes.oscilloscope import OscilloscopeTheme

from core.signal import SignalRegistry
from core.parameters import ParameterRegistry
from core.settings import Settings


@dataclass
class Context:
    """
    Shared engine runtime state.
    """

    # ---------------------------------------------------------
    # Engine
    # ---------------------------------------------------------

    running: bool = True
    paused: bool = False

    # ---------------------------------------------------------
    # Timing
    # ---------------------------------------------------------

    frame: int = 0
    delta_time: float = 0.0
    elapsed_time: float = 0.0
    fps: float = 0.0
    
    # ---------------------------------------------------------
    # Display
    # ---------------------------------------------------------

    width: int = 0
    height: int = 0

    # ---------------------------------------------------------
    # Theme
    # ---------------------------------------------------------

    theme: OscilloscopeTheme = field(
        default_factory=OscilloscopeTheme
    )

    # ---------------------------------------------------------
    # Engine Services
    # ---------------------------------------------------------

    signals: SignalRegistry = field(
        default_factory=SignalRegistry
    )

    parameters: ParameterRegistry = field(
        default_factory=ParameterRegistry
    )

    # ---------------------------------------------------------
    # Random Generator
    # ---------------------------------------------------------

    random: pyrandom.Random = field(
        default_factory=pyrandom.Random
    )

    # ---------------------------------------------------------
    # Internal
    # ---------------------------------------------------------

    _last_time: float = field(
        default_factory=time.perf_counter,
        init=False,
        repr=False,
    )

    # ---------------------------------------------------------
    # Post Initialization
    # ---------------------------------------------------------

    def __post_init__(self):

        #
        # Typed settings interface.
        #

        self.settings = Settings(
            self.parameters
        )

    # ---------------------------------------------------------

    def update(self):

        now = time.perf_counter()

        self.delta_time = now - self._last_time

        self.elapsed_time += self.delta_time

        self.frame += 1

        self._last_time = now

    # ---------------------------------------------------------

    def set_fps(
        self,
        fps: float,
    ):

        self.fps = fps
        
    @property
    def center(self):

        return (
            self.width * 0.5,
            self.height * 0.5,
        )

    @property
    def aspect_ratio(self):

        if self.height == 0:
            return 1.0

        return self.width / self.height