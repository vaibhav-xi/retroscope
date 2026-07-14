#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <numpy/arrayobject.h>

#include <math.h>

#include "spectrum_ring.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

PyObject *
spectrum_ring_build(
    PyObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    PyObject *magnitudes_obj;
    double base_radius;
    double amplitude;
    double rotation = 0.0;
    int mirror = 1;

    static char *keywords[] = {
        "magnitudes",
        "base_radius",
        "amplitude",
        "rotation",
        "mirror",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args,
            kwds,
            "Odd|dp",
            keywords,
            &magnitudes_obj,
            &base_radius,
            &amplitude,
            &rotation,
            &mirror))
    {
        return NULL;
    }

    PyArrayObject *magnitudes =
        (PyArrayObject *)PyArray_FROM_OTF(
            magnitudes_obj,
            NPY_FLOAT32,
            NPY_ARRAY_IN_ARRAY
        );

    if (magnitudes == NULL)
    {
        return NULL;
    }

    int n = (int)PyArray_DIM(magnitudes, 0);

    float *values = (float *)PyArray_DATA(magnitudes);

    int count = mirror ? n * 2 : n;

    if (count < 1)
    {
        Py_DECREF(magnitudes);

        npy_intp empty_dims[2] = { 0, 2 };

        return PyArray_SimpleNew(2, empty_dims, NPY_FLOAT32);
    }

    npy_intp dims[2] = { count + 1, 2 };

    PyArrayObject *result =
        (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_FLOAT32);

    if (result == NULL)
    {
        Py_DECREF(magnitudes);
        return NULL;
    }

    float *out = (float *)PyArray_DATA(result);

    for (int i = 0; i < count; i++)
    {
        float value;

        if (!mirror || i < n)
        {
            value = values[i];
        }
        else
        {
            /*
             * Mirrors the pure-Python
             * np.concatenate([values, values[::-1]]).
             */

            value = values[(2 * n - 1) - i];
        }

        float angle =
            (float)rotation +
            ((float)i / (float)count) * (float)(2.0 * M_PI);

        float radius = (float)base_radius + value * (float)amplitude;

        out[i * 2 + 0] = radius * cosf(angle);
        out[i * 2 + 1] = radius * sinf(angle);
    }

    /*
     * Close the loop - last point repeats the first, matching
     * np.vstack([points, points[0]]).
     */

    out[count * 2 + 0] = out[0];
    out[count * 2 + 1] = out[1];

    Py_DECREF(magnitudes);

    return (PyObject *)result;
}
