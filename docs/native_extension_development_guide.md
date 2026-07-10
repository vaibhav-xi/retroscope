# 25 - Native Extension Development Guide

Version: 1.0

---

# Introduction

One of Retroscope's defining architectural decisions is that it is **not** purely a Python engine.

Instead, it is a hybrid engine where

- Python owns architecture
- C owns performance

As the project evolved, performance-critical systems were gradually migrated from Python into native C while preserving the exact same public API.

This document explains how to write native extensions that integrate seamlessly into Retroscope.

It is intended for developers who wish to

- optimize existing systems
- add new native objects
- improve performance
- contribute to the rendering backend

---

# Philosophy

The native layer exists for one purpose:

> Execute computationally expensive work without changing the Python architecture.

Python should remain expressive.

C should remain fast.

Neither layer should duplicate the other's responsibilities.

---

# Current Native Architecture

The native renderer lives in

```
render_es2/

└── _native/
```

Current contents

```
_native/

geometry.c

mesh_object.c

shader_object.c

vertex_buffer_object.c

stroke.c

wrapper.c

setup.py

gl_platform.h
```

Each file has one responsibility.

---

# Design Goals

Every native object should

✔ expose a clean Python API

✔ hide OpenGL

✔ own its resources

✔ support macOS

✔ support Raspberry Pi

✔ minimize allocations

✔ avoid unnecessary Python interaction

---

# Python ↔ C Boundary

Python should only call high-level methods.

Example

```python
mesh.draw()
```

Python should never care whether

```
draw()

↓

OpenGL

↓

Metal

↓

Vulkan
```

The implementation remains hidden.

---

# Public API Stability

One of the most important goals is

```
Python API

↓

Never Changes
```

Internals may evolve indefinitely.

---

# Current Native Objects

Retroscope currently exposes

```
VertexBuffer

Mesh

Shader
```

Each appears to Python as a normal object.

---

# Object Ownership

Each native object owns exactly one concept.

Example

```
Mesh

↓

VAO

↓

VBO

↓

Vertex Count
```

Nothing more.

---

# Python Object Layout

Every object begins with

```c
typedef struct
{
    PyObject_HEAD

} ExampleObject;
```

Additional fields follow.

Example

```c
GLuint program;

GLint color_location;
```

---

# PyTypeObject

Every native class is registered using

```c
PyTypeObject
```

Example

```c
PyTypeObject ShaderType =
{
    ...
};
```

This defines the Python-visible class.

---

# Initialization

Constructors use

```c
tp_init
```

Example

```c
static int

Shader_init(...)
```

This should initialize

- handles
- counters
- pointers

Never allocate GPU resources unless required.

---

# Resource Creation

Heavy resources should usually be created explicitly.

Example

```python
shader.create(...)
```

rather than inside

```
tp_init
```

This ensures a valid OpenGL context exists.

---

# Deallocation

GPU resources belong to the object.

When destroyed

```
Mesh

↓

Delete VBO

↓

Delete VAO
```

Then

```
tp_free()
```

---

# Python Methods

Methods are exposed through

```c
PyMethodDef
```

Example

```c
{

    "draw",

    ...

}
```

These become

```python
mesh.draw()
```

---

# Python Members

Public fields use

```c
PyMemberDef
```

Example

```c
vertex_count
```

Readable from Python.

---

# Hidden Members

Implementation details should remain private.

Avoid exposing

```
GLuint*

Pointers

Temporary buffers
```

unless absolutely necessary.

---

# Error Handling

Never

```
printf()

return NULL
```

Instead

```c
PyErr_SetString(...)
```

This propagates correctly into Python exceptions.

---

# OpenGL Errors

OpenGL failures should become Python exceptions whenever possible.

Example

```
Shader Compilation

↓

RuntimeError
```

This greatly simplifies debugging.

---

# File Organization

Every object should have

```
example_object.c

example_object.h
```

Avoid large monolithic files.

---

# Wrapper

```
wrapper.c
```

is responsible for

- module creation
- registering types
- exported functions

Nothing more.

---

# Registering Objects

Typical flow

```
PyType_Ready()

↓

Py_INCREF()

↓

PyModule_AddObject()
```

Every exported type follows this pattern.

---

# Platform Layer

All OpenGL portability belongs inside

```
gl_platform.h
```

No platform-specific OpenGL code should appear elsewhere.

---

# Why gl_platform.h Exists

macOS

↓

Desktop OpenGL

Raspberry Pi

↓

OpenGL ES

Different APIs.

One abstraction layer.

---

# Example

Current abstraction

```
glGenVertexArrays

↓

glGenVertexArraysOES

↓

OpenGL ES
```

Platform differences disappear from engine code.

---

# Avoid Platform Checks

Never scatter

```c
#ifdef __APPLE__
```

throughout object implementations.

Keep them centralized.

---

# Memory Ownership

Every allocation must have one owner.

Example

```
VertexBuffer

↓

malloc()

↓

free()
```

No shared ownership.

---

# Allocation Strategy

Prefer

```
Reserve

↓

Reuse

↓

Grow Occasionally
```

Avoid

```
malloc()

↓

free()

↓

malloc()
```

every frame.

---

# Python Interaction

Minimize transitions between Python and C.

One large native call is almost always preferable to thousands of tiny ones.

---

# Native Algorithms

Good candidates

- tessellation
- FFT
- particles
- interpolation
- buffer generation

Poor candidates

- scene graph
- module logic
- application flow

---

# OpenGL Ownership

Eventually every OpenGL call should exist inside native code.

Python should describe

```
What
```

Native code decides

```
How
```

---

# Debugging

Useful tools

```
printf()

fflush()

PyErr_SetString()

assert()
```

Keep debug output temporary.

---

# Testing

Every native object should have

```
test_mesh.py

test_shader.py

...
```

Small focused tests are much easier to debug than the entire engine.

---

# Incremental Porting

The preferred workflow is

```
Python Version

↓

Native Prototype

↓

API Compatibility

↓

Replace Python

↓

Delete Old Code
```

This keeps the engine operational throughout development.

---

# API Compatibility

The Python interface should remain identical.

Example

Old

```python
shader.use()
```

New

```python
shader.use()
```

Internals change.

Call sites do not.

---

# When Should Something Move To C?

Ask

Is it

✔ CPU intensive?

✔ Called every frame?

✔ Allocation heavy?

✔ Memory intensive?

✔ Easily isolated?

If yes,

it is probably a good native candidate.

---

# When Should It Stay In Python?

Keep systems in Python if they involve

- architecture
- orchestration
- module logic
- scene construction
- configuration
- readability

Premature native code makes maintenance harder.

---

# Coding Style

Every native object should

✔ have one responsibility

✔ expose minimal APIs

✔ own its resources

✔ avoid global state

✔ clean up after itself

---

# Common Mistakes

Avoid

Multiple ownership

Hidden allocations

Platform-specific code

Duplicated APIs

Large wrapper functions

OpenGL calls from Python

---

# Future Native Objects

Likely future additions

```
Framebuffer

Texture

RenderPass

FFT

Particle Engine

Noise

Spatial Grid

Instancing

Compute Helpers
```

Each should follow the same architecture as existing native objects.

---

# Mental Model

Think of each native object as a hardware driver.

Python issues high-level requests.

The driver performs the complex work efficiently.

Python should never know how the driver works internally.

---

# Summary

The native extension layer is responsible for the performance-critical core of Retroscope.

It encapsulates OpenGL interaction, memory management, geometry generation, and GPU resources behind stable Python APIs. By carefully separating architecture from implementation, the engine gains the performance of native code without sacrificing the flexibility and readability of Python.

When extending the native layer, always preserve the existing public API, keep responsibilities narrowly focused, and isolate platform-specific behavior behind common abstractions. This approach has allowed Retroscope to evolve from a pure Python renderer into a high-performance hybrid engine while remaining pleasant to develop and easy to extend.