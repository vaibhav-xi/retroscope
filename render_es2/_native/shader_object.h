#ifndef SHADER_OBJECT_H
#define SHADER_OBJECT_H

#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "gl_platform.h"

typedef struct
{
    PyObject_HEAD

    GLuint program;

    GLint color_location;

    GLint alpha_location;

    GLint size_location;

    GLint intensity_location;

} ShaderObject;

extern PyTypeObject ShaderType;

#endif
