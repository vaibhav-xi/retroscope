"""
RetroScope

OpenGL ES 2.0 Window

Owns:

- GLFW
- OpenGL Context
- Swap Buffers
- Event Polling

Knows nothing about rendering.
"""

from __future__ import annotations

import platform

import glfw
from OpenGL import GL


class Window:

    def __init__(self, width, height, title):

        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        #
        # macOS
        #
        # Desktop OpenGL 4.1
        #

        if platform.system() == "Darwin":

            glfw.window_hint(
                glfw.CONTEXT_VERSION_MAJOR,
                4,
            )

            glfw.window_hint(
                glfw.CONTEXT_VERSION_MINOR,
                1,
            )

            glfw.window_hint(
                glfw.OPENGL_PROFILE,
                glfw.OPENGL_CORE_PROFILE,
            )

            glfw.window_hint(
                glfw.OPENGL_FORWARD_COMPAT,
                glfw.TRUE,
            )

        #
        # Raspberry Pi
        #
        # OpenGL ES 2.0
        #

        else:

            glfw.window_hint(
                glfw.CLIENT_API,
                glfw.OPENGL_ES_API,
            )

            glfw.window_hint(
                glfw.CONTEXT_VERSION_MAJOR,
                2,
            )

            glfw.window_hint(
                glfw.CONTEXT_VERSION_MINOR,
                0,
            )

        self.handle = glfw.create_window(
            width,
            height,
            title,
            None,
            None,
        )

        if self.handle is None:

            glfw.terminate()

            raise RuntimeError(
                "Unable to create window."
            )

        glfw.make_context_current(self.handle)

        glfw.swap_interval(1)

        #
        # Print OpenGL information
        #

        print(
            "Vendor  :",
            GL.glGetString(GL.GL_VENDOR).decode(),
        )

        print(
            "Renderer:",
            GL.glGetString(GL.GL_RENDERER).decode(),
        )

        print(
            "Version :",
            GL.glGetString(GL.GL_VERSION).decode(),
        )

        print(
            "Viewport:",
            GL.glGetIntegerv(GL.GL_VIEWPORT),
        )

    # ---------------------------------------------------------

    def should_close(self):

        return glfw.window_should_close(
            self.handle
        )

    # ---------------------------------------------------------

    def poll(self):

        glfw.poll_events()

    # ---------------------------------------------------------

    def swap(self):

        glfw.swap_buffers(
            self.handle
        )

    # ---------------------------------------------------------

    def shutdown(self):

        glfw.destroy_window(
            self.handle
        )

        glfw.terminate()