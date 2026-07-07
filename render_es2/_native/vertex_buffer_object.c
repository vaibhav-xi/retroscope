#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "vertex_buffer_object.h"

#include <structmember.h>

static int
VertexBuffer_init(
    VertexBufferObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    self->vertices = NULL;

    self->capacity = 0;

    self->count = 0;

    return 0;
}

static PyObject *
VertexBuffer_clear(
    VertexBufferObject *self,
    PyObject *Py_UNUSED(ignored)
)
{
    self->count = 0;

    Py_RETURN_NONE;
}

int
vertex_buffer_reserve(
    VertexBufferObject *self,
    int capacity
)
{
    if (self->capacity >= capacity)
    {
        return 1;
    }

    float *new_vertices =
        PyMem_Realloc(
            self->vertices,
            sizeof(float) * capacity
        );

    if (new_vertices == NULL)
    {
        PyErr_NoMemory();
        return 0;
    }

    self->vertices = new_vertices;
    self->capacity = capacity;

    return 1;
}

static void
VertexBuffer_dealloc(
    VertexBufferObject *self
)
{
    if (self->vertices)
    {
        PyMem_Free(self->vertices);
    }

    Py_TYPE(self)->tp_free(
        (PyObject *)self
    );
}

static PyObject *
VertexBuffer_reserve(
    VertexBufferObject *self,
    PyObject *args
)
{
    int capacity;

    if (!PyArg_ParseTuple(args, "i", &capacity))
        return NULL;

    if (!vertex_buffer_reserve(self, capacity))
        return NULL;

    Py_RETURN_NONE;
}

float *
vertex_buffer_data(
    VertexBufferObject *self
)
{
    return self->vertices;
}

static PyMemberDef VertexBuffer_members[] =
{
    {
        "count",
        T_INT,
        offsetof(VertexBufferObject, count),
        0,
        NULL
    },

    {
        "capacity",
        T_INT,
        offsetof(VertexBufferObject, capacity),
        READONLY,
        NULL
    },

    {NULL}
};

static PyMethodDef VertexBuffer_methods[] =
{
    {
        "reserve",
        (PyCFunction)VertexBuffer_reserve,
        METH_VARARGS,
        NULL
    },

    {
        "clear",
        (PyCFunction)VertexBuffer_clear,
        METH_NOARGS,
        NULL
    },

    {NULL}
};

PyTypeObject VertexBufferType =
{
    PyVarObject_HEAD_INIT(NULL, 0)

    .tp_name = "_native.VertexBuffer",

    .tp_basicsize =
        sizeof(VertexBufferObject),

    .tp_flags =
        Py_TPFLAGS_DEFAULT,

    .tp_new =
        PyType_GenericNew,

    .tp_init =
        (initproc)VertexBuffer_init,

    .tp_dealloc =
        (destructor)VertexBuffer_dealloc,

    .tp_methods = VertexBuffer_methods,

    .tp_members = VertexBuffer_members,

};

