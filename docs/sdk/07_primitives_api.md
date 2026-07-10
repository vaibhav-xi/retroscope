# 07 - Primitive API

Version: 1.0

---

# Introduction

Primitives are the smallest drawable objects in Retroscope.

Everything visible on screen ultimately originates from one or more primitives.

Unlike a Renderable, a primitive does not know anything about

- materials
- transforms
- meshes
- shaders
- GPU buffers

A primitive only answers one question:

> **"What geometric object should exist?"**

---

# Rendering Pipeline

Primitives are the foundation of the rendering pipeline.

```
Module

↓

Geometry

↓

Primitive

↓

Geometry Builder

↓

Native Builder

↓

Vertex Buffer

↓

Mesh

↓

Renderer

↓

GPU
```

Every object eventually becomes primitives.

---

# Philosophy

Retroscope intentionally separates

**shape**

from

**appearance**

A primitive defines shape.

A Material defines appearance.

A Transform defines position.

A Renderable combines them.

---

# Primitive Hierarchy

Conceptually

```
Renderable

↓

Geometry

↓

Primitive

↓

Vertices
```

Geometry is simply a collection of primitives.

---

# Current Primitive

Today the engine contains one primary primitive.

```
Polyline
```

Although simple,

it is surprisingly powerful.

Waveforms

Grid lines

Boxes

Crosshairs

Axes

Curves

All are constructed from polylines.

---

# Why Only Polyline?

Retroscope began as an oscilloscope.

Nearly every visualization consisted of

continuous strokes.

Instead of implementing many primitive types immediately,

the engine optimized one primitive extremely well.

Today,

Polyline generation is entirely native C code.

---

# Polyline

A Polyline represents

```
P0

↓

P1

↓

P2

↓

P3
```

Each segment has thickness.

Unlike OpenGL lines,

these are converted into triangles.

Advantages

- identical appearance on every platform
- configurable width
- future joins
- future caps
- antialiasing support

---

# Polyline Data

Conceptually

```python
Polyline

points

width
```

Example

```python
Polyline(

    points=[

        (0,0),

        (50,20),

        (90,80),

    ],

    width=2.0

)
```

---

# Geometry Builder

When the renderer encounters a Polyline

```
Polyline

↓

Stroke Builder

↓

Triangles
```

The module never performs this conversion.

---

# Native Stroke Builder

The Stroke Builder computes

```
Normals

↓

Offsets

↓

Triangle Strip

↓

Vertex Buffer
```

All of this happens in optimized C.

---

# Why Not OpenGL Lines?

OpenGL line rendering is notoriously inconsistent.

Different drivers produce different results.

Many platforms ignore

```
glLineWidth()
```

especially OpenGL ES.

Generating triangles provides

- deterministic output
- thick lines
- portability
- future styling

---

# Primitive Ownership

Primitives belong to Geometry.

```
Geometry

↓

Primitive

↓

Vertices
```

Modules normally manipulate Geometry,

not individual primitives directly.

---

# Multiple Primitives

A Geometry object may contain many primitives.

Example

```
Geometry

├── Polyline

├── Polyline

├── Polyline

└── Polyline
```

The builder processes each independently.

---

# Example

A grid may consist of

```
100 horizontal lines

+

100 vertical lines
```

Each line is one Polyline.

---

# Compound Objects

A single visual object often consists of multiple primitives.

Example

Radar

```
Outer Circle

↓

Sweep

↓

Crosshair

↓

Tick Marks
```

Although visually one object,

internally it is many primitives.

---

# Primitive Lifetime

Primitives usually live inside Geometry.

```
Geometry Created

↓

Primitive Created

↓

Modified

↓

Modified

↓

Destroyed
```

They are rarely created every frame.

---

# Dynamic Primitives

Waveforms

Particles

Audio

Noise

These update frequently.

Only the primitive data changes.

The object itself remains.

---

# Static Primitives

Grid

Frame

Border

Reference Axis

Generated once,

reused forever.

---

# Builder Registration

Each primitive type has a corresponding builder.

```
Primitive

↓

Builder

↓

Vertices
```

Examples

```
Polyline

↓

Polyline Builder
```

Future

```
Circle

↓

Circle Builder
```

---

# Future Primitive Types

The rendering architecture already supports

```
Circle

Arc

Rectangle

Ellipse

Polygon

Spline

Bezier

Text

Point Cloud

Triangle Mesh

Image

Sprite
```

Only builders need to be implemented.

The renderer itself does not change.

---

# Circle Primitive

Conceptually

```python
Circle(

    center,

    radius

)
```

The builder generates

```
Polyline

↓

Stroke Builder

↓

Triangles
```

---

# Arc Primitive

Conceptually

```python
Arc(

    center,

    radius,

    start,

    end
)
```

Internally approximated using many line segments.

---

# Rectangle Primitive

```python
Rectangle(

    x,

    y,

    width,

    height
)
```

Builder generates four edges.

---

# Polygon Primitive

```python
Polygon(

    vertices
)
```

Future versions may support

- filled polygons
- outlined polygons
- triangulation

---

# Text Primitive

Eventually

```python
Text(

    position,

    string,

    font
)
```

will become

glyph geometry

↓

triangles

Modules never generate glyph meshes manually.

---

# Point Cloud Primitive

Useful for

- stars
- particles
- lidar
- radar

Potentially millions of points.

---

# Instanced Primitive

Future versions may allow

```
One Primitive

↓

Thousands of Instances
```

Reducing CPU work dramatically.

---

# Procedural Primitives

Modules may internally generate

```
DNA

↓

Polyline
```

or

```
Spiral

↓

Polyline
```

No renderer changes required.

---

# Primitive Builders

Builders translate

```
Intent

↓

Vertices
```

Modules should never worry about

- tessellation
- normals
- joins
- vertex layout

---

# Coordinate System

Primitives are expressed in world coordinates.

Example

```python
Polyline(

    [

        (100,50),

        (200,120)

    ]

)
```

No GPU coordinate conversion occurs here.

---

# Memory

Primitives are lightweight.

They store

- parameters
- points
- dimensions

They do not store

- VBOs
- VAOs
- OpenGL IDs

---

# Best Practices

✔ Reuse primitives.

✔ Modify existing point arrays.

✔ Avoid reallocating every frame.

✔ Let builders generate triangles.

✔ Express intent,

not implementation.

---

# Anti-Patterns

Never

```python
glBufferData()
```

Never

```python
glDrawArrays()
```

Never

```python
glVertexPointer()
```

Primitives should remain renderer-independent.

---

# Mental Model

Imagine drawing with a pencil.

You sketch

a line,

a circle,

or a rectangle.

Those sketches are primitives.

The Geometry Builder is the machine that converts those sketches into precise manufactured components.

The renderer later paints them.

---

# Example

Suppose a module wants to display a waveform.

It creates

```
Polyline

↓

2048 points
```

The Geometry Builder converts it into

```
~12,000 vertices
```

The renderer uploads those vertices into a Mesh.

The module never sees any of this work.

---

# Future-Proof Design

The Primitive API intentionally remains extremely small.

Adding a new primitive never requires changing

- modules
- renderer
- render graph

Only two new pieces are required

```
Primitive

+

Builder
```

This allows Retroscope to grow from a simple oscilloscope into a complete procedural visualization engine without redesigning the rendering pipeline.

---

# Summary

Primitives are the fundamental geometric building blocks of Retroscope.

They describe abstract shapes without any knowledge of rendering, materials, transforms, or GPU resources.

By separating primitives from rendering, the engine achieves a clean architecture where visualization modules express intent, builders generate optimized geometry, and the renderer focuses solely on efficient drawing.

Although today's engine is centered around the highly optimized `Polyline` primitive, the architecture is intentionally designed to accommodate many future primitive types—including circles, splines, text, point clouds, and procedural geometry—without requiring changes to existing modules or the renderer.