#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>

#include <structmember.h>
#include <math.h>
#include <time.h>

#include "ring_field.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static int
RingField_init(
    RingFieldObject *self,
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

    self->radius = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->speed = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->strength = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->wobble = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->rotation = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->spin = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->age = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->lifetime = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->alive = (unsigned char *)PyMem_Calloc(capacity, sizeof(unsigned char));

    if (
        !self->radius || !self->speed || !self->strength || !self->wobble ||
        !self->rotation || !self->spin || !self->age || !self->lifetime ||
        !self->alive
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
RingField_spawn(
    RingFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    double strength;
    double speed;
    double wobble = 0.0;
    double start_radius = 6.0;
    double spin_min = 0.0;
    double spin_max = 0.0;
    double lifetime_base = 0.5;
    double lifetime_coefficient = 0.03;
    int randomize_rotation = 1;
    double start_rotation = 0.0;

    static char *keywords[] = {
        "strength", "speed", "wobble", "start_radius",
        "spin_min", "spin_max", "lifetime_base", "lifetime_coefficient",
        "randomize_rotation", "start_rotation",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "dd|ddddddpd", keywords,
            &strength, &speed, &wobble, &start_radius,
            &spin_min, &spin_max, &lifetime_base, &lifetime_coefficient,
            &randomize_rotation, &start_rotation))
    {
        return NULL;
    }

    int i = self->cursor;

    self->cursor = (self->cursor + 1) % self->capacity;

    self->radius[i] = (float)start_radius;
    self->speed[i] = (float)speed;
    self->strength[i] = (float)strength;
    self->wobble[i] = (float)wobble;

    self->rotation[i] = randomize_rotation
        ? rng_uniform(&self->rng, 0.0f, (float)(2.0 * M_PI))
        : (float)start_rotation;

    self->spin[i] = rng_uniform(&self->rng, (float)spin_min, (float)spin_max);
    self->age[i] = 0.0f;
    self->lifetime[i] =
        (float)lifetime_base + (float)strength * (float)lifetime_coefficient;
    self->alive[i] = 1;

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
RingField_update(
    RingFieldObject *self,
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
        self->rotation[i] += self->spin[i] * fdt;
    }

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyObject *
RingField_rings(
    RingFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    double cx, cy;
    int segments;
    double wobble_scale = 6.0;
    double wobble_frequency = 5.0;

    static char *keywords[] = {
        "cx", "cy", "segments", "wobble_scale", "wobble_frequency", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "ddi|dd", keywords,
            &cx, &cy, &segments, &wobble_scale, &wobble_frequency))
    {
        return NULL;
    }

    PyObject *result = PyList_New(0);

    if (result == NULL)
    {
        return NULL;
    }

    for (int i = 0; i < self->capacity; i++)
    {
        if (!self->alive[i])
        {
            continue;
        }

        float life = 1.0f - (self->age[i] / fmaxf(self->lifetime[i], 1e-6f));

        float wobble_amount = self->wobble[i] * (float)wobble_scale * life;

        npy_intp dims[2] = { segments + 1, 2 };

        PyArrayObject *points =
            (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_FLOAT32);

        if (points == NULL)
        {
            Py_DECREF(result);
            return NULL;
        }

        float *data = (float *)PyArray_DATA(points);

        for (int s = 0; s <= segments; s++)
        {
            float t = (float)s / (float)segments;

            float angle = self->rotation[i] + t * (float)(2.0 * M_PI);

            float radius =
                self->radius[i]
                + wobble_amount * sinf(angle * (float)wobble_frequency);

            data[s * 2 + 0] = (float)cx + radius * cosf(angle);
            data[s * 2 + 1] = (float)cy + radius * sinf(angle);
        }

        PyObject *entry = Py_BuildValue("(Of)", (PyObject *)points, life);

        Py_DECREF(points);

        if (entry == NULL)
        {
            Py_DECREF(result);
            return NULL;
        }

        PyList_Append(result, entry);
        Py_DECREF(entry);
    }

    return result;
}

/* --------------------------------------------------------- */

static PyObject *
RingField_shells(
    RingFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    double cx, cy;
    int sides;

    static char *keywords[] = { "cx", "cy", "sides", NULL };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "ddi", keywords, &cx, &cy, &sides))
    {
        return NULL;
    }

    PyObject *result = PyList_New(0);

    if (result == NULL)
    {
        return NULL;
    }

    for (int i = 0; i < self->capacity; i++)
    {
        if (!self->alive[i])
        {
            continue;
        }

        float life = 1.0f - (self->age[i] / fmaxf(self->lifetime[i], 1e-6f));

        float visible = (float)sides * fminf(life * 1.4f, 1.0f);

        int visible_sides = (int)visible;

        if (visible_sides < 3)
        {
            visible_sides = 3;
        }

        npy_intp dims[2] = { visible_sides + 1, 2 };

        PyArrayObject *points =
            (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_FLOAT32);

        if (points == NULL)
        {
            Py_DECREF(result);
            return NULL;
        }

        float *data = (float *)PyArray_DATA(points);

        for (int s = 0; s <= visible_sides; s++)
        {
            float angle =
                self->rotation[i]
                + ((float)s / (float)visible_sides) * (float)(2.0 * M_PI);

            data[s * 2 + 0] = (float)cx + self->radius[i] * cosf(angle);
            data[s * 2 + 1] = (float)cy + self->radius[i] * sinf(angle);
        }

        PyObject *entry = Py_BuildValue("(Of)", (PyObject *)points, life);

        Py_DECREF(points);

        if (entry == NULL)
        {
            Py_DECREF(result);
            return NULL;
        }

        PyList_Append(result, entry);
        Py_DECREF(entry);
    }

    return result;
}

/* --------------------------------------------------------- */

static PyObject *
RingField_kick(
    RingFieldObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    PyObject *positions_obj;
    double cx, cy;
    double gain = 1.0;
    double band = 16.0;

    static char *keywords[] = { "positions", "cx", "cy", "gain", "band", NULL };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "Odd|dd", keywords,
            &positions_obj, &cx, &cy, &gain, &band))
    {
        return NULL;
    }

    PyArrayObject *positions = (PyArrayObject *)PyArray_FROM_OTF(
        positions_obj, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY | NPY_ARRAY_FORCECAST);

    if (positions == NULL)
    {
        return NULL;
    }

    if (PyArray_NDIM(positions) != 2 || PyArray_DIM(positions, 1) != 2)
    {
        PyErr_SetString(PyExc_ValueError, "positions must have shape (N, 2)");
        Py_DECREF(positions);
        return NULL;
    }

    npy_intp n = PyArray_DIM(positions, 0);
    float *data = (float *)PyArray_DATA(positions);

    float fcx = (float)cx;
    float fcy = (float)cy;
    float fgain = (float)gain;
    float fband = (float)band;

    for (npy_intp p = 0; p < n; p++)
    {
        float dx = data[p * 2 + 0] - fcx;
        float dy = data[p * 2 + 1] - fcy;

        float dist = sqrtf(dx * dx + dy * dy) + 1e-6f;

        for (int i = 0; i < self->capacity; i++)
        {
            if (!self->alive[i])
            {
                continue;
            }

            if (fabsf(dist - self->radius[i]) >= fband)
            {
                continue;
            }

            float push = self->strength[i] * fgain;

            data[p * 2 + 0] += (dx / dist) * push;
            data[p * 2 + 1] += (dy / dist) * push;
        }
    }

    return (PyObject *)positions;
}

/* --------------------------------------------------------- */

static void
RingField_dealloc(
    RingFieldObject *self
)
{
    PyMem_Free(self->radius);
    PyMem_Free(self->speed);
    PyMem_Free(self->strength);
    PyMem_Free(self->wobble);
    PyMem_Free(self->rotation);
    PyMem_Free(self->spin);
    PyMem_Free(self->age);
    PyMem_Free(self->lifetime);
    PyMem_Free(self->alive);

    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* --------------------------------------------------------- */

static PyMemberDef RingField_members[] =
{
    { "capacity", T_INT, offsetof(RingFieldObject, capacity), READONLY, NULL },
    { NULL }
};

static PyMethodDef RingField_methods[] =
{
    {
        "spawn",
        (PyCFunction)RingField_spawn,
        METH_VARARGS | METH_KEYWORDS,
        "Spawn one new expanding ring."
    },
    {
        "update",
        (PyCFunction)RingField_update,
        METH_VARARGS,
        "Advance the simulation by `dt` seconds."
    },
    {
        "rings",
        (PyCFunction)RingField_rings,
        METH_VARARGS | METH_KEYWORDS,
        "Wobble-perturbed circle outlines, one per alive ring."
    },
    {
        "shells",
        (PyCFunction)RingField_shells,
        METH_VARARGS | METH_KEYWORDS,
        "Rotating polygon outlines that lose sides with age."
    },
    {
        "kick",
        (PyCFunction)RingField_kick,
        METH_VARARGS | METH_KEYWORDS,
        "Push positions outward where an alive ring's radius passes through them."
    },
    { NULL, NULL, 0, NULL }
};

PyTypeObject RingFieldType =
{
    PyVarObject_HEAD_INIT(NULL, 0)

    .tp_name = "_native.RingField",
    .tp_basicsize = sizeof(RingFieldObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)RingField_init,
    .tp_dealloc = (destructor)RingField_dealloc,
    .tp_methods = RingField_methods,
    .tp_members = RingField_members,
};
