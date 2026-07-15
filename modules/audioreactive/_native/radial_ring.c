#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>

#include <math.h>

#include "radial_ring.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

PyObject *
radial_ring_build(
    PyObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    PyObject *radius_obj;
    double base_angle = 0.0;
    double angle_span = 2.0 * M_PI;
    double center_x = 0.0;
    double center_y = 0.0;
    int close_loop = 1;

    static char *keywords[] = {
        "radius", "base_angle", "angle_span",
        "center_x", "center_y", "close_loop", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "O|ddddp", keywords,
            &radius_obj, &base_angle, &angle_span,
            &center_x, &center_y, &close_loop))
    {
        return NULL;
    }

    PyArrayObject *radius =
        (PyArrayObject *)PyArray_FROM_OTF(
            radius_obj,
            NPY_FLOAT32,
            NPY_ARRAY_IN_ARRAY | NPY_ARRAY_FORCECAST
        );

    if (radius == NULL)
    {
        return NULL;
    }

    int n = (int)PyArray_DIM(radius, 0);

    float *radius_data = (float *)PyArray_DATA(radius);

    if (n < 1)
    {
        Py_DECREF(radius);

        npy_intp empty_dims[2] = { 0, 2 };

        return PyArray_SimpleNew(2, empty_dims, NPY_FLOAT32);
    }

    int point_count = close_loop ? n + 1 : n;

    npy_intp dims[2] = { point_count, 2 };

    PyArrayObject *result =
        (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_FLOAT32);

    if (result == NULL)
    {
        Py_DECREF(radius);
        return NULL;
    }

    float *out = (float *)PyArray_DATA(result);

    for (int i = 0; i < n; i++)
    {
        float angle =
            (float)base_angle + ((float)i / (float)n) * (float)angle_span;

        float r = radius_data[i];

        out[i * 2 + 0] = (float)center_x + r * cosf(angle);
        out[i * 2 + 1] = (float)center_y + r * sinf(angle);
    }

    if (close_loop)
    {
        out[n * 2 + 0] = out[0];
        out[n * 2 + 1] = out[1];
    }

    Py_DECREF(radius);

    return (PyObject *)result;
}
