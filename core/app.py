"""
RetroScope

Application

OpenGL ES 2.0 Version
"""

import glfw

import config

from core.context import Context
from core.frame import Frame
from core.manager import Manager

from render_es2.window import Window
from render_es2.renderer import Renderer


class App:

    def __init__(self):

        #
        # Engine
        #

        self.context = Context()

        self.manager = Manager()

        self.frame = Frame()

        #
        # OpenGL Window
        #

        self.window = Window(
            config.WIDTH,
            config.HEIGHT,
            config.WINDOW_TITLE,
        )

        #
        # Renderer
        #

        self.renderer = Renderer()

    # ---------------------------------------------------------

    def initialize(self):

        from modules.grid.grid import GridModule
        from modules.overlay.overlay import OverlayModule
        from modules.wave.module import WaveModule

        self.manager.register(
            GridModule()
        )

        self.manager.register(
            OverlayModule()
        )

        self.manager.register(
            WaveModule()
        )

        self.manager.initialize(
            self.context
        )

    # ---------------------------------------------------------

    def update(self):

        self.context.update()

        self.manager.update(
            self.context
        )

        self.frame.clear()

        self.manager.emit(
            self.context,
            self.frame,
        )

    # ---------------------------------------------------------

    def draw(self):

        self.renderer.render(
            self.frame
        )

        self.window.swap()

    # ---------------------------------------------------------

    def shutdown(self):

        self.manager.shutdown()

        self.window.shutdown()

    # ---------------------------------------------------------

    def run(self):

        self.initialize()

        while not self.window.should_close():

            self.window.poll()

            #
            # ESC closes window
            #

            if glfw.get_key(
                self.window.handle,
                glfw.KEY_ESCAPE,
            ) == glfw.PRESS:

                break

            #
            # Engine
            #

            self.update()

            #
            # Draw
            #

            self.draw()

        self.shutdown()