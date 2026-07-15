#ifndef RING_FIELD_H
#define RING_FIELD_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "rng.h"

typedef struct
{
    PyObject_HEAD

    int capacity;

    float *radius;
    float *speed;
    float *strength;
    float *wobble;
    float *rotation;
    float *spin;
    float *age;
    float *lifetime;
    unsigned char *alive;

    int cursor;

    RngState rng;

} RingFieldObject;

extern PyTypeObject RingFieldType;

#endif
