#ifndef BURST_FIELD_H
#define BURST_FIELD_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "rng.h"

typedef struct
{
    PyObject_HEAD

    int capacity;
    float drag;

    float *origin_x;
    float *origin_y;
    float *angle;
    float *angular_velocity;
    float *distance;
    float *speed;
    float *age;
    float *lifetime;
    unsigned char *alive;

    int cursor;

    RngState rng;

} BurstFieldObject;

extern PyTypeObject BurstFieldType;

#endif
