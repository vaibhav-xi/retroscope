# 06 - Geometry API

Version: 1.0

---

# Introduction

Geometry is the mathematical description of a Renderable.

It answers one question:

> **"What shape should this object have?"**

Unlike a Mesh, Geometry does **not** contain GPU resources.

Unlike a Renderable, Geometry does **not** contain appearance.

It is simply a description of vertices and primitives.

```
Module

↓

Geometry

↓

Renderable

↓

Geometry Builder

↓

Vertex Buffer

↓

Mesh

↓

GPU
```

Geometry is entirely CPU-side.

---

# Philosophy

Geometry should describe intent, not implementation.

A module should say

> Draw a polyline through these points.

not

> Upload these 842 vertices to a VBO.

That translation is the responsibility of the Geometry Builder.

---

# Current Pipeline

Today's rendering pipeline looks like

```
Primitive

↓

Geometry

↓

Geometry Builder

↓

Native Stroke Builder

↓

Vertex Buffer

↓

Mesh

↓

OpenGL
```

Every primitive ultimately becomes triangles.

---

# Geometry vs Mesh

These two objects are frequently confused.

Geometry

```
Logical

CPU

Editable

Portable
```

Mesh

```
GPU

Optimized

Cached

Draw-ready
```

Modules work almost exclusively with Geometry.

The renderer owns the Mesh.

---

# Geometry Object

A Geometry object is essentially a container of primitives.

Conceptually

```python
Geometry

└── primitives[]
```

Each primitive describes one independent piece of geometry.

---

# Example

```
Geometry

├── Polyline

├── Circle

├── Rectangle

└── Polygon
```

The Geometry Builder visits every primitive in order.

---

# Why Separate Geometry?

Suppose a module wants to draw

- one waveform
- one grid
- twenty circles

Instead of creating twenty-two Renderables,

they may all belong to one Geometry object.

```
Renderable

↓

Geometry

↓

22 primitives
```

This reduces overhead.

---

# Primitive Types

Today Retroscope primarily uses

```
Polyline
```

because the engine originated as an oscilloscope renderer.

Future primitive types include

```
Line

Circle

Arc

Rectangle

Polygon

Spline

Bezier

Text

Points

Triangles
```

The pipeline was designed for this expansion.

---

# Polyline

The most common primitive.

Represents

```
P0

↓

P1

↓

P2

↓

P3
```

with a configurable stroke width.

The native Stroke Builder converts it into triangles.

---

# Circle

Conceptually

```python
Circle

center

radius
```

The Geometry Builder approximates the circle using line segments.

Modules never generate those segments manually.

---

# Rectangle

Conceptually

```python
Rectangle

position

width

height
```

Converted into four connected edges.

---

# Arc

Represents

```
start angle

end angle

radius
```

Internally approximated using line segments.

---

# Polygon

Represents

```
N vertices
```

Future versions may support

- filled polygons
- outlined polygons
- triangulation

---

# Text

Future primitive.

Instead of drawing letters manually,

modules will simply submit

```python
Text

position

string

font
```

The renderer will generate glyph geometry.

---

# Custom Geometry

Modules are free to define their own procedural geometry.

For example

```
DNA Helix

↓

Spiral Generator

↓

Polyline
```

or

```
Particle System

↓

Thousands of Polylines
```

As long as the Geometry Builder understands the primitive.

---

# Geometry Builder

The Geometry Builder converts abstract geometry into vertices.

```
Geometry

↓

Primitive

↓

Native Builder

↓

Vertex Buffer
```

Modules never call OpenGL.

---

# Native Stroke Builder

Currently,

Polyline primitives are expanded by the native C implementation.

```
Polyline

↓

stroke_build()

↓

Triangles
```

This is one of the engine's largest performance optimizations.

---

# Vertex Buffer

The Geometry Builder writes directly into

```
VertexBuffer
```

which is a native dynamically growing array.

The renderer later uploads it into the Mesh.

---

# Primitive Ordering

Primitives are processed in insertion order.

```
Geometry

↓

Primitive 1

↓

Primitive 2

↓

Primitive 3
```

Ordering only affects generation,

not rendering.

The Renderable determines draw order.

---

# Geometry Ownership

Modules own Geometry.

```
Module

↓

Geometry
```

Renderables reference it.

```
Renderable

↓

Geometry
```

The renderer never owns Geometry.

---

# Lifetime

Geometry is usually long-lived.

```
Module Created

↓

Geometry Created

↓

Modified

↓

Modified

↓

Destroyed
```

Modules should reuse Geometry whenever possible.

---

# Dirty Geometry

Changing Geometry requires

```python
renderable.is_dirty = True
```

Nothing else.

The renderer automatically rebuilds the Mesh.

---

# Geometry Allocation

Good

```python
self.geometry = Geometry()
```

Bad

```python
Geometry()
```

inside

```python
build()
```

every frame.

---

# Dynamic Geometry

Waveforms

Particles

Noise

Audio

These typically change every frame.

The Geometry object remains.

Only its contents change.

---

# Static Geometry

Examples

Grid

Logo

Frame

HUD Border

These are often generated once.

The renderer uploads them only once.

---

# Coordinate System

Geometry exists in world coordinates.

The renderer does not distinguish between

```
Grid

Wave

Particles
```

They are all simply collections of vertices.

---

# Precision

Current coordinates are floating point.

Example

```python
(123.5, 92.25)
```

This allows

- smooth animation
- scaling
- interpolation

---

# Memory

Geometry is intentionally lightweight.

It contains

- primitive descriptions
- parameters

It does **not** contain

- GPU buffers
- OpenGL handles
- shaders

---

# Builder Registry

The Geometry Builder does not know every primitive itself.

Instead,

builders are registered.

Conceptually

```
Polyline

↓

Polyline Builder

Circle

↓

Circle Builder

Text

↓

Text Builder
```

This allows the engine to grow without modifying the renderer.

---

# Adding New Primitive Types

Future workflow

```
Create Primitive

↓

Create Builder

↓

Register Builder

↓

Done
```

The renderer immediately understands the new primitive.

---

# Example

A future Spiral primitive

```
Spiral

↓

Spiral Builder

↓

Polyline

↓

Stroke Builder

↓

Triangles
```

The renderer itself remains unchanged.

---

# Why Builders?

Instead of placing geometry generation inside every module,

Retroscope centralizes it.

Benefits include

- consistent output
- native acceleration
- easier optimization
- reusable algorithms

---

# Performance

Current optimized path

```
Polyline

↓

Native C

↓

VertexBuffer

↓

Mesh
```

Future builders may also move to C.

Examples

- circles
- polygons
- splines

---

# Best Practices

✔ Reuse Geometry objects.

✔ Reuse primitives.

✔ Modify existing data.

✔ Mark Renderables dirty.

✔ Let the Geometry Builder regenerate vertices.

---

# Anti-Patterns

Never

```python
glVertexAttribPointer()
```

Never

```python
glDrawArrays()
```

Never

```python
glBufferData()
```

Geometry should never know about OpenGL.

---

# Mental Model

Imagine Geometry as a CAD drawing.

It describes

- dimensions
- paths
- curves

The Geometry Builder is the factory that turns the drawing into manufactured parts.

The Mesh stores those manufactured parts.

The renderer finally assembles them on screen.

---

# Example

An oscilloscope module might generate

```
Geometry

↓

Polyline

↓

2048 points
```

The Geometry Builder expands it into

```
12,000+ vertices
```

Those vertices are uploaded into the Mesh,

which the renderer finally draws.

The module never sees this conversion.

---

# Future Directions

The Geometry system is intentionally extensible.

Planned additions include

- circles
- arcs
- splines
- Bézier curves
- polygons
- text
- point clouds
- instancing
- signed-distance geometry

None of these require changing the module API.

Only new primitive types and builders.

---

# Summary

Geometry is the CPU-side description of shape in Retroscope.

It is composed of one or more primitives that describe *what* should be drawn, while leaving *how* those shapes become triangles to the Geometry Builder.

This separation allows modules to remain expressive and simple, enables aggressive native optimization, and provides a clean path for adding entirely new primitive types without changing the renderer or existing visualization modules.