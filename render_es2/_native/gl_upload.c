#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "gl_platform.h"

#include "vertex_buffer_object.h"

PyObject *
gl_upload(
    PyObject *self,
    PyObject *args
)
{
    unsigned int vbo;

    PyObject *obj;

    if (!PyArg_ParseTuple(
            args,
            "IO",
            &vbo,
            &obj))
    {
        return NULL;
    }

    if (!PyObject_TypeCheck(
            obj,
            &VertexBufferType))
    {
        PyErr_SetString(
            PyExc_TypeError,
            "expected VertexBuffer"
        );

        return NULL;
    }

    VertexBufferObject *vb =
        (VertexBufferObject *)obj;

    glBindBuffer(
        GL_ARRAY_BUFFER,
        vbo
    );

    glBufferData(
        GL_ARRAY_BUFFER,
        vb->count * sizeof(float),
        vb->vertices,
        GL_DYNAMIC_DRAW
    );

    Py_RETURN_NONE;
}