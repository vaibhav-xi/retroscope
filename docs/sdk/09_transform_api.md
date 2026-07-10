# 09 - Transform API

Version: 1.0

---

# Introduction

The **Transform** defines where and how a Renderable exists in the world.

Geometry answers

> **"What shape is this?"**

Material answers

> **"What does it look like?"**

Transform answers

> **"Where is it?"**

and eventually

> **"How is it oriented?"**

Every Renderable owns exactly one Transform.

```
Renderable

├── Geometry

├── Material

└── Transform
```

The renderer combines all three during rendering.

---

# Philosophy

A Transform should contain only spatial information.

It should never contain

- geometry
- colors
- shaders
- meshes
- simulation

Instead, it describes how an object is positioned in the world.

---

# Ownership

Every Renderable owns one Transform.

```
Module

↓

Renderable

↓

Transform
```

Modules update transforms.

The renderer consumes them.

---

# Lifetime

Transforms are persistent.

Typical lifetime

```
Module Created

↓

Transform Created

↓

Animated

↓

Animated

↓

Destroyed
```

Transforms are almost never recreated.

---

# Current Implementation

Today's Transform is intentionally minimal.

The current engine primarily renders directly in world coordinates.

A Transform therefore acts mostly as a placeholder for future expansion.

Conceptually

```python
Transform()
```

contains little or no state today.

This is intentional.

---

# Why Have A Transform Already?

A common question is

> Why include a Transform if it currently does very little?

The answer is architectural stability.

Every Renderable already has a place to store spatial information.

As the engine evolves,

the API remains unchanged.

Modules written today continue working tomorrow.

---

# Future Structure

The planned Transform looks approximately like

```python
Transform(

    position=(0, 0),

    rotation=0,

    scale=(1, 1)

)
```

Additional properties may be added without affecting existing modules.

---

# Position

Future property

```python
transform.position
```

Example

```python
transform.position = (

    120,

    300

)
```

Moves the entire Renderable.

---

# Rotation

Future property

```python
transform.rotation
```

Measured in radians.

Example

```python
transform.rotation = math.pi * 0.5
```

Rotates the Renderable about its origin.

---

# Scale

Future property

```python
transform.scale
```

Example

```python
transform.scale = (

    2.0,

    2.0

)
```

Doubles the size of the object.

---

# Origin

Future versions may expose

```python
transform.origin
```

This determines the pivot used during rotation and scaling.

Example

```
Center

Top Left

Bottom Left

Custom Point
```

---

# Matrix

Internally,

future versions may compute

```python
transform.matrix
```

Modules should never build transformation matrices manually.

The renderer handles this automatically.

---

# Hierarchical Transforms

Today's engine intentionally avoids scene graphs.

Therefore

```
Parent

↓

Child
```

relationships do not currently exist.

Every Transform is independent.

Future versions may introduce hierarchy while preserving the public API.

---

# Coordinate Space

Transforms operate in world space.

The renderer later converts world coordinates into clip space.

Modules should not perform projection themselves.

---

# Relationship with Geometry

Geometry describes local shape.

Transform places that shape into the world.

```
Geometry

↓

Transform

↓

Renderer
```

This separation allows geometry to be reused.

---

# Relationship with Material

Transform has no effect on appearance.

Changing position does not change

- color
- opacity
- glow

These remain Material properties.

---

# Relationship with Mesh

Transforms do not modify GPU buffers.

Moving an object should not require rebuilding geometry.

Instead,

future renderers may upload a transformation matrix before drawing.

---

# Static Objects

Example

Grid

```
Geometry

↓

Static

Transform

↓

Identity
```

No updates required.

---

# Animated Objects

Example

Radar Sweep

```
Geometry

↓

Arc

Transform

↓

Rotation

↓

Renderer
```

Only the Transform changes.

Geometry remains untouched.

---

# Translation Example

Imagine a circle.

Geometry

```
Center

↓

(0,0)
```

Transform

```
Position

↓

(300,150)
```

The renderer displays the circle at

```
(300,150)
```

without modifying the Geometry.

---

# Rotation Example

Imagine a radar arm.

Geometry

```
Horizontal Line
```

Transform

```
Rotation

↓

45°
```

The renderer rotates the line.

The Geometry remains unchanged.

---

# Scaling Example

Geometry

```
Unit Circle
```

Transform

```
Scale

↓

3×
```

The renderer draws a larger circle.

Again,

Geometry remains untouched.

---

# Animation

Transforms are ideal for animation.

Example

```python
transform.rotation += (

    context.dt

)
```

or

```python
transform.position = (

    x,

    y

)
```

This is significantly cheaper than rebuilding geometry.

---

# Dirty State

Future renderers may distinguish between

Geometry changes

and

Transform changes.

Example

```
Geometry Dirty

↓

Rebuild Mesh

Transform Dirty

↓

Update Matrix
```

This reduces CPU work.

---

# Camera

A future Camera object will likely be implemented as another Transform.

```
Camera

↓

Transform

↓

View Matrix
```

Using the same abstraction simplifies the renderer.

---

# World Space

Modules should think in world coordinates.

They should never worry about

- clip space
- normalized device coordinates
- projection matrices

Those are renderer responsibilities.

---

# Memory

Transforms are intentionally lightweight.

Current

```
Placeholder
```

Future

```
Position

Rotation

Scale

Matrix Cache
```

Still far smaller than Geometry or Mesh objects.

---

# Best Practices

✔ Modify transforms instead of rebuilding geometry whenever possible.

✔ Keep Geometry local.

✔ Use Transform for animation.

✔ Treat Transform as spatial data only.

---

# Anti-Patterns

Never

```python
glTranslatef(...)
```

Never

```python
glRotate(...)
```

Never

```python
glScale(...)
```

Never

```python
glUniformMatrix4fv(...)
```

Modules should remain completely independent from OpenGL.

---

# Mental Model

Imagine building a cardboard model airplane.

The cardboard pieces represent Geometry.

The paint represents Material.

Where you place the airplane on a shelf is the Transform.

Moving the airplane does not change the cardboard.

Painting it does not move it.

Each concept remains independent.

---

# Example

A future holographic globe module might contain

```
Renderable

↓

Sphere Geometry

↓

Blue Material

↓

Rotating Transform
```

Only the Transform changes every frame.

The renderer rotates the globe while reusing the same Geometry and Mesh.

---

# Future-Proof Design

Although today's Transform is intentionally simple,

its presence throughout the engine allows future features such as

- cameras
- zooming
- panning
- object rotation
- hierarchical transforms
- instancing

to be introduced without changing module code.

This was a deliberate architectural decision made early in the project.

---

# Summary

The Transform represents the spatial component of a Renderable.

While currently minimal, it forms the foundation for future translation, rotation, scaling, cameras, and hierarchical rendering.

By separating spatial information from geometry and appearance, Retroscope enables efficient animation, reusable geometry, and a stable rendering architecture that can evolve significantly without breaking existing modules.

A Transform should be viewed as **the spatial identity** of a Renderable—its place and orientation in the world.