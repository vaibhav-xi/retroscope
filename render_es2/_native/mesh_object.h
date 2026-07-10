#ifndef MESH_OBJECT_H
#define MESH_OBJECT_H

#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "gl_platform.h"

typedef struct
{
    PyObject_HEAD

    GLuint vao;

    GLuint vbo;

    int vertex_count;

} MeshObject;

extern PyTypeObject MeshType;

#endif