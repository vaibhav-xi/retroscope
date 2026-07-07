#ifndef VERTEX_BUFFER_H
#define VERTEX_BUFFER_H

#include <Python.h>

float *
vertex_buffer_begin(
    PyObject *vertex_buffer,
    int additional,
    int *old_count
);

int
vertex_buffer_finish(
    PyObject *vertex_buffer,
    int new_count
);

#endif