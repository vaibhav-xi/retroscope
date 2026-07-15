/* modules/audioreactive/_native/segments.h */
#ifndef SEGMENTS_H
#define SEGMENTS_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

PyObject *segments_fixed_dashes(PyObject *self, PyObject *args, PyObject *kwds);
PyObject *segments_life_dashes(PyObject *self, PyObject *args, PyObject *kwds);

#endif
