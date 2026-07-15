#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>

#include <structmember.h>
#include <math.h>
#include <time.h>

#include "burst_field.h"

static int
BurstField_init(
    BurstFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    int capacity;
    double drag = 0.0;
    unsigned long seed = 0;

    static char *keywords[] = { "capacity", "drag", "seed", NULL };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "i|dk", keywords, &capacity, &drag, &seed))
    {
        return -1;
    }

    if (capacity <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "capacity must be positive");
        return -1;
    }

    self->capacity = capacity;
    self->drag = (float)drag;

    self->origin_x = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->origin_y = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->angle = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->angular_velocity = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->distance = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->speed = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->age = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->lifetime = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->alive = (unsigned char *)PyMem_Calloc(capacity, sizeof(unsigned char));

    if (
        !self->origin_x || !self->origin_y || !self->angle ||
        !self->angular_velocity || !self->distance || !self->speed ||
        !self->age || !self->lifetime || !self->alive
    )
    {
        PyErr_NoMemory();
        return -1;
    }

    self->cursor = 0;

    if (seed == 0)
    {
        seed = (unsigned long)time(NULL);
    }

    rng_seed(&self->rng, (uint32_t)seed);

    return 0;
}

/* --------------------------------------------------------- */

static PyObject *
BurstField_spawn(
    BurstFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    int count;
    double origin_x, origin_y;
    double angle_min, angle_max;
    double speed_min, speed_max;
    double lifetime_min, lifetime_max;
    double angular_velocity_min = 0.0, angular_velocity_max = 0.0;
    double distance_start = 0.0;

    static char *keywords[] = {
        "count",
        "origin_x",
        "origin_y",
        "angle_min",
        "angle_max",
        "speed_min",
        "speed_max",
        "lifetime_min",
        "lifetime_max",
        "angular_velocity_min",
        "angular_velocity_max",
        "distance_start",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args,
            kwds,
            "idddddddd|ddd",
            keywords,
            &count,
            &origin_x,
            &origin_y,
            &angle_min,
            &angle_max,
            &speed_min,
            &speed_max,
            &lifetime_min,
            &lifetime_max,
            &angular_velocity_min,
            &angular_velocity_max,
            &distance_start))
    {
        return NULL;
    }

    for (int n = 0; n < count; n++)
    {
        int i = self->cursor;

        self->cursor = (self->cursor + 1) % self->capacity;

        self->origin_x[i] = (float)origin_x;
        self->origin_y[i] = (float)origin_y;

        self->angle[i] = rng_uniform(&self->rng, (float)angle_min, (float)angle_max);

        self->angular_velocity[i] = rng_uniform(
            &self->rng, (float)angular_velocity_min, (float)angular_velocity_max
        );

        self->distance[i] = (float)distance_start;

        self->speed[i] = rng_uniform(&self->rng, (float)speed_min, (float)speed_max);

        self->age[i] = 0.0f;

        self->lifetime[i] = rng_uniform(
            &self->rng, (float)lifetime_min, (float)lifetime_max
        );

        self->alive[i] = 1;
    }

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
BurstField_update(
    BurstFieldObject *self,
    PyObject *args
)
{
    double dt;

    if (!PyArg_ParseTuple(args, "d", &dt))
    {
        return NULL;
    }

    float fdt = (float)dt;

    int has_drag = self->drag > 0.0f;

    float drag_factor = has_drag ? expf(-self->drag * fdt) : 1.0f;

    for (int i = 0; i < self->capacity; i++)
    {
        if (!self->alive[i])
        {
            continue;
        }

        self->age[i] += fdt;

        if (self->age[i] >= self->lifetime[i])
        {
            self->alive[i] = 0;
            continue;
        }

        if (has_drag)
        {
            self->speed[i] *= drag_factor;
        }

        self->angle[i] += self->angular_velocity[i] * fdt;
        self->distance[i] += self->speed[i] * fdt;
    }

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
BurstField_points(
    BurstFieldObject *self,
    PyObject *Py_UNUSED(ignored)
)
{
    int alive_count = 0;

    for (int i = 0; i < self->capacity; i++)
    {
        if (self->alive[i])
        {
            alive_count++;
        }
    }

    npy_intp position_dims[2] = { alive_count, 2 };
    npy_intp scalar_dims[1] = { alive_count };

    PyArrayObject *positions =
        (PyArrayObject *)PyArray_SimpleNew(2, position_dims, NPY_FLOAT32);

    PyArrayObject *life =
        (PyArrayObject *)PyArray_SimpleNew(1, scalar_dims, NPY_FLOAT32);

    PyArrayObject *angle_out =
        (PyArrayObject *)PyArray_SimpleNew(1, scalar_dims, NPY_FLOAT32);

    PyArrayObject *speed_out =
        (PyArrayObject *)PyArray_SimpleNew(1, scalar_dims, NPY_FLOAT32);

    if (positions == NULL || life == NULL || angle_out == NULL || speed_out == NULL)
    {
        Py_XDECREF(positions);
        Py_XDECREF(life);
        Py_XDECREF(angle_out);
        Py_XDECREF(speed_out);
        return NULL;
    }

    float *position_data = (float *)PyArray_DATA(positions);
    float *life_data = (float *)PyArray_DATA(life);
    float *angle_data = (float *)PyArray_DATA(angle_out);
    float *speed_data = (float *)PyArray_DATA(speed_out);

    int out = 0;

    for (int i = 0; i < self->capacity; i++)
    {
        if (!self->alive[i])
        {
            continue;
        }

        float x = self->origin_x[i] + self->distance[i] * cosf(self->angle[i]);
        float y = self->origin_y[i] + self->distance[i] * sinf(self->angle[i]);

        position_data[out * 2 + 0] = x;
        position_data[out * 2 + 1] = y;

        float lifetime = self->lifetime[i] > 1e-6f ? self->lifetime[i] : 1e-6f;

        life_data[out] = 1.0f - (self->age[i] / lifetime);
        angle_data[out] = self->angle[i];
        speed_data[out] = self->speed[i];

        out++;
    }

    PyObject *result = PyTuple_Pack(
        4,
        (PyObject *)positions,
        (PyObject *)life,
        (PyObject *)angle_out,
        (PyObject *)speed_out
    );

    Py_DECREF(positions);
    Py_DECREF(life);
    Py_DECREF(angle_out);
    Py_DECREF(speed_out);

    return result;
}

/* --------------------------------------------------------- */

static void
BurstField_dealloc(
    BurstFieldObject *self
)
{
    PyMem_Free(self->origin_x);
    PyMem_Free(self->origin_y);
    PyMem_Free(self->angle);
    PyMem_Free(self->angular_velocity);
    PyMem_Free(self->distance);
    PyMem_Free(self->speed);
    PyMem_Free(self->age);
    PyMem_Free(self->lifetime);
    PyMem_Free(self->alive);

    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* --------------------------------------------------------- */

static PyMemberDef BurstField_members[] =
{
    { "capacity", T_INT, offsetof(BurstFieldObject, capacity), READONLY, NULL },
    { "drag", T_FLOAT, offsetof(BurstFieldObject, drag), READONLY, NULL },
    { NULL }
};

static PyMethodDef BurstField_methods[] =
{
    {
        "spawn",
        (PyCFunction)BurstField_spawn,
        METH_VARARGS | METH_KEYWORDS,
        "Spawn `count` particles from (origin_x, origin_y)."
    },
    {
        "update",
        (PyCFunction)BurstField_update,
        METH_VARARGS,
        "Advance the simulation by `dt` seconds."
    },
    {
        "points",
        (PyCFunction)BurstField_points,
        METH_NOARGS,
        "Returns (positions, life, angle, speed) for every alive particle."
    },
    { NULL, NULL, 0, NULL }
};

PyTypeObject BurstFieldType =
{
    PyVarObject_HEAD_INIT(NULL, 0)

    .tp_name = "_native.BurstField",
    .tp_basicsize = sizeof(BurstFieldObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)BurstField_init,
    .tp_dealloc = (destructor)BurstField_dealloc,
    .tp_methods = BurstField_methods,
    .tp_members = BurstField_members,
};
