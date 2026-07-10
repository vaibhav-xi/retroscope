# 03 - Geometry

# Introduction

Geometry is the core abstraction of Retroscope.

Everything visible on the screen begins life as geometry.

Unlike traditional graphics engines, modules never construct GPU meshes directly.

Instead, modules construct logical geometry.

The renderer later converts that geometry into triangles suitable for the GPU.

This separation allows modules to remain completely independent from the rendering backend.

Changing the renderer should never require changing a module.

---

# Geometry Philosophy

A Retroscope module should never think about:

- vertices
- triangles
- VBOs
- VAOs
- shaders
- GPU memory

Instead, it should think about shapes.

Examples:

```
Polyline

Circle

Arc

Rectangle

Grid

Spline

Polygon
```

The renderer owns the conversion from these logical shapes into triangles.

---

# Geometry Hierarchy

The current rendering hierarchy is

```
Module

↓

Geometry

↓

Renderable

↓

Frame

↓

Renderer
```

Geometry never renders itself.

Geometry only describes shape.

---

# Primitive vs Geometry

These two terms are closely related.

Primitive

A logical drawing command.

Examples:

```
Polyline

Circle

Rectangle

Arc
```

Geometry

A collection of primitives representing one object.

For example

```
Geometry

├── Polyline
├── Polyline
├── Circle
└── Arc
```

One Geometry may contain many primitives.

---

# Why Separate Them?

Consider a radar.

A radar contains

```
outer circle

inner circles

crosshair

sweep line

markers
```

This should be represented as

```
Geometry

├── Circle
├── Circle
├── Circle
├── Polyline
├── Polyline
├── Polyline
```

instead of many independent renderables.

This keeps related geometry together.

---

# Current Primitive

At present, the engine primarily uses

```
Polyline
```

Every visualization ultimately becomes one or more polylines.

Those polylines are later converted into triangles by the Stroke Builder.

---

# Future Primitive Types

The architecture intentionally allows many primitive types.

Examples include

```
Polyline

Circle

Arc

Rectangle

Polygon

Spline

Bezier

Ellipse

Triangle

Arrow

Text

Mesh
```

Each primitive will eventually have its own GeometryBuilder implementation.

---

# Polyline

A Polyline represents connected line segments.

Example

```
A────B────C────D
```

Internally

```
points

width
```

The renderer later expands this into triangles.

Modules never perform that expansion.

---

# Circle

A Circle represents an ideal mathematical circle.

Fields

```
center

radius
```

The renderer approximates the circle using line segments.

Modules never need to know how many.

---

# Arc

An Arc represents a partial circle.

Fields

```
center

radius

start angle

end angle
```

Again, tessellation is handled by the renderer.

---

# Rectangle

A Rectangle represents four connected edges.

Fields

```
position

width

height
```

Internally the renderer may convert this into

```
Polyline

or

Triangles
```

depending on implementation.

---

# Polygon

Represents any closed shape.

Example

```
hexagon

octagon

star

random outline
```

Stored simply as a list of points.

---

# Spline

Represents a smooth curve.

Possible implementations

```
Bezier

Catmull-Rom

Cubic

Quadratic
```

The renderer approximates the spline with line segments.

---

# Grid

A Grid is conceptually just many polylines.

For example

```
───────

───────

───────

│ │ │ │
```

Internally

```
Polyline

Polyline

Polyline

Polyline
```

---

# Text

Future versions may introduce a Text primitive.

Fields

```
position

string

font

size

alignment
```

Text should remain logical.

Modules should never manipulate glyph meshes.

---

# Mesh

Although the renderer ultimately produces GPU meshes,

modules should almost never construct Mesh primitives directly.

Meshes represent renderer-specific resources.

Geometry remains renderer-independent.

---

# Geometry Object

Geometry groups multiple primitives into one logical object.

Example

```
Geometry

├── Polyline
├── Polyline
├── Circle
└── Arc
```

This entire object is later wrapped inside a Renderable.

---

# Geometry Ownership

Modules own Geometry.

The renderer owns Meshes.

This distinction is fundamental.

```
Module

↓

Geometry

↓

Renderer

↓

Mesh
```

The module never sees the Mesh.

---

# Mutable Geometry

Geometry is mutable.

Modules are free to

- add primitives
- remove primitives
- update points
- rebuild geometry

The renderer will regenerate triangles when required.

---

# Static Geometry

Some geometry rarely changes.

Examples

```
Grid

Borders

Calibration marks
```

The renderer may cache these internally.

Modules do not need special logic.

---

# Dynamic Geometry

Examples

```
Audio wave

Particles

Lightning

Snow

Radar sweep
```

These are rebuilt every frame.

The native backend is optimized for this workflow.

---

# Geometry Lifetime

Typical lifetime

```
Module

creates Geometry

↓

Geometry submitted

↓

Renderer consumes Geometry

↓

Frame destroyed

↓

Next frame
```

Geometry objects may persist between frames if the module chooses.

The renderer treats every frame independently.

---

# Coordinate System

Geometry exists in world coordinates.

The renderer is responsible for mapping those coordinates to clip space.

Modules should never manually convert coordinates for OpenGL.

For example

```
(-1, -1)

↓

Bottom Left
```

```
(1, 1)

↓

Top Right
```

or any future coordinate system.

The mapping belongs to the renderer.

---

# Units

Geometry units are logical.

Examples

```
radius = 50

spacing = 20

width = 3
```

Modules should not assume pixel-perfect rendering.

---

# Precision

Geometry uses floating point values.

Coordinates

```
float
```

Widths

```
float
```

Angles

```
float
```

This provides smooth animation and resolution independence.

---

# Geometry Builders

Each primitive eventually has a corresponding builder.

Example

```
Polyline

↓

StrokeBuilder
```

Future

```
Circle

↓

CircleBuilder
```

```
Text

↓

TextBuilder
```

```
Spline

↓

SplineBuilder
```

Each builder converts logical geometry into triangles.

---

# Extending Geometry

Adding a new primitive generally requires

1.

Define the primitive.

```
Hexagon
```

2.

Teach GeometryBuilder how to build it.

```
HexagonBuilder
```

3.

Done.

Existing modules require no modification.

---

# Example

A holographic sphere module might generate

```
Geometry

├── Circle
├── Circle
├── Circle
├── Arc
├── Arc
├── Arc
├── Polyline
├── Polyline
```

The module never creates triangles.

---

# Another Example

A particle system may generate

```
Geometry

├── Polyline
├── Polyline
├── Polyline
├── Polyline
...
```

Thousands of particles.

The renderer decides how those become GPU geometry.

---

# Design Goals

Geometry should be

Simple

A module should be able to construct geometry with very little code.

Portable

Geometry should not depend on OpenGL.

Composable

Multiple primitives can combine into one object.

Predictable

Geometry always means the same thing regardless of renderer.

Extensible

New primitive types should require minimal changes.

---

# Geometry vs Rendering

The most important distinction in Retroscope is

Geometry answers

> What exists?

Rendering answers

> How is it drawn?

Those responsibilities must remain separate.

---

# Summary

Geometry is the universal language spoken between modules and the renderer.

Modules describe mathematical shapes.

The renderer transforms those shapes into optimized GPU meshes.

Because geometry is independent of OpenGL, visualization modules remain simple, expressive, portable, and future-proof.

Every visible effect in Retroscope—from a single oscilloscope trace to a complex holographic particle system—begins as logical geometry.