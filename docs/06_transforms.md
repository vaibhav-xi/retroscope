# 06 - Transforms

# Introduction

A Transform describes **where and how geometry exists in the world**.

Geometry describes shape.

Material describes appearance.

Transform describes spatial placement.

Together they form a Renderable.

```
Geometry

+

Material

+

Transform

↓

Renderable
```

Without a Transform, every object would exist in exactly the same place.

Transforms allow geometry to be reused anywhere in the scene.

---

# Philosophy

Geometry should never contain positioning information beyond its own local coordinate system.

For example, imagine a circle.

```
Circle

Radius = 25
```

The circle itself should not know whether it is

- centered on the screen
- attached to a particle
- orbiting another object
- part of a holographic sphere

Those responsibilities belong to the Transform.

---

# Why Separate Transform From Geometry?

Imagine drawing one thousand identical particles.

Without Transforms you would need

```
1000 copies

of

1000 different geometries
```

With Transforms

```
One Geometry

↓

1000 Transforms
```

This dramatically reduces memory usage and simplifies animation.

---

# Current Transform

Today the Transform class is intentionally simple.

It represents the position and orientation of a Renderable.

Typical fields include

```
Translation

Rotation

Scale
```

Internally these may later become a matrix.

---

# Translation

Translation moves an object.

Example

```
Circle

↓

(100, 50)
```

becomes

```
          ○
```

instead of

```
○
```

Translation never changes the geometry itself.

---

# Rotation

Rotation changes orientation.

Example

```
Arrow

↓

45°

```

Geometry remains unchanged.

Only its orientation changes.

---

# Scale

Scale changes size.

Example

```
Scale = 2
```

doubles the apparent size of an object.

The underlying Geometry remains identical.

---

# Composition

Transforms combine.

For example

```
Scale

↓

Rotate

↓

Translate
```

The renderer combines these into a final transformation.

Modules should not manually compute transformed vertices.

---

# Local Space

Every Geometry is defined in **local space**.

For example

```
(-1, 0)

(0, 1)

(1, 0)
```

may define a triangle centered around the origin.

The Transform moves this triangle into world space.

---

# World Space

After applying the Transform

```
Translate

↓

Rotate

↓

Scale
```

the object exists somewhere in the world.

Modules normally think in world coordinates.

The renderer converts world coordinates into clip space.

---

# Coordinate Spaces

Retroscope distinguishes several coordinate systems.

```
Local Space

↓

World Space

↓

View Space

↓

Clip Space

↓

Screen Space
```

Currently most modules operate directly in world space.

Future camera support will introduce view transformations.

---

# Identity Transform

The simplest Transform is

```
Position = (0,0)

Rotation = 0°

Scale = 1
```

This is called the identity transform.

Applying it changes nothing.

---

# Independent Geometry

Because Geometry and Transform are separate,

the same Geometry may appear many times.

Example

```
Circle Geometry

↓

Renderable A

↓

Transform A

↓

Renderable B

↓

Transform B

↓

Renderable C

↓

Transform C
```

Only the Transform changes.

---

# Animation

Animation almost always modifies the Transform.

Example

```python
transform.position.x += speed * dt
```

The Geometry remains untouched.

---

# Orbiting Objects

Example

```
Angle

↓

sin()

↓

cos()

↓

Translation
```

The Geometry never changes.

Only its Transform updates every frame.

---

# Scaling Effects

Examples

```
Heartbeat

↓

Scale
```

```
Audio Pulse

↓

Scale
```

```
Explosion

↓

Scale
```

Again,

Geometry remains unchanged.

---

# Rotation Effects

Examples

```
Radar Sweep

↓

Rotation
```

```
Compass

↓

Rotation
```

```
Clock Hands

↓

Rotation
```

No Geometry regeneration is required.

---

# Future Matrix Representation

Internally,

Transforms may eventually store

```
4×4 Matrix
```

instead of separate values.

Modules should never depend on internal representation.

They should use the public API only.

---

# Hierarchical Transforms

Future versions may support parent-child relationships.

Example

```
Solar System

Sun

↓

Planet

↓

Moon
```

Moving the Sun automatically moves everything beneath it.

---

# Camera

Currently,

Retroscope primarily renders directly in world coordinates.

Future versions may introduce a Camera.

The pipeline would become

```
Geometry

↓

Transform

↓

Camera

↓

Projection

↓

Screen
```

Existing modules would require no modification.

---

# Instancing

Transforms naturally enable GPU instancing.

Example

```
One Circle

↓

10,000 Transforms

↓

10,000 Rendered Circles
```

without duplicating Geometry.

---

# Performance

Changing a Transform is much cheaper than rebuilding Geometry.

Example

Instead of

```
Rebuild

↓

Upload

↓

Draw
```

the renderer can simply update transformation state.

This becomes important for large particle systems.

---

# Best Practices

Animate Transforms whenever possible.

Avoid rebuilding Geometry if only the position changes.

Good

```
Particle

↓

Update Transform
```

Poor

```
Particle

↓

Rebuild Circle Geometry
```

every frame.

---

# Transform Lifetime

Transforms usually persist.

Example

```
Create

↓

Modify

↓

Render

↓

Modify

↓

Render
```

Only the values change.

The object itself remains.

---

# Examples

A moving cursor

```
Geometry

↓

Crosshair

↓

Transform

↓

Mouse Position
```

A rotating radar

```
Geometry

↓

Sweep Line

↓

Transform

↓

Rotation
```

A pulsing hologram

```
Geometry

↓

Sphere Rings

↓

Transform

↓

Animated Scale
```

---

# Future Extensions

The Transform system has intentionally been designed for growth.

Future additions may include

- parent transforms
- pivot points
- shear
- billboarding
- constraints
- animation tracks
- skeletal transforms
- camera-relative transforms
- instancing support

These additions should not affect existing modules.

---

# Mental Model

Think of Geometry as a stamp.

The Transform decides

- where to stamp it
- how large the stamp is
- how it is rotated

The stamp itself never changes.

---

# Summary

Transforms define the spatial placement of Geometry.

They are responsible for

- translation
- rotation
- scale

while remaining completely independent from both Geometry and Material.

This separation allows geometry to be reused efficiently, animated cheaply, and rendered consistently while keeping modules focused on procedural generation rather than rendering details.

Geometry defines **what exists**.

Material defines **how it appears**.

Transform defines **where it exists**.

Together they form the complete visual language of Retroscope.