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
        "points = %zd   width = %.1f\n",
        PyList_Size(points),
        width
    );

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