#ifndef CHAOS_FIELD_H
#define CHAOS_FIELD_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "rng.h"

typedef struct
{
    PyObject_HEAD

    int capacity;

    float *x;
    float *y;

    float a, b, c, d;
    float kick;

    RngState rng;

} ChaosFieldObject;

extern PyTypeObject ChaosFieldType;

#endif
