/* modules/audioreactive/_native/boid_swarm.c */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>

#include <structmember.h>
#include <math.h>
#include <time.h>
#include <stdlib.h>

#include "boid_swarm.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static int
BoidSwarm_init(
    BoidSwarmObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    int capacity;
    double neighbor_radius = 70.0;
    unsigned long seed = 0;

    static char *keywords[] = { "capacity", "neighbor_radius", "seed", NULL };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "i|dk", keywords,
            &capacity, &neighbor_radius, &seed))
    {
        return -1;
    }

    if (capacity <= 0)
    {
        PyErr_SetString(PyExc_ValueError, "capacity must be positive");
        return -1;
    }

    self->capacity = capacity;
    self->neighbor_radius = (float)neighbor_radius;

    self->pos_x = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->pos_y = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->vel_x = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->vel_y = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->scratch_vx = (float *)PyMem_Calloc(capacity, sizeof(float));
    self->scratch_vy = (float *)PyMem_Calloc(capacity, sizeof(float));

    if (
        !self->pos_x || !self->pos_y || !self->vel_x || !self->vel_y ||
        !self->scratch_vx || !self->scratch_vy
    )
    {
        PyErr_NoMemory();
        return -1;
    }

    if (seed == 0)
    {
        seed = (unsigned long)time(NULL);
    }

    rng_seed(&self->rng, (uint32_t)seed);

    for (int i = 0; i < capacity; i++)
    {
        float angle = rng_uniform(&self->rng, 0.0f, (float)(2.0 * M_PI));
        float radius = rng_uniform(&self->rng, 20.0f, 120.0f);

        self->pos_x[i] = radius * cosf(angle);
        self->pos_y[i] = radius * sinf(angle);

        self->vel_x[i] = rng_uniform(&self->rng, -20.0f, 20.0f);
        self->vel_y[i] = rng_uniform(&self->rng, -20.0f, 20.0f);
    }

    return 0;
}

/* --------------------------------------------------------- */

static PyObject *
BoidSwarm_update(
    BoidSwarmObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    double dt;
    double focus_x, focus_y;
    double cohesion, alignment, separation, jitter, max_speed;
    int has_threat = 0;
    double threat_x = 0.0, threat_y = 0.0, threat_strength = 0.0;

    static char *keywords[] = {
        "dt", "focus_x", "focus_y", "cohesion", "alignment",
        "separation", "jitter", "max_speed",
        "has_threat", "threat_x", "threat_y", "threat_strength",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "dddddddd|pddd", keywords,
            &dt, &focus_x, &focus_y, &cohesion, &alignment,
            &separation, &jitter, &max_speed,
            &has_threat, &threat_x, &threat_y, &threat_strength))
    {
        return NULL;
    }

    int n = self->capacity;

    float radius2 = self->neighbor_radius * self->neighbor_radius;
    float close_radius = self->neighbor_radius * 0.35f;
    float close2 = close_radius * close_radius;

    float fdt = (float)dt;

    for (int i = 0; i < n; i++)
    {
        float px = self->pos_x[i];
        float py = self->pos_y[i];
        float vx = self->vel_x[i];
        float vy = self->vel_y[i];

        float cohesion_sum_x = 0.0f, cohesion_sum_y = 0.0f;
        float align_sum_x = 0.0f, align_sum_y = 0.0f;
        int neighbor_count = 0;

        float sep_x = 0.0f, sep_y = 0.0f;

        for (int j = 0; j < n; j++)
        {
            if (j == i)
            {
                continue;
            }

            float dx = px - self->pos_x[j];
            float dy = py - self->pos_y[j];

            float dist2 = dx * dx + dy * dy;

            if (dist2 < radius2)
            {
                cohesion_sum_x += self->pos_x[j];
                cohesion_sum_y += self->pos_y[j];

                align_sum_x += self->vel_x[j];
                align_sum_y += self->vel_y[j];

                neighbor_count++;
            }

            if (dist2 < close2)
            {
                float inv_dist = 1.0f / sqrtf(fmaxf(dist2, 1e-6f));

                sep_x += dx * inv_dist;
                sep_y += dy * inv_dist;
            }
        }

        int divisor = neighbor_count > 0 ? neighbor_count : 1;

        float avg_x = cohesion_sum_x / (float)divisor;
        float avg_y = cohesion_sum_y / (float)divisor;
        float avg_vx = align_sum_x / (float)divisor;
        float avg_vy = align_sum_y / (float)divisor;

        float cohesion_x = (avg_x - px) * (float)cohesion;
        float cohesion_y = (avg_y - py) * (float)cohesion;

        float align_x = (avg_vx - vx) * (float)alignment;
        float align_y = (avg_vy - vy) * (float)alignment;

        float separation_x = sep_x * (float)separation;
        float separation_y = sep_y * (float)separation;

        float focus_force_x = ((float)focus_x - px) * 0.015f;
        float focus_force_y = ((float)focus_y - py) * 0.015f;

        float jitter_x = rng_uniform(&self->rng, -(float)jitter, (float)jitter);
        float jitter_y = rng_uniform(&self->rng, -(float)jitter, (float)jitter);

        float flee_x = 0.0f, flee_y = 0.0f;

        if (has_threat && threat_strength > 0.0)
        {
            float tdx = px - (float)threat_x;
            float tdy = py - (float)threat_y;

            float tdist = sqrtf(tdx * tdx + tdy * tdy) + 1e-6f;

            float flee_radius = 160.0f;

            float influence = 1.0f - tdist / flee_radius;

            if (influence < 0.0f)
            {
                influence = 0.0f;
            }

            if (influence > 1.0f)
            {
                influence = 1.0f;
            }

            influence = influence * influence;

            flee_x = (tdx / tdist) * influence * (float)threat_strength;
            flee_y = (tdy / tdist) * influence * (float)threat_strength;
        }

        float dist_from_center = sqrtf(px * px + py * py) + 1e-6f;

        float leash = (dist_from_center - 200.0f) * 0.4f;

        if (leash < 0.0f)
        {
            leash = 0.0f;
        }

        float leash_x = -(px / dist_from_center) * leash;
        float leash_y = -(py / dist_from_center) * leash;

        self->scratch_vx[i] = vx + (
            cohesion_x + align_x + separation_x +
            focus_force_x + jitter_x + leash_x + flee_x
        ) * fdt;

        self->scratch_vy[i] = vy + (
            cohesion_y + align_y + separation_y +
            focus_force_y + jitter_y + leash_y + flee_y
        ) * fdt;
    }

    float fmax_speed = (float)max_speed;

    for (int i = 0; i < n; i++)
    {
        float nvx = self->scratch_vx[i];
        float nvy = self->scratch_vy[i];

        float speed = sqrtf(nvx * nvx + nvy * nvy);

        if (speed > fmax_speed)
        {
            float scale = fmax_speed / fmaxf(speed, 1e-6f);

            nvx *= scale;
            nvy *= scale;
        }

        self->vel_x[i] = nvx;
        self->vel_y[i] = nvy;

        self->pos_x[i] += nvx * fdt;
        self->pos_y[i] += nvy * fdt;
    }

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

typedef struct
{
    int i;
    int j;
    float dist2;
} BoidLinkCandidate;

static int
_boid_link_compare(
    const void *a,
    const void *b
)
{
    const BoidLinkCandidate *la = (const BoidLinkCandidate *)a;
    const BoidLinkCandidate *lb = (const BoidLinkCandidate *)b;

    if (la->dist2 < lb->dist2)
    {
        return -1;
    }

    if (la->dist2 > lb->dist2)
    {
        return 1;
    }

    return 0;
}

static PyObject *
BoidSwarm_neighbor_links(
    BoidSwarmObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    int max_links;
    double link_radius;
    double center_x = 0.0;
    double center_y = 0.0;

    static char *keywords[] = {
        "max_links", "link_radius", "center_x", "center_y", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "id|dd", keywords,
            &max_links, &link_radius, &center_x, &center_y))
    {
        return NULL;
    }

    int n = self->capacity;

    float radius2 = (float)(link_radius * link_radius);

    int max_pairs = n * (n - 1) / 2;

    if (max_pairs <= 0)
    {
        npy_intp empty_dims[3] = { 0, 2, 2 };
        return PyArray_SimpleNew(3, empty_dims, NPY_FLOAT32);
    }

    BoidLinkCandidate *candidates = (BoidLinkCandidate *)PyMem_Malloc(
        sizeof(BoidLinkCandidate) * (size_t)max_pairs
    );

    if (candidates == NULL)
    {
        return PyErr_NoMemory();
    }

    int count = 0;

    for (int i = 0; i < n; i++)
    {
        for (int j = i + 1; j < n; j++)
        {
            float dx = self->pos_x[i] - self->pos_x[j];
            float dy = self->pos_y[i] - self->pos_y[j];

            float dist2 = dx * dx + dy * dy;

            if (dist2 < radius2)
            {
                candidates[count].i = i;
                candidates[count].j = j;
                candidates[count].dist2 = dist2;
                count++;
            }
        }
    }

    if (count > max_links)
    {
        qsort(
            candidates, (size_t)count, sizeof(BoidLinkCandidate),
            _boid_link_compare
        );

        count = max_links;
    }

    /*
     * Single (count, 2, 2) array instead of a Python list of
     * `count` separate (2, 2) arrays.
     */

    npy_intp dims[3] = { count, 2, 2 };

    PyArrayObject *result =
        (PyArrayObject *)PyArray_SimpleNew(3, dims, NPY_FLOAT32);

    if (result == NULL)
    {
        PyMem_Free(candidates);
        return NULL;
    }

    float *dst = (float *)PyArray_DATA(result);

    float fcx = (float)center_x;
    float fcy = (float)center_y;

    for (int k = 0; k < count; k++)
    {
        int i = candidates[k].i;
        int j = candidates[k].j;

        float *out = dst + k * 4;

        out[0] = self->pos_x[i] + fcx;
        out[1] = self->pos_y[i] + fcy;
        out[2] = self->pos_x[j] + fcx;
        out[3] = self->pos_y[j] + fcy;
    }

    PyMem_Free(candidates);

    return (PyObject *)result;
}

static PyObject *
BoidSwarm_render_points(
    BoidSwarmObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    double center_x = 0.0;
    double center_y = 0.0;

    static char *keywords[] = { "center_x", "center_y", NULL };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "|dd", keywords, &center_x, &center_y))
    {
        return NULL;
    }

    float fcx = (float)center_x;
    float fcy = (float)center_y;

    int n = self->capacity;

    /*
     * Single (n, 4, 2) array instead of a Python list of n
     * separate (4, 2) arrays.
     */

    npy_intp dims[3] = { n, 4, 2 };

    PyArrayObject *result =
        (PyArrayObject *)PyArray_SimpleNew(3, dims, NPY_FLOAT32);

    if (result == NULL)
    {
        return NULL;
    }

    float *dst = (float *)PyArray_DATA(result);

    float size = 6.0f;

    for (int i = 0; i < n; i++)
    {
        float speed = sqrtf(
            self->vel_x[i] * self->vel_x[i] +
            self->vel_y[i] * self->vel_y[i]
        ) + 1e-6f;

        float dir_x = self->vel_x[i] / speed;
        float dir_y = self->vel_y[i] / speed;

        float perp_x = -dir_y;
        float perp_y = dir_x;

        float px = self->pos_x[i] + fcx;
        float py = self->pos_y[i] + fcy;

        float nose_x = px + dir_x * size;
        float nose_y = py + dir_y * size;

        float left_x = px - dir_x * size * 0.6f + perp_x * size * 0.5f;
        float left_y = py - dir_y * size * 0.6f + perp_y * size * 0.5f;

        float right_x = px - dir_x * size * 0.6f - perp_x * size * 0.5f;
        float right_y = py - dir_y * size * 0.6f - perp_y * size * 0.5f;

        float *out = dst + i * 8;

        out[0] = nose_x;  out[1] = nose_y;
        out[2] = left_x;  out[3] = left_y;
        out[4] = right_x; out[5] = right_y;
        out[6] = nose_x;  out[7] = nose_y;
    }

    return (PyObject *)result;
}

/* --------------------------------------------------------- */

static void
BoidSwarm_dealloc(
    BoidSwarmObject *self
)
{
    PyMem_Free(self->pos_x);
    PyMem_Free(self->pos_y);
    PyMem_Free(self->vel_x);
    PyMem_Free(self->vel_y);
    PyMem_Free(self->scratch_vx);
    PyMem_Free(self->scratch_vy);

    Py_TYPE(self)->tp_free((PyObject *)self);
}

/* --------------------------------------------------------- */

static PyMemberDef BoidSwarm_members[] =
{
    { "capacity", T_INT, offsetof(BoidSwarmObject, capacity), READONLY, NULL },
    { NULL }
};

static PyMethodDef BoidSwarm_methods[] =
{
    {
        "update",
        (PyCFunction)BoidSwarm_update,
        METH_VARARGS | METH_KEYWORDS,
        "Advance the flocking simulation by dt seconds."
    },
    {
        "neighbor_links",
        (PyCFunction)BoidSwarm_neighbor_links,
        METH_VARARGS | METH_KEYWORDS,
        "Line segments between nearby boid pairs, closest-first when truncated."
    },
    {
        "render_points",
        (PyCFunction)BoidSwarm_render_points,
        METH_VARARGS | METH_KEYWORDS,
        "Per-boid arrow-shaped outline (nose/left/right/nose)."
    },
    { NULL, NULL, 0, NULL }
};

PyTypeObject BoidSwarmType =
{
    PyVarObject_HEAD_INIT(NULL, 0)

    .tp_name = "_native.BoidSwarm",
    .tp_basicsize = sizeof(BoidSwarmObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)BoidSwarm_init,
    .tp_dealloc = (destructor)BoidSwarm_dealloc,
    .tp_methods = BoidSwarm_methods,
    .tp_members = BoidSwarm_members,
};
