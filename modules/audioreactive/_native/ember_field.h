#ifndef EMBER_FIELD_H
#define EMBER_FIELD_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "rng.h"

typedef struct
{
    PyObject_HEAD

    int capacity;
    float inner_radius;

    float *angle;
    float *radius;
    float *speed;
    float *drift;
    float *age;
    float *lifetime;
    unsigned char *alive;

    int cursor;

    RngState rng;

} EmberFieldObject;

extern PyTypeObject EmberFieldType;

#endif
