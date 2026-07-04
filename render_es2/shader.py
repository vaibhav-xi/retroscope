from OpenGL.GL import *
import platform


class Shader:

    def __init__(self, vertex_src, fragment_src):

        if platform.system() == "Darwin":

            vertex_src = self._desktop_vertex(vertex_src)
            fragment_src = self._desktop_fragment(fragment_src)

        self.program = glCreateProgram()

        vs = self._compile(
            GL_VERTEX_SHADER,
            vertex_src,
        )

        fs = self._compile(
            GL_FRAGMENT_SHADER,
            fragment_src,
        )

        glAttachShader(self.program, vs)
        glAttachShader(self.program, fs)

        glBindAttribLocation(
            self.program,
            0,
            "a_position",
        )

        glBindAttribLocation(
            self.program,
            1,
            "a_color",
        )

        glLinkProgram(self.program)
        
        print(
            "position:",
            glGetAttribLocation(
                self.program,
                "a_position",
            ),
        )

        print(
            "color:",
            glGetAttribLocation(
                self.program,
                "a_color",
            ),
        )

        if glGetProgramiv(
            self.program,
            GL_LINK_STATUS,
        ) != GL_TRUE:

            raise RuntimeError(
                glGetProgramInfoLog(
                    self.program
                ).decode()
            )

    # -------------------------------------------------

    def use(self):

        glUseProgram(self.program)

    # -------------------------------------------------

    def _compile(self, shader_type, source):

        shader = glCreateShader(shader_type)

        glShaderSource(shader, source)

        glCompileShader(shader)

        if glGetShaderiv(
            shader,
            GL_COMPILE_STATUS,
        ) != GL_TRUE:

            raise RuntimeError(
                glGetShaderInfoLog(shader).decode()
            )

        return shader

    # -------------------------------------------------

    def _desktop_vertex(self, src):

        return (
            "#version 410 core\n"
            "layout(location=0) in vec2 a_position;\n"
            "layout(location=1) in vec3 a_color;\n"
            "out vec3 v_color;\n"
            "void main(){"
            "v_color=a_color;"
            "gl_Position=vec4(a_position,0.0,1.0);"
            "}"
        )

    # -------------------------------------------------

    def _desktop_fragment(self, src):

        return (
            "#version 410 core\n"
            "in vec3 v_color;"
            "out vec4 FragColor;"
            "void main(){"
            "FragColor=vec4(v_color,1.0);"
            "}"
        )