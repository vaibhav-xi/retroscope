"""
RetroScope

Application

Owns the entire engine lifecycle.

The App coordinates:

    Context
    Module Manager
    Frame

The App NEVER contains simulation logic.

The App NEVER performs rendering.

Rendering begins in Phase 1.
"""

from time import sleep

import config

from core.context import Context
from core.frame import Frame
from core.manager import Manager


class App:
    """
    RetroScope Engine
    """

    def __init__(self):

        #
        # Shared engine state
        #

        self.context = Context()

        #
        # Module manager
        #

        self.manager = Manager()

        #
        # Current render frame
        #

        self.frame = Frame()

    # ---------------------------------------------------------

    def initialize(self) -> None:
        """
        Initialize the engine.
        """

        self.manager.initialize(self.context)

    # ---------------------------------------------------------

    def update(self) -> None:
        """
        Update one engine tick.
        """

        #
        # Update timing
        #

        self.context.update()

        #
        # Update modules
        #

        self.manager.update(self.context)

        #
        # Build next frame
        #

        self.frame.clear()

        self.manager.emit(self.frame)

    # ---------------------------------------------------------

    def shutdown(self) -> None:
        """
        Shutdown the engine.
        """

        self.manager.shutdown()

    # ---------------------------------------------------------

    def run(self) -> None:
        """
        Main engine loop.
        """

        print()

        print("=====================================")
        print(" RetroScope Engine")
        print("=====================================")

        self.initialize()

        print("Engine initialized.")
        print("Running...")
        print()

        try:

            #
            # Phase 0
            #
            # No renderer exists yet.
            # No window exists yet.
            #
            # We simply prove the engine loop.
            #

            while self.context.running:

                self.update()

                #
                # Temporary frame limiter.
                #
                # Replaced with pygame.Clock()
                # in Phase 1.
                #

                sleep(1 / config.FPS)

                #
                # Display FPS estimate
                #

                if self.context.delta_time > 0:

                    fps = 1.0 / self.context.delta_time

                    self.context.set_fps(fps)

        except KeyboardInterrupt:

            print()
            print("Stopping engine...")

        finally:

            self.shutdown()

            print("Shutdown complete.")