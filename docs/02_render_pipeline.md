# 02 - Render Pipeline

# Introduction

The render pipeline is responsible for transforming high-level procedural geometry into pixels on the display.

Modules never interact with this pipeline directly.

Instead, modules generate logical geometry, and the renderer performs every step required to convert that geometry into GPU commands.

The entire pipeline has been designed around one principle:

> **Each stage has exactly one responsibility.**

No stage performs work that belongs to another.

---

# Complete Pipeline

Every frame follows the same path.

```
main.py

↓

App

↓

ModuleManager

↓

Modules

↓

Frame

↓

Renderables

↓

GeometryBuilder

↓

Geometry

↓

StrokeBuilder (native)

↓

VertexBuffer (native)

↓

Mesh (native)

↓

Shader (native)

↓

OpenGL

↓

GPU

↓

Framebuffer

↓

Display
```

This pipeline executes approximately 60 times every second.

---

# Stage 1 — Application

The application owns the main loop.

Responsibilities include:

- creating the OpenGL context
- polling input
- updating modules
- rendering the current frame
- swapping buffers

Simplified:

```python
while running:

    update()

    render()
```

Nothing graphical is generated here.

---

# Stage 2 — Module Update

Every active module updates itself.

Example:

```
Wave

↓

advance phase

↓

update samples
```

or

```
Snow

↓

move particles

↓

remove dead particles

↓

spawn new particles
```

No geometry is produced yet.

Only simulation state changes.

---

# Stage 3 — Frame Construction

After every module updates:

```
Frame()

↓

empty
```

Every module receives this Frame.

Example:

```
Wave.build(frame)

↓

Grid.build(frame)

↓

Overlay.build(frame)

↓

Particles.build(frame)
```

Each module contributes Renderables.

---

# Stage 4 — Renderables

A Renderable represents one drawable object.

A Renderable combines:

```
Geometry

+

Material

+

Transform
```

Nothing GPU-related exists yet.

Example:

```
Renderable

Geometry:
    Polyline

Material:
    Green

Transform:
    Identity
```

---

# Stage 5 — Geometry Builder

The renderer receives the completed Frame.

```
Frame

↓

GeometryBuilder
```

Its responsibility is to convert logical geometry into vertex data.

Examples:

```
Polyline

↓

Stroke Builder

↓

Triangles
```

or

```
Circle

↓

Approximate Circle

↓

Polyline

↓

Triangles
```

Every logical primitive eventually becomes triangles.

---

# Stage 6 — Stroke Builder

The Stroke Builder is implemented in native C.

Input:

```
points

+

line width
```

Output:

```
triangle vertices
```

For example:

```
A────B
```

becomes

```
╱────╲

╲────╱
```

Two triangles.

For long polylines this becomes thousands of triangles.

Doing this in C is significantly faster than Python.

---

# Stage 7 — Vertex Buffer

The generated triangles are written into a native VertexBuffer.

The VertexBuffer owns:

```
float*

capacity

count
```

Its memory is reused every frame.

Instead of allocating new memory continuously:

```
malloc

free

malloc

free
```

the buffer simply grows when needed.

Typical workflow:

```
clear()

↓

reserve()

↓

append()

↓

upload()
```

---

# Memory Layout

Vertices are stored as packed floats.

Example:

```
x0

y0

x1

y1

x2

y2
```

Internally:

```
float vertices[]

↓

[x,y,x,y,x,y,...]
```

No Python objects exist inside this buffer.

Only raw memory.

---

# Stage 8 — Mesh

The Mesh owns GPU resources.

Specifically:

```
VAO

VBO

vertex count
```

Unlike VertexBuffer, Mesh lives on the GPU.

Responsibilities:

```
upload()

bind()

draw()
```

The Mesh knows nothing about geometry.

It only knows about vertices.

---

# GPU Upload

When geometry changes:

```
VertexBuffer

↓

glBufferData()

↓

GPU memory
```

This happens entirely inside native C.

Python never uploads vertices.

---

# Stage 9 — Shader

The Shader owns:

```
program

uniform locations

attribute locations
```

The shader is created once.

Typical workflow:

```
compile

↓

link

↓

cache uniforms
```

Every frame:

```
use()

↓

set uniforms

↓

draw
```

---

# Stage 10 — Draw

The Mesh performs the draw.

Internally:

```
bind VAO

↓

bind VBO

↓

enable attributes

↓

glDrawArrays()
```

Everything required for rendering is now already on the GPU.

---

# Stage 11 — Display

OpenGL renders into the framebuffer.

After every render pass:

```
swap buffers
```

The image becomes visible.

---

# Render Graph

Rendering is organized into passes.

Current pipeline:

```
GeometryPass
```

Future pipeline:

```
ShadowPass

↓

GeometryPass

↓

GlowPass

↓

CRT

↓

UI

↓

Overlay
```

Every pass operates on Renderables.

---

# GeometryBuilder

Current responsibilities include:

```
Polyline

↓

StrokeBuilder
```

Future responsibilities may include:

```
Circle

Arc

Bezier

Spline

Polygon

Mesh

Text
```

Every primitive eventually produces triangles.

---

# Native Components

The renderer currently contains several native C systems.

## Stroke Builder

Converts lines into triangles.

---

## VertexBuffer

Owns CPU-side vertex memory.

---

## Mesh

Owns GPU buffers.

Performs draw calls.

---

## Shader

Compiles shaders.

Caches uniforms.

Binds programs.

---

Together these components perform almost all expensive rendering work.

---

# Python Responsibilities

Python remains responsible for:

```
Simulation

Animation

Audio

Particles

Procedural generation

Scene composition

Module management
```

Python never manipulates GPU resources directly.

---

# Native Responsibilities

Native C performs:

```
Stroke tessellation

Memory allocation

Vertex storage

GPU upload

Draw calls

Shader management
```

This separation allows the engine to remain expressive while achieving native performance.

---

# Cached Objects

Several objects persist across frames.

```
Mesh

Shader

Material

Transform
```

Others are rebuilt every frame.

```
Frame

Geometry

VertexBuffer contents
```

This minimizes allocations while preserving a clean architecture.

---

# Frame Lifetime

Each frame follows this lifecycle.

```
Frame created

↓

Modules submit Renderables

↓

Renderer consumes Frame

↓

Geometry generated

↓

Uploaded

↓

Drawn

↓

Frame discarded
```

The next frame begins with a completely new Frame.

---

# Data Ownership

Ownership transfers through the pipeline.

```
Module

owns simulation

↓

Geometry

owns logical shape

↓

GeometryBuilder

owns tessellation

↓

VertexBuffer

owns CPU memory

↓

Mesh

owns GPU memory

↓

GPU

owns rendered image
```

Each object has one clear owner.

---

# Error Handling

Errors should be detected as early as possible.

Examples:

Modules:

- invalid parameters
- invalid geometry

GeometryBuilder:

- malformed primitives

Shader:

- compilation failures

Mesh:

- invalid OpenGL state

Keeping failures localized simplifies debugging.

---

# Performance Goals

The renderer is designed so that modules remain almost entirely Python while the expensive work executes natively.

Typical cost breakdown:

```
Simulation

↓

Geometry generation

↓

Native tessellation

↓

GPU upload

↓

Draw
```

On modern hardware:

- simulation is usually inexpensive
- tessellation dominates CPU time
- GPU upload dominates bandwidth
- draw calls dominate driver overhead

The native backend exists primarily to reduce these costs.

---

# Design Goals

The pipeline was designed around several goals.

## Predictable

Every frame follows exactly the same sequence.

---

## Deterministic

Modules cannot interfere with rendering.

---

## Portable

Only a small native layer depends on OpenGL.

Modules remain renderer-independent.

---

## Efficient

Large memory allocations are avoided.

GPU resources are persistent.

CPU memory is reused.

---

## Extensible

New primitives require changes only inside the GeometryBuilder.

Modules remain unchanged.

---

# Pipeline Summary

Every visualization in Retroscope ultimately follows this sequence:

```
Module

↓

Simulation

↓

Geometry

↓

Renderable

↓

Frame

↓

GeometryBuilder

↓

StrokeBuilder (C)

↓

VertexBuffer (C)

↓

Mesh (C)

↓

Shader (C)

↓

OpenGL

↓

GPU

↓

Framebuffer

↓

Display
```

This strict separation between procedural generation and rendering is the defining architectural characteristic of Retroscope.

It allows visualization modules to remain simple, portable, and expressive while concentrating all rendering complexity inside a highly optimized native backend.