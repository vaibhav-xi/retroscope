#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <numpy/arrayobject.h>

#include "stroke.h"

#include "vertex_buffer_object.h"

#include "mesh_object.h"

#include "shader_object.h"

#include "gl_platform.h"

/*
 * init_gl()
 *
 * Loads OpenGL >1.1 entry points via wglGetProcAddress() on
 * Windows. No-op on macOS/Linux/Pi, where these are already
 * statically linked. Must be called once, right after the GL
 * context is created and made current (Window.__init__ does
 * this), before any Mesh/Shader object is used.
 */

static PyObject *
native_init_gl(
    PyObject *Py_UNUSED(self),
    PyObject *Py_UNUSED(args)
)
{
#ifdef _WIN32
    gl_platform_init();
#endif

    Py_RETURN_NONE;
}

static PyObject *
build(
    PyObject *self,
    PyObject *args
)
{
    PyArrayObject *points_array;
    double width;
    double screen_width;
    double screen_height;

    PyObject *vertex_buffer_obj;
    VertexBufferObject *vertex_buffer;

    PyObject *points;

    if (!PyArg_ParseTuple(
        args,
        "OdOdd",
        &points,
        &width,
        &vertex_buffer_obj,
        &screen_width,
        &screen_height))
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
            (float)screen_width,
            (float)screen_height,
            vertices
        );

    vertex_buffer->count =
        old_count + written;

    Py_DECREF(points_array);

    Py_RETURN_NONE;
}

/* --------------------------------------------------------- */

/*
 * build_many(polylines, width, vertex_buffer)
 *
 * Same as build(), but for a whole sequence of point arrays at
 * once. Reserves capacity for the entire batch up front (one
 * grow instead of one per primitive) and does a single Python/C
 * transition instead of one per primitive. Intended for
 * renderables that add hundreds of small polylines per frame
 * (dash fields, particle fans, etc).
 */

static PyObject *
build_many(
    PyObject *self,
    PyObject *args
)
{
    PyObject *polylines;
    double width;
    double screen_width;
    double screen_height;

    PyObject *vertex_buffer_obj;
    VertexBufferObject *vertex_buffer;

    if (!PyArg_ParseTuple(
        args,
        "OdOdd",
        &polylines,
        &width,
        &vertex_buffer_obj,
        &screen_width,
        &screen_height))
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

    if (!PySequence_Check(polylines))
    {
        PyErr_SetString(
            PyExc_TypeError,
            "expected a sequence of point arrays"
        );

        return NULL;
    }

    Py_ssize_t polyline_count =
        PySequence_Size(polylines);

    if (polyline_count < 0)
    {
        return NULL;
    }

    if (polyline_count == 0)
    {
        Py_RETURN_NONE;
    }

    PyArrayObject **arrays =
        (PyArrayObject **)PyMem_Malloc(
            sizeof(PyArrayObject *) * (size_t)polyline_count
        );

    if (arrays == NULL)
    {
        PyErr_NoMemory();
        return NULL;
    }

    /*
     * First pass: convert every entry to a contiguous float32
     * array and compute the total capacity needed, so the vertex
     * buffer grows (at most) once for the whole batch.
     */

    int total_max_floats = 0;

    for (Py_ssize_t i = 0; i < polyline_count; ++i)
    {
        PyObject *item =
            PySequence_GetItem(polylines, i);

        if (item == NULL)
        {
            for (Py_ssize_t j = 0; j < i; ++j)
                Py_DECREF(arrays[j]);

            PyMem_Free(arrays);
            return NULL;
        }

        PyArrayObject *array =
            (PyArrayObject *)PyArray_FROM_OTF(
                item,
                NPY_FLOAT32,
                NPY_ARRAY_IN_ARRAY
            );

        Py_DECREF(item);

        if (array == NULL)
        {
            for (Py_ssize_t j = 0; j < i; ++j)
                Py_DECREF(arrays[j]);

            PyMem_Free(arrays);
            return NULL;
        }

        arrays[i] = array;

        int point_count =
            (int)PyArray_DIM(array, 0);

        if (point_count >= 2)
        {
            total_max_floats +=
                (point_count - 1) * 12;
        }
    }

    int old_count = vertex_buffer->count;

    if (!vertex_buffer_reserve(
            vertex_buffer,
            old_count + total_max_floats))
    {
        for (Py_ssize_t i = 0; i < polyline_count; ++i)
            Py_DECREF(arrays[i]);

        PyMem_Free(arrays);
        return NULL;
    }

    float *cursor =
        vertex_buffer_data(vertex_buffer) + old_count;

    int written_total = 0;

    for (Py_ssize_t i = 0; i < polyline_count; ++i)
    {
        PyArrayObject *array = arrays[i];

        int point_count =
            (int)PyArray_DIM(array, 0);

        if (point_count >= 2)
        {
            float *packed_points =
                (float *)PyArray_DATA(array);

            int written =
                stroke_build(
                    packed_points,
                    point_count,
                    (float)(width * 0.5f),
                    (float)screen_width,
                    (float)screen_height,
                    cursor
                );

            cursor += written;
            written_total += written;
        }

        Py_DECREF(array);
    }

    PyMem_Free(arrays);

    vertex_buffer->count =
        old_count + written_total;

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
        "build_many",
        build_many,
        METH_VARARGS,
        ""
    },

    {
        "init_gl",
        native_init_gl,
        METH_NOARGS,
        "Load OpenGL entry points on Windows (no-op elsewhere)."
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

    if (PyType_Ready(&ShaderType) < 0)
        return NULL;

    Py_INCREF(&MeshType);

    PyModule_AddObject(
        module,
        "Mesh",
        (PyObject *)&MeshType
    );

    Py_INCREF(&ShaderType);

    PyModule_AddObject(
        module,
        "Shader",
        (PyObject *)&ShaderType
    );

    Py_INCREF(&VertexBufferType);

    PyModule_AddObject(
        module,
        "VertexBuffer",
        (PyObject *)&VertexBufferType
    );

    return module;
}
