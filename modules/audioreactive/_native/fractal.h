#ifndef FRACTAL_H
#define FRACTAL_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *
fractal_lightning_bolt(
    PyObject *self,
    PyObject *args,
    PyObject *kwds
);

PyObject *
fractal_subdivide_triangle(
    PyObject *self,
    PyObject *args,
    PyObject *kwds
);

#endif
