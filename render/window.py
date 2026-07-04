"""
RetroScope

Window

Creates the GLFW window and the ModernGL context.

Owns:

- GLFW initialization
- Window creation
- OpenGL context
- Swap buffers
- Timing

Knows nothing about rendering.
"""

from __future__ import annotations

import glfw
import moderngl
import time
import platform
import config


class Window:

    def __init__(self):

        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        system = platform.system()

        if system == "Darwin":

            #
            # macOS
            #

            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

            glfw.window_hint(
                glfw.OPENGL_PROFILE,
                glfw.OPENGL_CORE_PROFILE,
            )

            glfw.window_hint(
                glfw.OPENGL_FORWARD_COMPAT,
                glfw.TRUE,
            )

        else:

            #
            # Raspberry Pi / Linux
            #

            glfw.window_hint(
                glfw.CLIENT_API,
                glfw.OPENGL_ES_API,
            )

            glfw.window_hint(
                glfw.CONTEXT_VERSION_MAJOR,
                3,
            )

            glfw.window_hint(
                glfw.CONTEXT_VERSION_MINOR,
                0,
            )

        self.window = glfw.create_window(
            config.WIDTH,
            config.HEIGHT,
            config.WINDOW_TITLE,
            None,
            None,
        )

        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create window")

        glfw.make_context_current(self.window)

        #
        # Enable VSync
        #

        glfw.swap_interval(1)

        #
        # Create ModernGL context
        #

        self.ctx = moderngl.create_context()
        
        print("Vendor :", self.ctx.info["GL_VENDOR"])
        print("Renderer:", self.ctx.info["GL_RENDERER"])
        print("Version :", self.ctx.info["GL_VERSION"])

        self.last_time = time.perf_counter()

    # ---------------------------------------------------------

    def should_close(self):

        return glfw.window_should_close(self.window)

    # ---------------------------------------------------------

    def poll_events(self):

        glfw.poll_events()

    # ---------------------------------------------------------

    def begin_frame(self):

        self.ctx.clear(
            0.0,
            0.0,
            0.0,
            1.0,
        )

    # ---------------------------------------------------------

    def end_frame(self):

        glfw.swap_buffers(self.window)

    # ---------------------------------------------------------

    def shutdown(self):

        glfw.destroy_window(self.window)
        glfw.terminate()