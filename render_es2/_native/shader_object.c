#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "shader_object.h"

static int
Shader_init(
    ShaderObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    self->program = 0;
    self->color_location = -1;

    return 0;
}

static PyObject *
Shader_use(
    ShaderObject *self,
    PyObject *Py_UNUSED(ignored)
)
{
    glUseProgram(
        self->program
    );

    Py_RETURN_NONE;
}

static PyObject *
Shader_set_color(
    ShaderObject *self,
    PyObject *args
)
{
    float r;
    float g;
    float b;

    if (!PyArg_ParseTuple(
            args,
            "fff",
            &r,
            &g,
            &b))
    {
        return NULL;
    }

    glUniform3f(
        self->color_location,
        r,
        g,
        b
    );

    Py_RETURN_NONE;
}

static GLuint
compile_shader(
    GLenum type,
    const char *source
)
{
    GLuint shader =
        glCreateShader(type);

    glShaderSource(
        shader,
        1,
        &source,
        NULL
    );

    glCompileShader(shader);

    GLint success = GL_FALSE;

    glGetShaderiv(
        shader,
        GL_COMPILE_STATUS,
        &success
    );

    if (!success)
    {
        char log[4096];

        glGetShaderInfoLog(
            shader,
            sizeof(log),
            NULL,
            log
        );

        PyErr_SetString(
            PyExc_RuntimeError,
            log
        );

        glDeleteShader(shader);

        return 0;
    }

    return shader;
}

static PyObject *
Shader_create(
    ShaderObject *self,
    PyObject *args
)
{
    const char *vertex_source;
    const char *fragment_source;

    if (!PyArg_ParseTuple(
            args,
            "ss",
            &vertex_source,
            &fragment_source))
    {
        return NULL;
    }

    GLuint vertex =
        compile_shader(
            GL_VERTEX_SHADER,
            vertex_source
        );

    if (vertex == 0)
    {
        return NULL;
    }

    GLuint fragment =
        compile_shader(
            GL_FRAGMENT_SHADER,
            fragment_source
        );

    if (fragment == 0)
    {
        glDeleteShader(vertex);
        return NULL;
    }

    GLuint program =
        glCreateProgram();

    glAttachShader(
        program,
        vertex
    );

    glAttachShader(
        program,
        fragment
    );

    glLinkProgram(
        program
    );

    GLint success = GL_FALSE;

    glGetProgramiv(
        program,
        GL_LINK_STATUS,
        &success
    );

    if (!success)
    {
        char log[4096];

        glGetProgramInfoLog(
            program,
            sizeof(log),
            NULL,
            log
        );

        glDeleteProgram(program);
        glDeleteShader(vertex);
        glDeleteShader(fragment);

        PyErr_SetString(
            PyExc_RuntimeError,
            log
        );

        return NULL;
    }

    glDeleteShader(vertex);
    glDeleteShader(fragment);

    self->program = program;

    self->color_location =
        glGetUniformLocation(
            program,
            "u_color"
        );

    printf("Shader_create\n");
    fflush(stdout);

    Py_RETURN_NONE;
}

static PyObject *
Shader_test(
    ShaderObject *self,
    PyObject *Py_UNUSED(args)
)
{
    printf("Shader_test\n");
    fflush(stdout);

    Py_RETURN_NONE;
}

static PyMethodDef Shader_methods[] =
{
    {
        "test",
        (PyCFunction)Shader_test,
        METH_NOARGS,
        NULL
    },

    {
        "use",
        (PyCFunction)Shader_use,
        METH_NOARGS,
        NULL
    },

    {
        "set_color",
        (PyCFunction)Shader_set_color,
        METH_VARARGS,
        NULL
    },

    {
        "create",
        (PyCFunction)Shader_create,
        METH_VARARGS,
        NULL
    },
    

    {NULL}
};

PyTypeObject ShaderType =
{
    PyVarObject_HEAD_INIT(NULL, 0)

    .tp_name = "_native.Shader",

    .tp_basicsize =
        sizeof(ShaderObject),

    .tp_flags =
        Py_TPFLAGS_DEFAULT,

    .tp_new =
        PyType_GenericNew,

    .tp_init =
        (initproc)Shader_init,

    .tp_methods =
        Shader_methods,
};