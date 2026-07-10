# 10 - Mesh API

Version: 1.0

---

# Introduction

The **Mesh** is the final CPU object before geometry reaches the GPU.

Unlike Geometry, which describes *what should exist*, a Mesh contains GPU-ready vertex data and the OpenGL objects required to render it.

Conceptually

```
Geometry

↓

Geometry Builder

↓

Vertex Buffer

↓

Mesh

↓

Renderer

↓

GPU
```

Every Renderable owns exactly one Mesh.

Modules almost never interact with Mesh directly.

---

# Philosophy

The Mesh exists to hide GPU management from visualization modules.

A module should never need to know

- VBOs
- VAOs
- glBindBuffer()
- glVertexAttribPointer()
- glDrawArrays()

Instead, the renderer manages those details through Mesh.

This separation is one of the major architectural goals of Retroscope.

---

# Ownership

Mesh ownership is straightforward.

```
Module

↓

Renderable

↓

Mesh
```

The renderer updates the Mesh.

The module never does.

---

# Lifetime

Meshes are persistent.

Typical lifetime

```
Renderable Created

↓

Mesh Created

↓

GPU Upload

↓

GPU Upload

↓

GPU Upload

↓

Destroyed
```

The same Mesh normally lives for the lifetime of its Renderable.

---

# Current Native Implementation

Unlike most engine objects,

Mesh is implemented entirely in native C.

```
render_es2/_native/

mesh_object.c

mesh_object.h
```

This avoids Python overhead around OpenGL.

---

# Internal Structure

Conceptually

```
Mesh

├── vao

├── vbo

└── vertex_count
```

These members correspond almost directly to GPU resources.

---

# vao

```
GLuint vao
```

Represents the Vertex Array Object.

The VAO stores

- vertex attribute configuration
- enabled attributes
- bound VBO layout

This means vertex layout only needs to be configured once.

---

# vbo

```
GLuint vbo
```

Represents the Vertex Buffer Object.

The renderer uploads triangle vertices into this buffer.

Modules never access it directly.

---

# vertex_count

```
int vertex_count
```

Number of vertices currently stored inside the VBO.

Example

```
6
```

represents

```
2 triangles
```

The renderer uses this during

```
glDrawArrays()
```

---

# Native API

Current native Mesh exposes methods similar to

```python
mesh.create()

mesh.draw()
```

These methods are thin wrappers around OpenGL.

---

# Mesh Creation

During initialization

```
Mesh()

↓

create()

↓

glGenBuffers()

↓

glGenVertexArrays()

↓

Ready
```

This only occurs once.

---

# GPU Upload

The Geometry Builder generates vertices into a native VertexBuffer.

The renderer later performs

```
VertexBuffer

↓

Mesh Upload

↓

GPU
```

The Mesh itself never generates geometry.

---

# Draw

Rendering is extremely small.

Conceptually

```
Bind VAO

↓

Draw Arrays
```

Everything else has already been configured.

---

# Why Native?

Previous versions of Retroscope performed

```
glBindBuffer()

glEnableVertexAttribArray()

glVertexAttribPointer()

glDrawArrays()
```

through PyOpenGL.

This incurred Python overhead every draw call.

Moving Mesh into C significantly reduces this cost.

---

# Python Wrapper

Today's Python wrapper is intentionally tiny.

Conceptually

```python
class Mesh:

    def __init__(self):

        self.native = NativeMesh()
```

Almost every operation forwards directly to native code.

---

# Responsibilities

Mesh is responsible for

- owning GPU buffers
- configuring vertex attributes
- drawing triangles

Mesh is **not** responsible for

- geometry generation
- simulation
- materials
- transforms

---

# Relationship with Geometry

Geometry lives on the CPU.

Mesh lives on the GPU.

```
Geometry

↓

Builder

↓

Mesh
```

Once uploaded,

the Mesh contains only triangles.

The original Geometry remains unchanged.

---

# Relationship with VertexBuffer

The VertexBuffer is temporary.

```
Geometry

↓

VertexBuffer

↓

Mesh
```

After upload,

the VertexBuffer may be reused.

The Mesh owns the persistent GPU copy.

---

# Relationship with Renderable

Renderable owns exactly one Mesh.

```
Renderable

↓

Mesh
```

The renderer asks

```
renderable.mesh.draw()
```

during rendering.

Modules never call this.

---

# Dirty Updates

Current pipeline

```
Geometry Changed

↓

Renderable Dirty

↓

Geometry Builder

↓

VertexBuffer

↓

Mesh Upload

↓

Clean
```

No upload occurs if the Renderable is already clean.

---

# Static Geometry

Static objects

```
Grid

Logo

Frame
```

Upload once.

Reuse forever.

This minimizes GPU traffic.

---

# Dynamic Geometry

Waveforms

Particles

Audio

These rebuild frequently.

The Mesh remains.

Only its contents change.

---

# VAO Abstraction

Historically,

Retroscope had

```
vao.py
```

implemented in Python.

After the native renderer migration,

VAO management moved into Mesh.

This simplified the Python renderer considerably.

---

# Platform Differences

Desktop OpenGL

```
glGenVertexArrays()
```

OpenGL ES

```
glGenVertexArrays()

or

glGenVertexArraysOES()
```

These differences are hidden inside

```
gl_platform.h
```

Modules never see platform-specific code.

---

# Raspberry Pi Compatibility

One important design goal was identical behavior across

- macOS
- Raspberry Pi
- future Linux systems

The Mesh implementation hides

- OpenGL ES differences
- VAO extension handling
- function naming

behind one interface.

---

# Memory Ownership

Ownership hierarchy

```
Renderable

↓

Mesh

↓

VAO

↓

VBO
```

Destroying a Renderable automatically destroys its Mesh.

Destroying the Mesh releases GPU resources.

---

# Destruction

During cleanup

```
Mesh

↓

glDeleteBuffers()

↓

glDeleteVertexArrays()
```

No manual cleanup is required by modules.

---

# Performance

Mesh was one of the largest rendering optimizations.

Benefits include

- fewer Python calls
- fewer ctypes conversions
- direct C OpenGL calls
- persistent GPU resources

Combined with the native Stroke Builder,

this significantly increased frame rate on Raspberry Pi.

---

# Current Responsibilities

Today Mesh performs

✔ VAO creation

✔ VBO creation

✔ GPU uploads

✔ Attribute configuration

✔ Draw calls

---

# Future Responsibilities

Future versions may additionally support

- indexed rendering
- instancing
- multiple vertex streams
- dynamic buffer growth
- persistent mapped buffers
- indirect drawing

The public Mesh API is already compatible with these additions.

---

# Best Practices

Modules should

✔ Ignore Mesh entirely.

✔ Work with Geometry.

✔ Mark Renderables dirty.

✔ Let the renderer manage Mesh updates.

---

# Anti-Patterns

Never

```python
mesh.draw()
```

inside a module.

Never

```python
mesh.create()
```

Never

```python
glBindBuffer(...)
```

Never

```python
glBufferData(...)
```

These are renderer responsibilities.

---

# Mental Model

Imagine Geometry as a CAD drawing.

The Mesh is the finished manufactured part stored in a warehouse.

The renderer simply retrieves the part and assembles it into the final image.

Modules never enter the warehouse.

They only create the blueprint.

---

# Example Pipeline

A waveform follows this path.

```
Wave Module

↓

Polyline

↓

Geometry

↓

Stroke Builder

↓

VertexBuffer

↓

Mesh Upload

↓

GPU

↓

Draw
```

The module itself only creates the Polyline.

Everything after that happens automatically.

---

# Summary

The Mesh is Retroscope's GPU representation of a Renderable.

Implemented entirely in native C, it owns the OpenGL objects required for rendering while hiding platform-specific details from the rest of the engine.

Modules never manipulate Meshes directly. Instead, they generate Geometry, mark Renderables dirty, and allow the renderer to rebuild and update Meshes as needed.

This separation keeps visualization code clean while enabling high-performance rendering across desktop OpenGL and OpenGL ES platforms.