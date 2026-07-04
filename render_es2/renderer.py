"""
RetroScope

ES2 Renderer

Owns OpenGL state.
"""

from OpenGL.GL import *


class Renderer:

    def __init__(self):

        #
        # Viewport
        #

        viewport = glGetIntegerv(GL_VIEWPORT)

        glViewport(
            0,
            0,
            viewport[2],
            viewport[3],
        )

        #
        # Black background
        #

        glClearColor(
            0.0,
            0.0,
            0.0,
            1.0,
        )

    # -------------------------------------------------

    def begin_frame(self):

        glClear(
            GL_COLOR_BUFFER_BIT
        )

    # -------------------------------------------------

    def end_frame(self):

        pass