#ifndef RADIAL_RING_H
#define RADIAL_RING_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *
radial_ring_build(
    PyObject *self,
    PyObject *args,
    PyObject *kwds
);

#endif
