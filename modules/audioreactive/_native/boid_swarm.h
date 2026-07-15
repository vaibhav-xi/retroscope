/* modules/audioreactive/_native/boid_swarm.h */
#ifndef BOID_SWARM_H
#define BOID_SWARM_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "rng.h"

typedef struct
{
    PyObject_HEAD

    int capacity;

    float neighbor_radius;

    float *pos_x;
    float *pos_y;
    float *vel_x;
    float *vel_y;

    float *scratch_vx;
    float *scratch_vy;

    RngState rng;

} BoidSwarmObject;

extern PyTypeObject BoidSwarmType;

#endif
