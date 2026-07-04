from OpenGL.GL import *


class Shader:

    def __init__(self, vertex_src, fragment_src):

        self.program = glCreateProgram()

        vs = self._compile(GL_VERTEX_SHADER, vertex_src)
        fs = self._compile(GL_FRAGMENT_SHADER, fragment_src)

        glAttachShader(self.program, vs)
        glAttachShader(self.program, fs)

        glLinkProgram(self.program)

        if glGetProgramiv(self.program, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(glGetProgramInfoLog(self.program).decode())

    def use(self):
        glUseProgram(self.program)

    def _compile(self, shader_type, source):

        shader = glCreateShader(shader_type)

        glShaderSource(shader, source)
        glCompileShader(shader)

        if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(shader).decode())

        return shader