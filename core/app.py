"""
RetroScope

App

Temporary OpenGL bootstrap.

Purpose:

Verify GLFW + ModernGL works before
connecting the engine.
"""

from __future__ import annotations

from render.window import Window


class App:

    def __init__(self):

        self.window = Window()

    # ---------------------------------------------------------

    def run(self):

        while not self.window.should_close():

            self.window.poll_events()

            self.window.begin_frame()

            #
            # Nothing rendered yet.
            #

            self.window.end_frame()

        self.window.shutdown()