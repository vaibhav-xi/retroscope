#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "mesh_object.h"

#include <structmember.h>

#include "vertex_buffer_object.h"

static int
Mesh_init(
    MeshObject *self,
    PyObject *args,
    PyObject *kwds
)
{
    // printf("Mesh_init\n");
    // fflush(stdout);

    self->vbo = 0;
    self->vertex_count = 0;

    return 0;
}

static PyObject *
Mesh_create(
    MeshObject *self,
    PyObject *Py_UNUSED(ignored)
)
{
    if (self->vbo == 0)
    {
        glGenBuffers(
            1,
            &self->vbo
        );
    }

    self->vertex_count = 0;

    Py_RETURN_NONE;
}

static PyObject *
Mesh_upload(
    MeshObject *self,
    PyObject *args
)
{
    PyObject *obj;

    if (!PyArg_ParseTuple(
            args,
            "O",
            &obj))
    {
        return NULL;
    }

    if (!PyObject_TypeCheck(
            obj,
            &VertexBufferType))
    {
        PyErr_SetString(
            PyExc_TypeError,
            "expected VertexBuffer"
        );

        return NULL;
    }

    VertexBufferObject *vb =
        (VertexBufferObject *)obj;

    self->vertex_count =
        vb->count / 2;

    glBindBuffer(
        GL_ARRAY_BUFFER,
        self->vbo
    );

    glBufferData(
        GL_ARRAY_BUFFER,
        vb->count * sizeof(float),
        vb->vertices,
        GL_DYNAMIC_DRAW
    );

    Py_RETURN_NONE;
}

static PyObject *
Mesh_test(
    MeshObject *self,
    PyObject *Py_UNUSED(args)
)
{
    printf("test\n");
    fflush(stdout);

    Py_RETURN_NONE;
}

static PyObject *
Mesh_draw(
    MeshObject *self,
    PyObject *Py_UNUSED(ignored)
)
{
    if (self->vertex_count == 0)
    {
        Py_RETURN_NONE;
    }

    glBindBuffer(
        GL_ARRAY_BUFFER,
        self->vbo
    );

    glEnableVertexAttribArray(0);

    glVertexAttribPointer(

        0,

        2,

        GL_FLOAT,

        GL_FALSE,

        0,

        0

    );

    glDrawArrays(

        GL_TRIANGLES,

        0,

        self->vertex_count

    );

    Py_RETURN_NONE;
}

static PyMethodDef Mesh_methods[] =
{
    {
        "create",
        (PyCFunction)Mesh_create,
        METH_NOARGS,
        NULL
    },

    {
        "upload",
        (PyCFunction)Mesh_upload,
        METH_VARARGS,
        NULL
    },

    {
        "draw",
        (PyCFunction)Mesh_draw,
        METH_NOARGS,
        NULL
    },


    {
        "test",
        (PyCFunction)Mesh_test,
        METH_NOARGS,
        NULL
    },
    {NULL, NULL, 0, NULL}
};

static void
Mesh_dealloc(
    MeshObject *self
)
{
    // printf("Mesh_dealloc\n");
    // fflush(stdout);

    Py_TYPE(self)->tp_free(
        (PyObject *)self
    );
}

static PyMemberDef Mesh_members[] =
{
    {
        "vbo",
        T_UINT,
        offsetof(MeshObject, vbo),
        READONLY,
        NULL
    },

    {
        "vertex_count",
        T_INT,
        offsetof(MeshObject, vertex_count),
        0,
        NULL
    },

    {NULL}
};

PyTypeObject MeshType =
{
    PyVarObject_HEAD_INIT(NULL, 0)

    .tp_init = (initproc)Mesh_init,
    .tp_name = "_native.Mesh",
    .tp_basicsize = sizeof(MeshObject),
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
    .tp_dealloc = (destructor)Mesh_dealloc,
    .tp_methods = Mesh_methods,
    .tp_members = Mesh_members,
};