#ifndef VERTEX_BUFFER_OBJECT_H
#define VERTEX_BUFFER_OBJECT_H

#define PY_SSIZE_T_CLEAN

#include <Python.h>

typedef struct
{
    PyObject_HEAD

    float *vertices;

    int capacity;

    int count;

} VertexBufferObject;

int
vertex_buffer_reserve(
    VertexBufferObject *self,
    int capacity
);

float *
vertex_buffer_data(
    VertexBufferObject *self
);

extern PyTypeObject VertexBufferType;

#endif