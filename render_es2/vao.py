from OpenGL.GL import *
import platform


class VAO:

    def __init__(self):

        self.enabled = platform.system() == "Darwin"

        if self.enabled:

            self.id = glGenVertexArrays(1)

        else:

            self.id = None

    def bind(self):

        if self.enabled:

            glBindVertexArray(self.id)