# docs/reference/primitive_reference.md

# Primitive Reference

Version: 1.0

---

# Introduction

Primitives are the fundamental geometric building blocks of Retroscope.

A module never generates triangles directly.

Instead, it creates one or more **Primitives**, which represent logical geometric shapes.

The Geometry Builder later converts these primitives into GPU-ready triangle meshes.

This separation is one of the core architectural principles of Retroscope.

```
Module

↓

Primitive

↓

Geometry

↓

Geometry Builder

↓

Native Vertex Buffer

↓

Mesh

↓

GPU
```

A Primitive is **not** GPU geometry.

It is a mathematical description of geometry.

---

# Philosophy

A Primitive answers the question

> "What shape exists?"

The Geometry Builder answers

> "How should that shape be tessellated?"

---

# Current Primitive Set

Current primitives include

```
Polyline
```

Future primitives are expected to include

```
Line

Circle

Arc

Rectangle

Polygon

Bezier

Spline

Text

Point Cloud

Mesh

Custom
```

The renderer should never need to know where a primitive originated.

---

# Polyline

The Polyline is currently the most important primitive in Retroscope.

It represents one continuous path.

```
P0 ---- P1 ---- P2 ---- P3
```

The Geometry Builder converts this into a strip of triangles with configurable thickness.

---

## Properties

Conceptually

```python
Polyline(

    points=[...],

    width=...

)
```

---

## Points

A Polyline consists of

```
(x,y)

(x,y)

(x,y)
```

stored in order.

---

## Width

Width represents the logical line thickness.

It is interpreted by the Geometry Builder.

The primitive itself contains no triangles.

---

## Open Polyline

```
A ---- B ---- C
```

The endpoints remain open.

---

## Closed Polyline (Future)

```
A

|     |

D ---- C
```

Useful for polygons.

---

# Line

Conceptually

```
P0 -------- P1
```

A Line is simply a Polyline with two points.

The dedicated primitive exists primarily for convenience.

---

# Circle

Conceptually

```
      *****
   **       **
  *     •     *
   **       **
      *****
```

Properties

```python
Circle(

    center=(x,y),

    radius=r
)
```

The Geometry Builder approximates the circle using line segments.

---

## Segment Count

Future versions may automatically choose the number of segments based on

- radius
- zoom
- quality settings

---

# Arc

Represents only part of a circle.

```
*******
      *
      *
```

Properties

```python
Arc(

    center,

    radius,

    start_angle,

    end_angle
)
```

Useful for

- radar
- gauges
- progress indicators
- orbital paths

---

# Rectangle

Conceptually

```
+---------+

|         |

|         |

+---------+
```

Properties

```python
Rectangle(

    center,

    width,

    height
)
```

Future

Rounded corners.

---

# Polygon

General closed shape.

```
   *

*     *

 *   *

   *
```

Properties

```python
Polygon(

    vertices=[...]

)
```

Future triangulation will occur inside the Geometry Builder.

---

# Bezier Curve

Future primitive.

Defined by

```
P0

P1

P2

P3
```

The builder samples the curve into a Polyline before tessellation.

---

# Spline

Future

Catmull-Rom

B-Spline

NURBS

Useful for

- smooth animation paths
- scientific visualization
- handwriting
- motion trails

---

# Text

Future primitive.

Conceptually

```python
Text(

    position,

    string,

    font,

    size
)
```

The renderer determines glyph generation.

Modules remain text-backend independent.

---

# Point Cloud

Future

Represents many independent points.

Useful for

- stars
- particles
- lidar
- scientific data

---

# Mesh

Future

Allows importing externally generated geometry while still integrating with the engine.

Useful for

- CAD
- scientific meshes
- procedural generators

---

# Custom Primitives

The architecture intentionally allows new primitive types.

Workflow

```
New Primitive

↓

Register Builder

↓

Geometry Builder

↓

Renderer
```

No renderer modifications should be required.

---

# Primitive Lifetime

Primitives are temporary.

```
Frame Begins

↓

Module Creates Primitive

↓

Geometry Builder

↓

Triangles

↓

Primitive Discarded
```

GPU geometry persists.

Primitives do not.

---

# Coordinate Space

All primitive coordinates use engine space.

Current range

```
X

-1 → +1

Y

-1 → +1
```

Future camera systems may introduce world coordinates.

---

# Materials

Primitives do **not** store appearance.

Appearance belongs to

```
Renderable

↓

Material
```

This allows one geometry to be rendered using different materials.

---

# Transforms

Primitives describe local geometry.

Transforms belong to the Renderable.

A Circle remains a Circle regardless of where it is rendered.

---

# Audio Reactivity

Modules should modify primitive parameters.

Example

```
Microphone RMS

↓

Circle Radius

↓

New Primitive

↓

Renderer
```

The primitive itself contains no audio logic.

---

# Geometry Builder Responsibility

Every primitive must have a corresponding Geometry Builder implementation.

Example

```
Circle

↓

Circle Builder

↓

Vertices
```

This keeps tessellation isolated from module code.

---

# Best Practices

✔ Describe logical shapes.

✔ Keep primitives immutable where possible.

✔ Avoid embedding rendering state.

✔ Keep coordinate systems consistent.

✔ Separate geometry from appearance.

---

# Anti-Patterns

Avoid

- OpenGL calls
- GPU handles
- materials inside primitives
- transforms inside primitive definitions
- renderer-specific data

A primitive should remain a purely mathematical object.

---

# Summary

Primitives are the language used by modules to describe geometry.

Rather than creating GPU vertices directly, modules construct logical shapes such as polylines, circles, rectangles, and polygons. The Geometry Builder converts these shapes into optimized triangle meshes, allowing visualization code to remain concise, renderer-independent, and mathematically expressive.

As Retroscope evolves, new primitive types can be added without changing the rendering architecture, making the Primitive system one of the engine's most extensible components.