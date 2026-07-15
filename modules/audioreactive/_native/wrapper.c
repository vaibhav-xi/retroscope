#define PY_SSIZE_T_CLEAN
#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL AUDIOREACTIVE_ARRAY_API
#include <numpy/arrayobject.h>

#include "ember_field.h"
#include "spectrum_ring.h"
#include "burst_field.h"
#include "ring_field.h"
#include "chaos_field.h"
#include "fractal.h"
#include "radial_ring.h"
#include "boid_swarm.h"

static PyMethodDef methods[] =
{
    {
        "spectrum_ring",
        (PyCFunction)spectrum_ring_build,
        METH_VARARGS | METH_KEYWORDS,
        "Build a closed ring polyline from a spectrum array."
    },
    {
        "radial_ring",
        (PyCFunction)radial_ring_build,
        METH_VARARGS | METH_KEYWORDS,
        "Map a radius array onto evenly spaced angles."
    },
    {
        "lightning_bolt",
        (PyCFunction)fractal_lightning_bolt,
        METH_VARARGS | METH_KEYWORDS,
        "Recursive midpoint-displacement jagged bolt."
    },
    {
        "subdivide_triangle",
        (PyCFunction)fractal_subdivide_triangle,
        METH_VARARGS | METH_KEYWORDS,
        "Recursive Sierpinski-style triangle subdivision."
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

    if (PyType_Ready(&EmberFieldType) < 0) return NULL;
    if (PyType_Ready(&BurstFieldType) < 0) return NULL;
    if (PyType_Ready(&RingFieldType) < 0) return NULL;
    if (PyType_Ready(&ChaosFieldType) < 0) return NULL;
    if (PyType_Ready(&BoidSwarmType) < 0) return NULL;

    Py_INCREF(&EmberFieldType);
    PyModule_AddObject(module, "EmberField", (PyObject *)&EmberFieldType);

    Py_INCREF(&BurstFieldType);
    PyModule_AddObject(module, "BurstField", (PyObject *)&BurstFieldType);

    Py_INCREF(&RingFieldType);
    PyModule_AddObject(module, "RingField", (PyObject *)&RingFieldType);

    Py_INCREF(&ChaosFieldType);
    PyModule_AddObject(module, "ChaosField", (PyObject *)&ChaosFieldType);

    Py_INCREF(&BoidSwarmType);
    PyModule_AddObject(module, "BoidSwarm", (PyObject *)&BoidSwarmType);

    return module;
}
