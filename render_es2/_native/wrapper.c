#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <numpy/arrayobject.h>

#include "stroke.h"

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

    /*
     * Get current count.
     */

    PyObject *count_obj =
        PyObject_GetAttrString(
            vertex_buffer,
            "count"
        );

    if (count_obj == NULL)
    {
        return NULL;
    }

    int old_count =
        (int)PyLong_AsLong(
            count_obj
        );

    Py_DECREF(count_obj);

    /*
     * Make room for existing data + new data.
     */

    PyObject *reserve_result =
        PyObject_CallMethod(
            vertex_buffer,
            "reserve",
            "i",
            old_count + max_floats
        );

    if (reserve_result == NULL)
    {
        return NULL;
    }

    Py_DECREF(reserve_result);

    /*
     * Get NumPy array AFTER reserve().
     */

    PyObject *array =
        PyObject_CallMethod(
            vertex_buffer,
            "data",
            NULL
        );

    if (array == NULL)
    {
        return NULL;
    }

    PyArrayObject *vertex_array =
        (PyArrayObject *)array;

    float *vertices =
        (float *)PyArray_DATA(vertex_array);

    /*
     * Append after existing data.
     */

    vertices += old_count;

    float *packed_points =
        (float *)PyArray_DATA(
            points_array
        );

    /*
     * Write into free space.
     */

    int written =
        stroke_build(
            packed_points,
            (int)point_count,
            (float)(width * 0.5f),
            vertices
        );

    // printf(
    //     "old=%d written=%d new=%d\n",
    //     old_count,
    //     written,
    //     old_count + written
    // );

    /*
     * Update count.
     */

    PyObject *result =
        PyObject_CallMethod(
            vertex_buffer,
            "set_count",
            "i",
            old_count + written
        );

    Py_DECREF(array);

    if (result == NULL)
    {
        Py_DECREF(points_array);
        return NULL;
    }

    Py_DECREF(result);

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