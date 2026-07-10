#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <numpy/arrayobject.h>

#include "stroke.h"

#include "vertex_buffer_object.h"
#include "gl_upload.h"

#include "mesh_object.h"

static PyObject *
build(
    PyObject *self,
    PyObject *args
)
{
    PyArrayObject *points_array;
    double width;

    PyObject *vertex_buffer_obj;
    VertexBufferObject *vertex_buffer;

    PyObject *points;

    if (!PyArg_ParseTuple(
        args,
        "OdO",
        &points,
        &width,
        &vertex_buffer_obj))
    {
        return NULL;
    }

    if (!PyObject_TypeCheck(
            vertex_buffer_obj,
            &VertexBufferType))
    {
        PyErr_SetString(
            PyExc_TypeError,
            "expected VertexBuffer"
        );

        return NULL;
    }

    vertex_buffer =
        (VertexBufferObject *)
            vertex_buffer_obj;

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

    int old_count =
        vertex_buffer->count;

    if (!vertex_buffer_reserve(
            vertex_buffer,
            old_count + max_floats))
    {
        Py_DECREF(points_array);
        return NULL;
    }

    float *vertices =
        vertex_buffer_data(
            vertex_buffer
        ) + old_count;

    int written =
        stroke_build(
            packed_points,
            point_count,
            (float)(width * 0.5f),
            vertices
        );

    vertex_buffer->count =
        old_count + written;

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

    {
        "gl_upload",
        gl_upload,
        METH_VARARGS,
        ""
    },

    {NULL, NULL, 0, NULL}
};

/* --------------------------------------------------------- */

static struct PyModuleDef moduledef = {

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

    PyObject *module =
        PyModule_Create(&moduledef);

    if (module == NULL)
        return NULL;

    if (PyType_Ready(&MeshType) < 0)
        return NULL;

    if (PyType_Ready(&VertexBufferType) < 0)
        return NULL;

    Py_INCREF(&MeshType);

    PyModule_AddObject(
        module,
        "Mesh",
        (PyObject *)&MeshType
    );

    Py_INCREF(&VertexBufferType);

    PyModule_AddObject(
        module,
        "VertexBuffer",
        (PyObject *)&VertexBufferType
    );

    return module;
}