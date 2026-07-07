#include "vertex_buffer.h"

#include <numpy/arrayobject.h>

float *
vertex_buffer_begin(
    PyObject *vertex_buffer,
    int additional,
    int *old_count
)
{
    PyObject *count_obj =
        PyObject_GetAttrString(
            vertex_buffer,
            "count"
        );

    if (count_obj == NULL)
    {
        return NULL;
    }

    *old_count =
        (int)PyLong_AsLong(
            count_obj
        );

    Py_DECREF(
        count_obj
    );

    PyObject *reserve =
        PyObject_CallMethod(
            vertex_buffer,
            "reserve",
            "i",
            *old_count + additional
        );

    if (reserve == NULL)
    {
        return NULL;
    }

    Py_DECREF(
        reserve
    );

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

    /*
     * We intentionally leak one reference here.
     *
     * vertex_buffer_finish()
     * will fetch the array again and DECREF it.
     *
     * This keeps wrapper.c very simple.
     */

    PyArrayObject *vertex_array =
        (PyArrayObject *)array;

    float *vertices =
        (float *)PyArray_DATA(
            vertex_array
        );

    return vertices + *old_count;
}

int
vertex_buffer_finish(
    PyObject *vertex_buffer,
    int new_count
)
{
    PyObject *result =
        PyObject_CallMethod(
            vertex_buffer,
            "set_count",
            "i",
            new_count
        );

    if (result == NULL)
    {
        return 0;
    }

    Py_DECREF(
        result
    );

    /*
     * Balance the reference created
     * by vertex_buffer_begin().
     */

    PyObject *array =
        PyObject_CallMethod(
            vertex_buffer,
            "data",
            NULL
        );

    if (array != NULL)
    {
        Py_DECREF(
            array
        );
    }

    return 1;
}