# docs/reference/transform_reference.md

# Transform Reference

Version: 1.0

---

# Introduction

A **Transform** describes **where** a Renderable exists.

It does **not** describe

- geometry
- appearance
- rendering

Instead, it describes the spatial relationship between an object and the world.

```
Renderable

├── Geometry

├── Material

└── Transform
```

This separation allows one piece of geometry to be reused in multiple places without duplication.

---

# Philosophy

Geometry answers

> **What is the object?**

Material answers

> **What does it look like?**

Transform answers

> **Where is it?**

Keeping these three concepts independent is one of the most important architectural decisions in Retroscope.

---

# Current Transform

Current implementation is intentionally simple.

```python
Transform()
```

Future versions will gradually expand it while keeping the public API stable.

---

# Ownership

Every Renderable owns exactly one Transform.

```
Renderable

↓

Transform
```

The renderer applies the Transform during rendering.

Modules modify the Transform.

---

# Why Transforms Exist

Imagine 100 identical circles.

Without transforms

```
100 Different Geometries
```

With transforms

```
1 Geometry

↓

100 Transforms

↓

100 Objects
```

This dramatically reduces memory usage.

---

# Translation

Translation moves an object.

Example

```
(0,0)

↓

(0.5,0.2)
```

The geometry remains identical.

Only its position changes.

---

## Example

```python
renderable.transform.position = (

    0.25,

    -0.5

)
```

---

# Rotation (Future)

Future

```python
renderable.transform.rotation
```

Example

```
45°

90°

180°
```

Useful for

- radar sweeps
- rotating globes
- particle emitters
- UI elements

---

# Scale (Future)

Example

```python
renderable.transform.scale =

2.0
```

This enlarges the object without regenerating geometry.

---

# Non-Uniform Scale

Future

```python
(

2.0,

0.5

)
```

Stretching

X independently from Y.

---

# Matrix Representation

Internally,

future renderers may store

```
4×4 Matrix
```

or

```
3×3 Matrix
```

Modules should never manipulate matrices directly unless required.

---

# Local Space

Geometry is created in

```
Local Space
```

Example

```
Circle

Center = (0,0)
```

The Transform places that circle elsewhere.

---

# World Space

After applying the Transform

```
Local

↓

World
```

The renderer performs this conversion.

---

# Screen Space

Finally

```
World

↓

Camera

↓

Screen
```

Current engine has no camera,

so this stage is effectively the identity transform.

---

# Hierarchical Transforms (Future)

Future architecture

```
Radar

↓

Sweep

↓

Target

↓

Label
```

Children inherit parent transforms.

Useful for

- UI
- articulated systems
- orbiting objects

---

# Example

```
Solar System

↓

Sun

↓

Planet

↓

Moon
```

Moving the Sun automatically moves everything beneath it.

---

# Rotation Around Parent

Hierarchy allows

```
Moon

↓

Planet

↓

Sun
```

without manually recomputing positions.

---

# Pivot Point (Future)

Future

```python
transform.pivot
```

Allows

```
Rotate Around Edge

Rotate Around Center

Rotate Around Arbitrary Point
```

---

# Animation

Transforms are ideal for animation.

Example

```python
rotation +=

speed *

dt
```

Geometry never changes.

---

# Audio Reactivity

Rather than rebuilding geometry,

audio may simply modify

```
Scale

Rotation

Position
```

Much cheaper than generating new vertices.

---

# Camera Relationship

Current engine

```
Renderable

↓

Screen
```

Future

```
Renderable

↓

Transform

↓

Camera

↓

Projection

↓

Screen
```

The module API remains unchanged.

---

# Dirty State

Changing only a Transform should not rebuild geometry.

Instead

```
Transform Changed

↓

Renderer Updates Matrix

↓

Draw
```

Geometry remains cached.

---

# Instancing (Future)

Transforms enable GPU instancing.

Example

```
One Circle

↓

10,000 Transforms

↓

10,000 Objects
```

Without duplicating geometry.

---

# Physics

Future simulations

```
Velocity

↓

Position

↓

Transform
```

Geometry remains static.

---

# Polar Motion

Example

```python
x =

cos(angle)

y =

sin(angle)
```

Only the Transform changes.

Useful for

- orbiting particles
- radar sweeps
- Jarvis globe

---

# UI

Transforms also position

- labels
- overlays
- buttons

The same abstraction applies everywhere.

---

# Transform Composition

Future

```
Scale

↓

Rotate

↓

Translate
```

The renderer combines these into one matrix.

Modules should not perform matrix multiplication manually.

---

# Relationship With Geometry

Good

```
Move Circle

↓

Transform
```

Bad

```
Regenerate Circle

↓

Different Coordinates
```

Whenever possible,

move geometry instead of rebuilding it.

---

# Relationship With Materials

Transforms affect

```
Location
```

Materials affect

```
Appearance
```

These systems remain independent.

---

# Performance

Transform updates are among the cheapest operations in the renderer.

If an animation can be expressed as a Transform,

it should usually avoid rebuilding geometry.

---

# Best Practices

✔ Keep geometry centered around its local origin.

✔ Use Transforms for movement.

✔ Use Transforms for rotation.

✔ Use Transforms for scaling.

✔ Keep geometry immutable whenever possible.

---

# Anti-Patterns

Avoid

- storing colors inside Transform
- modifying vertices for simple movement
- embedding GPU state
- camera logic inside modules

Transforms describe spatial relationships only.

---

# Future Transform API

Long-term

```python
Transform(

    position,

    rotation,

    scale,

    parent,

    pivot
)
```

This API should remain stable even as the renderer evolves.

---

# Mental Model

Imagine a rubber stamp.

The stamp itself is the Geometry.

The ink is the Material.

Where you press the stamp onto the paper is the Transform.

You can stamp the same shape hundreds of times in different places without carving a new stamp each time.

That is exactly how Retroscope treats geometry and transforms.

---

# Summary

The Transform system defines the spatial placement of Renderables while remaining completely independent of geometry and appearance. By separating position, rotation, and scale from the underlying mesh, Retroscope enables efficient animation, future GPU instancing, hierarchical scenes, and camera support without requiring geometry regeneration.

Transforms are one of the key abstractions that allow procedural visualizations to remain expressive, performant, and renderer-independent.