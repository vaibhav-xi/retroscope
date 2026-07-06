#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <math.h>

/* --------------------------------------------------------- */

#define WIDTH 800.0
#define HEIGHT 480.0

/* --------------------------------------------------------- */

static inline float ndc_x(double x)
{
    return (float)(
        (2.0 * x / WIDTH) - 1.0
    );
}

/* --------------------------------------------------------- */

static inline float ndc_y(double y)
{
    return (float)(
        1.0 - (2.0 * y / HEIGHT)
    );
}

/* --------------------------------------------------------- */

static inline void
push_float(
    PyObject *list,
    Py_ssize_t *index,
    float value
)
{
    PyList_SET_ITEM(

        list,

        (*index)++,

        PyFloat_FromDouble(
            value
        )

    );
}

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

    Py_ssize_t count = PyList_Size(
        points
    );

    if (count < 2)
    {
        return PyList_New(0);
    }

    /*
     * Every segment generates:
     *
     * 2 triangles
     * 6 vertices
     * 12 floats
     */

    Py_ssize_t segments = count - 1;

    PyObject *list = PyList_New(
        segments * 12
    );

    Py_ssize_t out = 0;

    for (
        Py_ssize_t i = 0;
        i < segments;
        ++i
    )
    {
        PyObject *p0 = PyList_GetItem(
            points,
            i
        );

        PyObject *p1 = PyList_GetItem(
            points,
            i + 1
        );

        double x1 = PyFloat_AsDouble(
            PyTuple_GetItem(p0, 0)
        );

        double y1 = PyFloat_AsDouble(
            PyTuple_GetItem(p0, 1)
        );

        double x2 = PyFloat_AsDouble(
            PyTuple_GetItem(p1, 0)
        );

        double y2 = PyFloat_AsDouble(
            PyTuple_GetItem(p1, 1)
        );

        double dx = x2 - x1;
        double dy = y2 - y1;

        double length = hypot(
            dx,
            dy
        );

        if (length == 0.0)
        {
            continue;
        }

        double ux = dx / length;
        double uy = dy / length;

        double px = -uy;
        double py =  ux;

        double hw = width;

        double l1x = x1 + px * hw;
        double l1y = y1 + py * hw;

        double r1x = x1 - px * hw;
        double r1y = y1 - py * hw;

        double l2x = x2 + px * hw;
        double l2y = y2 + py * hw;

        double r2x = x2 - px * hw;
        double r2y = y2 - py * hw;

        /*
         * Triangle 1
         */

        push_float(
            list,
            &out,
            ndc_x(l1x)
        );

        push_float(
            list,
            &out,
            ndc_y(l1y)
        );

        push_float(
            list,
            &out,
            ndc_x(r1x)
        );

        push_float(
            list,
            &out,
            ndc_y(r1y)
        );

        push_float(
            list,
            &out,
            ndc_x(l2x)
        );

        push_float(
            list,
            &out,
            ndc_y(l2y)
        );

        /*
         * Triangle 2
         */

        push_float(
            list,
            &out,
            ndc_x(l2x)
        );

        push_float(
            list,
            &out,
            ndc_y(l2y)
        );

        push_float(
            list,
            &out,
            ndc_x(r1x)
        );

        push_float(
            list,
            &out,
            ndc_y(r1y)
        );

        push_float(
            list,
            &out,
            ndc_x(r2x)
        );

        push_float(
            list,
            &out,
            ndc_y(r2y)
        );
    }

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