#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>

#include <structmember.h>
#include <math.h>
#include <time.h>

#include "ember_field.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static int
EmberField_init(
    EmberFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    int capacity;
    double inner_radius;
    unsigned long seed = 0;

    static char *keywords[] = {
        "capacity",
        "inner_radius",
        "seed",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args,
            kwds,
            "id|k",
            keywords,
            &capacity,
            &inner_radius,
            &seed))
    {
        return -1;
    }

    if (capacity <= 0)
    {
        PyErr_SetString(
            PyExc_ValueError,
            "capacity must be positive"
        );

        return -1;
    }

    self->capacity = capacity;
    self->inner_radius = (float)inner_radius;

    self->angle = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->radius = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->speed = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->drift = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->age = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->lifetime = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->alive = (unsigned char *)PyMem_Calloc(capacity, sizeof(unsigned char));

    if (
        !self->angle || !self->radius || !self->speed ||
        !self->drift || !self->age || !self->lifetime || !self->alive
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
EmberField_spawn(
    EmberFieldObject *self,
    PyObject *args
)
{
    int count;

    if (!PyArg_ParseTuple(args, "i", &count))
    {
        return NULL;
    }

    for (int n = 0; n < count; n++)
    {
        int i = self->cursor;

        self->cursor = (self->cursor + 1) % self->capacity;

        self->angle[i] = rng_uniform(&self->rng, 0.0f, (float)(2.0 * M_PI));
        self->radius[i] = self->inner_radius;
        self->speed[i] = rng_uniform(&self->rng, 40.0f, 140.0f);
        self->drift[i] = rng_uniform(&self->rng, -0.6f, 0.6f);
        self->age[i] = 0.0f;
        self->lifetime[i] = rng_uniform(&self->rng, 0.6f, 1.6f);
        self->alive[i] = 1;
    }

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
EmberField_update(
    EmberFieldObject *self,
    PyObject *args
)
{
    double dt;

    if (!PyArg_ParseTuple(args, "d", &dt))
    {
        return NULL;
    }

    float fdt = (float)dt;

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

        self->radius[i] += self->speed[i] * fdt;
        self->angle[i] += self->drift[i] * fdt;
    }

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
EmberField_points(
    EmberFieldObject *self,
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
    npy_intp life_dims[1] = { alive_count };

    PyArrayObject *positions =
        (PyArrayObject *)PyArray_SimpleNew(2, position_dims, NPY_FLOAT32);

    PyArrayObject *life =
        (PyArrayObject *)PyArray_SimpleNew(1, life_dims, NPY_FLOAT32);

    if (positions == NULL || life == NULL)
    {
        Py_XDECREF(positions);
        Py_XDECREF(life);
        return NULL;
    }

    float *position_data = (float *)PyArray_DATA(positions);
    float *life_data = (float *)PyArray_DATA(life);

    int out = 0;

    for (int i = 0; i < self->capacity; i++)
    {
        if (!self->alive[i])
        {
            continue;
        }

        float radius = self->radius[i];
        float angle = self->angle[i];

        position_data[out * 2 + 0] = radius * cosf(angle);
        position_data[out * 2 + 1] = radius * sinf(angle);

        float lifetime = self->lifetime[i] > 1e-6f ? self->lifetime[i] : 1e-6f;

        life_data[out] = 1.0f - (self->age[i] / lifetime);

        out++;
    }

    PyObject *result = PyTuple_Pack(
        2,
        (PyObject *)positions,
        (PyObject *)life
    );

    Py_DECREF(positions);
    Py_DECREF(life);

    return result;
}

/* --------------------------------------------------------- */

static void
EmberField_dealloc(
    EmberFieldObject *self
)
{
    PyMem_Free(self->angle);
    PyMem_Free(self->radius);
    PyMem_Free(self->speed);
    PyMem_Free(self->drift);
    PyMem_Free(self->age);
    PyMem_Free(self->lifetime);
    PyMem_Free(self->alive);

    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* --------------------------------------------------------- */

static PyMemberDef EmberField_members[] =
{
    {
        "capacity",
        T_INT,
        offsetof(EmberFieldObject, capacity),
        READONLY,
        NULL
    },

    {
        "inner_radius",
        T_FLOAT,
        offsetof(EmberFieldObject, inner_radius),
        READONLY,
        NULL
    },

    { NULL }
};

static PyMethodDef EmberField_methods[] =
{
    {
        "spawn",
        (PyCFunction)EmberField_spawn,
        METH_VARARGS,
        "Spawn up to `count` new embers at the core."
    },

    {
        "update",
        (PyCFunction)EmberField_update,
        METH_VARARGS,
        "Advance the simulation by `dt` seconds."
    },

    {
        "points",
        (PyCFunction)EmberField_points,
        METH_NOARGS,
        "Returns (positions, life) for every currently alive ember."
    },

    { NULL, NULL, 0, NULL }
};

PyTypeObject EmberFieldType =
{
    PyVarObject_HEAD_INIT(NULL, 0)

    .tp_name = "_native.EmberField",
    .tp_basicsize = sizeof(EmberFieldObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)EmberField_init,
    .tp_dealloc = (destructor)EmberField_dealloc,
    .tp_methods = EmberField_methods,
    .tp_members = EmberField_members,
};
