/* modules/audioreactive/_native/segments.c */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#define NO_IMPORT_ARRAY
#include <numpy/arrayobject.h>

#include "segments.h"

PyObject *
segments_fixed_dashes(
    PyObject *Py_UNUSED(self),
    PyObject *args,
    PyObject *kwds
)
{
    PyObject *positions_obj;
    double dx, dy;
    double center_x = 0.0;
    double center_y = 0.0;

    static char *keywords[] = {
        "positions", "dx", "dy", "center_x", "center_y", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "Odd|dd", keywords,
            &positions_obj, &dx, &dy, &center_x, &center_y))
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
    float *src = (float *)PyArray_DATA(positions);

    float fdx = (float)dx;
    float fdy = (float)dy;
    float fcx = (float)center_x;
    float fcy = (float)center_y;

    PyObject *result = PyList_New(n);

    if (result == NULL)
    {
        Py_DECREF(positions);
        return NULL;
    }

    for (npy_intp p = 0; p < n; p++)
    {
        float x = src[p * 2 + 0] + fcx;
        float y = src[p * 2 + 1] + fcy;

        npy_intp dims[2] = { 2, 2 };

        PyArrayObject *points =
            (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_FLOAT32);

        if (points == NULL)
        {
            Py_DECREF(result);
            Py_DECREF(positions);
            return NULL;
        }

        float *data = (float *)PyArray_DATA(points);

        data[0] = x;
        data[1] = y;
        data[2] = x + fdx;
        data[3] = y + fdy;

        PyList_SET_ITEM(result, p, (PyObject *)points);
    }

    Py_DECREF(positions);

    return result;
}

PyObject *
segments_life_dashes(
    PyObject *Py_UNUSED(self),
    PyObject *args,
    PyObject *kwds
)
{
    PyObject *positions_obj;
    PyObject *life_obj;
    double center_x = 0.0;
    double center_y = 0.0;
    double size_base = 1.0;
    double size_scale = 1.0;

    static char *keywords[] = {
        "positions", "life", "center_x", "center_y",
        "size_base", "size_scale", NULL
    };

    if (!PyArg_ParseTupleAndKeywords(
            args, kwds, "OO|dddd", keywords,
            &positions_obj, &life_obj, &center_x, &center_y,
            &size_base, &size_scale))
    {
        return NULL;
    }

    PyArrayObject *positions = (PyArrayObject *)PyArray_FROM_OTF(
        positions_obj, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY | NPY_ARRAY_FORCECAST);

    PyArrayObject *life = (PyArrayObject *)PyArray_FROM_OTF(
        life_obj, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY | NPY_ARRAY_FORCECAST);

    if (positions == NULL || life == NULL)
    {
        Py_XDECREF(positions);
        Py_XDECREF(life);
        return NULL;
    }

    if (PyArray_NDIM(positions) != 2 || PyArray_DIM(positions, 1) != 2)
    {
        PyErr_SetString(PyExc_ValueError, "positions must have shape (N, 2)");
        Py_DECREF(positions);
        Py_DECREF(life);
        return NULL;
    }

    npy_intp n = PyArray_DIM(positions, 0);

    if (PyArray_DIM(life, 0) != n)
    {
        PyErr_SetString(PyExc_ValueError, "life must have shape (N,)");
        Py_DECREF(positions);
        Py_DECREF(life);
        return NULL;
    }

    float *pos_data = (float *)PyArray_DATA(positions);
    float *life_data = (float *)PyArray_DATA(life);

    float fcx = (float)center_x;
    float fcy = (float)center_y;
    float fbase = (float)size_base;
    float fscale = (float)size_scale;

    PyObject *result = PyList_New(n);

    if (result == NULL)
    {
        Py_DECREF(positions);
        Py_DECREF(life);
        return NULL;
    }

    for (npy_intp p = 0; p < n; p++)
    {
        float x = pos_data[p * 2 + 0] + fcx;
        float y = pos_data[p * 2 + 1] + fcy;

        float size = fbase + life_data[p] * fscale;

        npy_intp dims[2] = { 2, 2 };

        PyArrayObject *points =
            (PyArrayObject *)PyArray_SimpleNew(2, dims, NPY_FLOAT32);

        if (points == NULL)
        {
            Py_DECREF(result);
            Py_DECREF(positions);
            Py_DECREF(life);
            return NULL;
        }

        float *data = (float *)PyArray_DATA(points);

        data[0] = x - size;
        data[1] = y;
        data[2] = x + size;
        data[3] = y;

        PyList_SET_ITEM(result, p, (PyObject *)points);
    }

    Py_DECREF(positions);
    Py_DECREF(life);

    return result;
}
