# docs/reference/native_object_lifecycle.md

# Native Object Lifecycle

Version: 1.0

---

# Introduction

Retroscope is a hybrid Python/C rendering engine.

From the perspective of a visualization module, rendering appears extremely simple.

```python
mesh.draw()
```

Behind that single line, however, a considerable amount of work occurs across multiple layers of the engine.

Understanding this lifecycle is essential for anyone contributing to the native renderer.

This document traces the complete journey of an object from Python to the GPU and back again.

---

# The Big Picture

A typical rendering path looks like this.

```
Python Module

↓

Renderable

↓

Geometry

↓

Geometry Builder

↓

Vertex Buffer

↓

Mesh

↓

Shader

↓

OpenGL

↓

GPU
```

Each stage owns exactly one responsibility.

---

# Object Ownership

One of the core principles of the engine is

> Every resource has exactly one owner.

Example

```
VertexBuffer

↓

float memory
```

```
Mesh

↓

VAO

↓

VBO
```

```
Shader

↓

Program Object
```

Ownership is never ambiguous.

---

# Python Object Creation

Everything begins in Python.

Example

```python
mesh = Mesh()
```

This creates a Python object.

Internally

```
PyObject

↓

MeshObject
```

The Python object is only a wrapper.

---

# PyObject

Every native type begins with

```c
PyObject_HEAD
```

Example

```c
typedef struct
{
    PyObject_HEAD

    ...

} MeshObject;
```

This allows Python to manage

- reference counting
- type information
- lifetime

---

# tp_new

Creation begins with

```
PyType_GenericNew
```

Memory is allocated.

Nothing GPU-related exists yet.

---

# tp_init

Immediately afterwards

```
tp_init
```

runs.

Example

```
Mesh_init()
```

Typical responsibilities

- initialize fields
- zero handles
- initialize pointers

Avoid expensive work here.

---

# Explicit Resource Creation

Retroscope prefers

```python
mesh.create(...)
```

instead of allocating GPU resources inside

```
tp_init
```

Reasons

- explicit lifetime
- valid OpenGL context
- easier debugging

---

# Geometry Generation

Modules never create GPU vertices.

Instead

```
Polyline

↓

Geometry Builder

↓

Vertex Array
```

The Geometry Builder converts mathematical descriptions into triangles.

---

# Vertex Buffer

Generated vertices are copied into

```
VertexBufferObject
```

Conceptually

```
float*

↓

malloc()

↓

VertexBuffer
```

The buffer owns this memory.

---

# Mesh Upload

The Mesh uploads the vertex buffer.

```
CPU

↓

glBufferData()

↓

GPU
```

From this point,

rendering uses GPU memory.

---

# VAO

Desktop OpenGL

```
VAO

↓

VBO

↓

Vertex Format
```

OpenGL ES

```
VAO

↓

gl_platform.h

↓

Platform Abstraction
```

The engine hides platform differences.

---

# Shader Compilation

Shader lifecycle

```
Source

↓

Compile Vertex Shader

↓

Compile Fragment Shader

↓

Link Program

↓

Program Handle
```

Compilation occurs once.

---

# Uniform Discovery

Immediately after linking

```
glGetUniformLocation()
```

stores frequently used uniform locations.

Example

```
u_color
```

Avoid repeated lookups during rendering.

---

# Rendering

Rendering becomes

```
Use Program

↓

Bind VAO

↓

Draw Arrays
```

The renderer coordinates these operations.

Modules never see them.

---

# GPU Execution

After

```
glDrawArrays()
```

the GPU executes independently.

The CPU continues preparing future work.

---

# Persistent Objects

The ideal lifecycle

```
Startup

↓

Create

↓

Upload

↓

Draw

↓

Draw

↓

Draw

↓

Destroy
```

Notice that upload occurs only once.

---

# Temporary Objects

Avoid

```
Create

↓

Upload

↓

Destroy
```

every frame.

GPU allocation is expensive.

---

# Dirty Flag Flow

Good

```
Geometry Changes

↓

Renderable Dirty

↓

Rebuild Mesh

↓

Clear Dirty Flag
```

Nothing happens if geometry remains unchanged.

---

# Material Changes

Material changes should not rebuild geometry.

Instead

```
Material

↓

Uniform Update

↓

Draw
```

Geometry remains cached.

---

# Transform Changes

Similarly

```
Transform

↓

Matrix Update

↓

Draw
```

No vertex generation required.

---

# Resource Destruction

Eventually

```python
del mesh
```

or reference count reaches zero.

Python calls

```
tp_dealloc
```

---

# tp_dealloc

Typical cleanup

```
Delete VBO

↓

Delete VAO

↓

Free Memory

↓

Python Object
```

Every allocation must be released.

---

# Reference Counting

Python manages

```
Py_INCREF()

↓

Py_DECREF()
```

Native objects should cooperate with Python's ownership model.

---

# Native Memory

Native allocations

```
malloc()

↓

free()
```

must remain balanced.

Never assume Python will free native memory automatically.

---

# GPU Memory

GPU resources require explicit cleanup.

Examples

```
glDeleteBuffers()

glDeleteProgram()

glDeleteVertexArrays()
```

Failure results in GPU leaks.

---

# Platform Abstraction

All platform differences belong here.

```
gl_platform.h
```

Examples

```
macOS

↓

Desktop OpenGL
```

```
Raspberry Pi

↓

OpenGL ES
```

Every other source file should remain platform agnostic.

---

# Error Propagation

Errors flow upward.

```
OpenGL Failure

↓

Native Code

↓

PyErr_SetString()

↓

Python Exception
```

Never silently ignore failures.

---

# Lifetime Summary

Complete lifecycle

```
Python Object

↓

tp_new

↓

tp_init

↓

Create Resources

↓

Generate Geometry

↓

Upload

↓

Draw

↓

Reuse

↓

tp_dealloc

↓

GPU Cleanup

↓

Memory Free
```

This sequence applies to nearly every native object inside Retroscope.

---

# Native Objects Today

Current native objects

```
Mesh

Shader

VertexBuffer

Stroke Builder
```

All follow the same lifecycle.

Future objects should do likewise.

---

# Future Objects

Likely additions

```
Framebuffer

Texture

Particle Buffer

FFT

Render Pass

Instancing
```

Each should follow the ownership model established by the existing engine.

---

# Mental Model

Imagine a shipping company.

Python creates the shipping order.

The Geometry Builder packs the boxes.

The Vertex Buffer loads the truck.

The Mesh drives to the port.

The Shader tells the crane where to unload.

The GPU performs the heavy lifting.

Each participant performs one specialized task.

No participant attempts to do everyone else's job.

That separation is exactly what makes the architecture scalable.

---

# Summary

The native object lifecycle is built around explicit ownership, persistent resources, and clear separation of responsibilities. Python creates and orchestrates objects, native code owns performance-critical resources, and the GPU executes rendering commands. By ensuring that every resource has a well-defined lifetime—from allocation to cleanup—Retroscope achieves both high performance and long-term maintainability while preserving a simple, stable Python API for visualization developers.