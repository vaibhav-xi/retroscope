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

import time

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

        self.context.width = config.WIDTH
        self.context.height = config.HEIGHT

        #
        # Renderer
        #

        self.renderer = Renderer()

        #
        # Shared profiler. The renderer already owns one (used for
        # GeometryBuilder / StrokeBuilder / RenderGraph); reuse it
        # here so Poll / Update / Emit / Swap show up in the same
        # per-second report instead of being invisible.
        #

        self.profiler = self.renderer.profiler

    # ---------------------------------------------------------

    def initialize(self):

        from modules.grid.grid import GridModule
        from modules.overlay.overlay import OverlayModule
        from modules.wave.module import WaveModule

        from modules.blackhole.module import BlackHole
        from modules.audioreactive.mode1.module import AudioReactiveMode1
        from modules.audioreactive.mode2.module import AudioReactiveMode2
        from modules.audioreactive.mode3.module import AudioReactiveMode3
        from modules.audioreactive.mode4.module import AudioReactiveMode4
        from modules.audioreactive.mode5.module import AudioReactiveMode5
        from modules.audioreactive.mode6.module import AudioReactiveMode6
        from modules.audioreactive.mode7.module import AudioReactiveMode7
        from modules.audioreactive.mode8.module import AudioReactiveMode8
        from modules.audioreactive.mode9.module import AudioReactiveMode9
        from modules.audioreactive.mode10.module import AudioReactiveMode10
        from modules.audioreactive.mode11.module import AudioReactiveMode11

        # self.manager.register(
        #     GridModule()
        # )

        # self.manager.register(
        #     OverlayModule()
        # )

        # self.manager.register(
        #     WaveModule()
        # )

        # self.manager.register(
        #     BlackHole()
        # )

        # self.manager.register(
        #     AudioReactiveMode1()
        # )

        # self.manager.register(
        #     AudioReactiveMode2()
        # )

        # self.manager.register(
        #     AudioReactiveMode3()
        # )

        # self.manager.register(
        #     AudioReactiveMode4()
        # )

        # self.manager.register(
        #     AudioReactiveMode5()
        # )

        # self.manager.register(
        #     AudioReactiveMode6()
        # )

        # self.manager.register(
        #     AudioReactiveMode7()
        # )

        # self.manager.register(
        #     AudioReactiveMode8()
        # )

        # self.manager.register(
        #     AudioReactiveMode9()
        # )

        # self.manager.register(
        #     AudioReactiveMode10()
        # )
        
        self.manager.register(
            AudioReactiveMode11()
        )

        self.manager.initialize(
            self.context
        )

    # ---------------------------------------------------------

    def update(self):

        self.context.update()

        self.profiler.begin("Update")

        self.manager.update(
            self.context
        )

        self.profiler.end("Update")

        self.frame.clear()

        self.profiler.begin("Emit")

        self.manager.emit(
            self.context,
            self.frame,
        )

        self.profiler.end("Emit")

    # ---------------------------------------------------------

    def draw(self):

        self.renderer.render(
            self.frame
        )

        self.profiler.begin("Swap")

        self.window.swap()

        self.profiler.end("Swap")

    # ---------------------------------------------------------

    def shutdown(self):

        self.manager.shutdown()

        self.window.shutdown()

    # ---------------------------------------------------------

    def run(self):

        self.initialize()

        frame_counter = 0
        total_time = 0.0

        while not self.window.should_close():

            start = time.perf_counter()

            #
            # Reset the profiler for this frame. report() only
            # prints once a second, but always reflects the most
            # recent frame's breakdown.
            #

            self.profiler.samples.clear()

            self.profiler.begin("Poll")

            self.window.poll()

            self.profiler.end("Poll")

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

            self.profiler.report()

            end = time.perf_counter()

            total_time += end - start
            frame_counter += 1

            if frame_counter == 120:

                average = total_time / frame_counter

                fps = 1.0 / average

                print(
                    f"{average * 1000:.2f} ms   "
                    f"{fps:.1f} FPS"
                )

                frame_counter = 0
                total_time = 0.0

        self.shutdown()
