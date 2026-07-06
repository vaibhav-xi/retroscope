#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* --------------------------------------------------------- */

static PyObject *
build(PyObject *self, PyObject *args)
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

    printf(
        "points = %zd  width = %.1f\n",
        PyList_Size(points),
        width
    );

    if (PyList_Size(points) >= 2)
    {
        PyObject *p0 = PyList_GetItem(points, 0);
        PyObject *p1 = PyList_GetItem(points, 1);

        double x0 = PyFloat_AsDouble(
            PyTuple_GetItem(p0, 0)
        );

        double y0 = PyFloat_AsDouble(
            PyTuple_GetItem(p0, 1)
        );

        double x1 = PyFloat_AsDouble(
            PyTuple_GetItem(p1, 0)
        );

        double y1 = PyFloat_AsDouble(
            PyTuple_GetItem(p1, 1)
        );

        printf(
            "(%.1f, %.1f) -> (%.1f, %.1f)\n",
            x0, y0,
            x1, y1
        );
    }

    PyObject *list = PyList_New(6);

    PyList_SET_ITEM(list, 0, PyFloat_FromDouble(-0.5));
    PyList_SET_ITEM(list, 1, PyFloat_FromDouble(-0.5));

    PyList_SET_ITEM(list, 2, PyFloat_FromDouble( 0.5));
    PyList_SET_ITEM(list, 3, PyFloat_FromDouble(-0.5));

    PyList_SET_ITEM(list, 4, PyFloat_FromDouble( 0.0));
    PyList_SET_ITEM(list, 5, PyFloat_FromDouble( 0.5));

    return list;
}

/* --------------------------------------------------------- */

static PyMethodDef methods[] = {

    {
        "build",
        build,
        METH_VARARGS,
        "Build stroke geometry."
    },

    {NULL, NULL, 0, NULL}
};

/* --------------------------------------------------------- */

static struct PyModuleDef module = {

    PyModuleDef_HEAD_INIT,

    "_stroke_builder",

    NULL,

    -1,

    methods,
};

/* --------------------------------------------------------- */

PyMODINIT_FUNC
PyInit__stroke_builder(void)
{
    return PyModule_Create(
        &module
    );
}