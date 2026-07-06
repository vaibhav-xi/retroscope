#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "stroke.h"

static PyObject *
build(
    PyObject *self,
    PyObject *args
)
{
    PyObject *points;
    double width;

    if (!PyArg_ParseTuple(
            args,
            "Od",
            &points,
            &width))
    {
        return NULL;
    }

    Py_ssize_t point_count = PyList_Size(points);

    if (point_count < 2)
    {
        return PyList_New(0);
    }

    /*
     * Pack Python tuples into a float array.
     */

    float packed_points[point_count * 2];

    for (Py_ssize_t i = 0; i < point_count; ++i)
    {
        PyObject *p = PyList_GetItem(
            points,
            i
        );

        packed_points[i * 2 + 0] =
            (float)PyFloat_AsDouble(
                PyTuple_GetItem(p, 0)
            );

        packed_points[i * 2 + 1] =
            (float)PyFloat_AsDouble(
                PyTuple_GetItem(p, 1)
            );
    }

    /*
     * Maximum possible output:
     * (point_count - 1) segments
     * × 12 floats per segment
     */

    int max_floats =
        (int)(point_count - 1) * 12;

    float vertices[max_floats];

    int written = stroke_build(

        packed_points,

        (int)point_count,

        (float)(width * 0.5),

        vertices

    );

    /*
     * Convert back to Python list.
     */

    PyObject *list = PyList_New(
        written
    );

    for (int i = 0; i < written; ++i)
    {
        PyList_SET_ITEM(

            list,

            i,

            PyFloat_FromDouble(
                vertices[i]
            )

        );
    }

    return list;
}

static PyMethodDef methods[] = {

    {
        "build",
        build,
        METH_VARARGS,
        ""
    },

    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {

    PyModuleDef_HEAD_INIT,

    "_native",

    NULL,

    -1,

    methods,
};

PyMODINIT_FUNC
PyInit__native(void)
{
    return PyModule_Create(
        &module
    );
}