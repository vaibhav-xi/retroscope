#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>

#include <structmember.h>
#include <math.h>
#include <time.h>

#include "chaos_field.h"

static void
ChaosField_seed_all(
    ChaosFieldObject *self
)
{
    for (int i = 0; i < self->capacity; i++)
    {
        self->x[i] = rng_uniform(&self->rng, -1.5f, 1.5f);
        self->y[i] = rng_uniform(&self->rng, -1.5f, 1.5f);
    }
}

/* --------------------------------------------------------- */

static int
ChaosField_init(
    ChaosFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    int capacity;
    unsigned long seed = 0;

    static char *keywords[] = { "capacity", "seed", NULL };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "i|k", keywords, &capacity, &seed))
    {
        return -1;
    }

    if (capacity <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "capacity must be positive");
        return -1;
    }

    self->capacity = capacity;

    self->x = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->y = (float *)PyMem_Calloc(capacity, sizeof(float));

    if (!self->x || !self->y)
    {
        PyErr_NoMemory();
        return -1;
    }

    self->a = 1.1f;
    self->b = -1.8f;
    self->c = 1.9f;
    self->d = -1.5f;
    self->kick = 0.0f;

    if (seed == 0)
    {
        seed = (unsigned long)time(NULL);
    }

    rng_seed(&self->rng, (uint32_t)seed);

    ChaosField_seed_all(self);

    return 0;
}

/* --------------------------------------------------------- */

static PyObject *
ChaosField_set_parameters(
    ChaosFieldObject *self,
    PyObject *args
)
{
    double a, b, c, d;

    if (!PyArg_ParseTuple(args, "dddd", &a, &b, &c, &d))
    {
        return NULL;
    }

    self->a = (float)a;
    self->b = (float)b;
    self->c = (float)c;
    self->d = (float)d;

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
ChaosField_detonate(
    ChaosFieldObject *self,
    PyObject *args
)
{
    double strength;

    if (!PyArg_ParseTuple(args, "d", &strength))
    {
        return NULL;
    }

    if ((float)strength > self->kick)
    {
        self->kick = (float)strength;
    }

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
ChaosField_update(
    ChaosFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    double dt;
    double reseed_fraction = 0.02;

    static char *keywords[] = { "dt", "reseed_fraction", NULL };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "d|d", keywords, &dt, &reseed_fraction))
    {
        return NULL;
    }

    self->kick *= expf(-(float)dt * 3.0f);

    for (int i = 0; i < self->capacity; i++)
    {
        float x = self->x[i];
        float y = self->y[i];

        float new_x = sinf(self->a * y) - cosf(self->b * x);
        float new_y = sinf(self->c * x) - cosf(self->d * y);

        self->x[i] = new_x;
        self->y[i] = new_y;
    }

    int reseed_count = (int)(self->capacity * reseed_fraction);

    if (reseed_count < 1)
    {
        reseed_count = 1;
    }

    for (int n = 0; n < reseed_count; n++)
    {
        uint32_t index = rng_next(&self->rng) % (uint32_t)self->capacity;

        self->x[index] = rng_uniform(&self->rng, -1.5f, 1.5f);
        self->y[index] = rng_uniform(&self->rng, -1.5f, 1.5f);
    }

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
ChaosField_points(
    ChaosFieldObject *self,
    PyObject *args
)
{
    double cx, cy, scale;

    if (!PyArg_ParseTuple(args, "ddd", &cx, &cy, &scale))
    {
        return NULL;
    }

    npy_intp dims[2] = { self->capacity, 2 };

    PyArrayObject *result =
        (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_FLOAT32);

    if (result == NULL)
    {
        return NULL;
    }

    float *data = (float *)PyArray_DATA(result);

    float effective_scale = (float)scale * (1.0f + self->kick);

    for (int i = 0; i < self->capacity; i++)
    {
        data[i * 2 + 0] = (float)cx + self->x[i] * effective_scale;
        data[i * 2 + 1] = (float)cy + self->y[i] * effective_scale;
    }

    return (PyObject *)result;
}

/* --------------------------------------------------------- */

static void
ChaosField_dealloc(
    ChaosFieldObject *self
)
{
    PyMem_Free(self->x);
    PyMem_Free(self->y);

    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* --------------------------------------------------------- */

static PyMemberDef ChaosField_members[] =
{
    { "capacity", T_INT, offsetof(ChaosFieldObject, capacity), READONLY, NULL },
    { NULL }
};

static PyMethodDef ChaosField_methods[] =
{
    {
        "set_parameters",
        (PyCFunction)ChaosField_set_parameters,
        METH_VARARGS,
        "Set the (a, b, c, d) chaos map coefficients."
    },
    {
        "detonate",
        (PyCFunction)ChaosField_detonate,
        METH_VARARGS,
        "Temporarily blow the cloud outward by `strength`, decaying over time."
    },
    {
        "update",
        (PyCFunction)ChaosField_update,
        METH_VARARGS | METH_KEYWORDS,
        "Advance the chaos map by `dt` seconds and reseed a fraction of points."
    },
    {
        "points",
        (PyCFunction)ChaosField_points,
        METH_VARARGS,
        "Returns every point mapped to (cx, cy) at `scale`."
    },
    { NULL, NULL, 0, NULL }
};

PyTypeObject ChaosFieldType =
{
    PyVarObject_HEAD_INIT(NULL, 0)

    .tp_name = "_native.ChaosField",
    .tp_basicsize = sizeof(ChaosFieldObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)ChaosField_init,
    .tp_dealloc = (destructor)ChaosField_dealloc,
    .tp_methods = ChaosField_methods,
    .tp_members = ChaosField_members,
};
