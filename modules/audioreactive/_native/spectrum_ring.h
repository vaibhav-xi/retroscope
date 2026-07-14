#ifndef SPECTRUM_RING_H
#define SPECTRUM_RING_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *
spectrum_ring_build(
    PyObject *self,
    PyObject *args,
    PyObject *kwds
);

#endif
