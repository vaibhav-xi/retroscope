#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#include <numpy/arrayobject.h>

#include "ember_field.h"
#include "spectrum_ring.h"

static PyMethodDef methods[] =
{
    {
        "spectrum_ring",
        (PyCFunction)spectrum_ring_build,
        METH_VARARGS | METH_KEYWORDS,
        "Build a closed ring polyline from a spectrum array."
    },

    { NULL, NULL, 0, NULL }
};

static struct PyModuleDef moduledef =
{
    PyModuleDef_HEAD_INIT,

    "_native",

    "Native acceleration for modules/audioreactive.",

    -1,

    methods,
};

PyMODINIT_FUNC
PyInit__native(void)
{
    import_array();

    PyObject *module = PyModule_Create(&moduledef);

    if (module == NULL)
    {
        return NULL;
    }

    if (PyType_Ready(&EmberFieldType) < 0)
    {
        return NULL;
    }

    Py_INCREF(&EmberFieldType);

    PyModule_AddObject(
        module,
        "EmberField",
        (PyObject *)&EmberFieldType
    );

    return module;
}
