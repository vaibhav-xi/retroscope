#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <numpy/arrayobject.h>

#include "stroke.h"

#include "vertex_buffer.h"

static PyObject *
build(
    PyObject *self,
    PyObject *args
)
{
    PyArrayObject *points_array;
    double width;
    PyObject *vertex_buffer;

    PyObject *points;

    if (!PyArg_ParseTuple(
            args,
            "OdO",
            &points,
            &width,
            &vertex_buffer))
    {
        return NULL;
    }

    points_array =
        (PyArrayObject *)PyArray_FROM_OTF(

            points,

            NPY_FLOAT32,

            NPY_ARRAY_IN_ARRAY

        );

    if (points_array == NULL)
    {
        return NULL;
    }

    int point_count =
        (int)PyArray_DIM(
            points_array,
            0
        );

    float *packed_points =
        (float *)PyArray_DATA(
            points_array
        );

    if (point_count < 2)
    {
        Py_DECREF(points_array);
        Py_RETURN_NONE;
    }

    /*
     * Maximum floats this polyline can generate.
     */

    int max_floats =
        (int)(point_count - 1) * 12;

    int old_count;

    float *vertices =
        vertex_buffer_begin(
            vertex_buffer,
            max_floats,
            &old_count
        );

    if (vertices == NULL)
    {
        Py_DECREF(points_array);
        return NULL;
    }

    int written =
        stroke_build(
            packed_points,
            point_count,
            (float)(width * 0.5f),
            vertices
        );

    if (!vertex_buffer_finish(
            vertex_buffer,
            old_count + written
        ))
    {
        Py_DECREF(points_array);
        return NULL;
    }

    Py_DECREF(points_array);

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

static PyMethodDef methods[] = {

    {
        "build",
        build,
        METH_VARARGS,
        ""
    },

    {NULL, NULL, 0, NULL}
};

/* --------------------------------------------------------- */

static struct PyModuleDef module = {

    PyModuleDef_HEAD_INIT,

    "_native",

    NULL,

    -1,

    methods,
};

/* --------------------------------------------------------- */

PyMODINIT_FUNC
PyInit__native(void)
{
    import_array();

    return PyModule_Create(
        &module
    );
}