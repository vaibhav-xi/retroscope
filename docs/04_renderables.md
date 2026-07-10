# 04 - Renderables

# Introduction

A **Renderable** is the bridge between simulation and rendering.

Geometry alone is not enough to draw something.

A line has no color.

A circle has no position.

A particle has no orientation.

A Renderable combines all of these pieces into a single drawable object.

Conceptually,

```
Renderable

=

Geometry

+

Material

+

Transform
```

The renderer only understands Renderables.

Modules therefore generate Renderables rather than talking directly to the renderer.

---

# Philosophy

Geometry answers

> What shape exists?

Material answers

> How should it look?

Transform answers

> Where does it exist?

Renderable answers

> Draw this object.

---

# Current Structure

Today, a Renderable contains

```
Geometry

Material

Transform

Mesh (cached)

Flags
```

The cached mesh belongs to the renderer.

Modules should never interact with it directly.

---

# Complete Layout

```
Renderable

├── Geometry

├── Material

├── Transform

├── Cached Mesh

├── Visibility

├── Dirty Flag

└── Dynamic Flag
```

Not every field is manipulated by modules.

Several exist purely to help the renderer.

---

# Geometry

Geometry describes the mathematical shape.

Examples

```
Polyline

Circle

Grid

Spline

Arc
```

Geometry contains no GPU data.

---

# Material

Material describes appearance.

Examples

```
Color

Opacity

Glow

Blending
```

Material never changes the underlying shape.

---

# Transform

Transform describes placement.

Examples

```
Position

Rotation

Scale
```

The same Geometry may be drawn many times using different Transforms.

---

# Cached Mesh

The renderer stores GPU resources inside the Renderable.

This cache includes

```
VAO

VBO

Vertex Count
```

The module should completely ignore these.

They exist solely to accelerate rendering.

---

# Dirty Flag

The dirty flag tells the renderer

> Geometry has changed.

When dirty

```
Geometry

↓

Rebuild

↓

Upload

↓

Draw
```

When clean

```
Reuse GPU Mesh

↓

Draw
```

This avoids unnecessary CPU work.

---

# Dynamic Flag

Some Renderables change every frame.

Examples

```
Waveform

Particles

Lightning
```

Others rarely change.

Examples

```
Grid

Frame

Background

Logo
```

Dynamic renderables are expected to rebuild frequently.

Static renderables should be reused whenever possible.

---

# Visibility

Renderable visibility is independent from existence.

Invisible objects still exist.

They simply are not rendered.

Example

```
renderable.is_visible = False
```

Future optimizations may skip invisible objects entirely.

---

# Lifetime

Typical lifetime

```
Create

↓

Modify

↓

Submit

↓

Renderer

↓

Reuse Next Frame
```

The Renderable itself may persist for the application's lifetime.

Only its Geometry changes.

---

# Ownership

A Renderable owns

```
Geometry

Material

Transform
```

The renderer owns

```
GPU Buffers

Native Mesh

Vertex Memory
```

Keeping ownership separate simplifies memory management.

---

# Multiple Renderables

A module may submit any number of Renderables.

Example

```
Frame

├── Grid

├── Wave

├── Cursor

├── Labels

└── Overlay
```

Each Renderable is processed independently.

---

# Why Not One Giant Geometry?

Imagine an oscilloscope.

```
Grid

Wave

Crosshair

Trigger Marker

Text
```

If all of these become one Renderable

```
Everything
```

then changing one element forces everything to rebuild.

Instead

```
Grid

Wave

Cursor

Labels
```

can each update independently.

---

# Materials Are Shared

Multiple Renderables may share the same Material.

Example

```
Green Material

↓

Grid

↓

Wave

↓

Ticks
```

Changing one Material updates every Renderable using it.

---

# Geometry Is Not Shared

Geometry belongs to one Renderable.

Each Renderable represents one logical object.

---

# Transforms Are Independent

The same Geometry may appear multiple times.

Example

```
Circle Geometry

↓

Renderable A

↓

Position (0,0)

↓

Renderable B

↓

Position (100,50)

↓

Renderable C

↓

Position (-20,80)
```

Only the Transform changes.

---

# Renderer Perspective

When rendering begins,

the renderer sees only Renderables.

It does not know

```
Wave Module

Grid Module

Snow Module
```

It simply receives

```
Renderable

Renderable

Renderable

Renderable
```

This keeps rendering independent of simulation.

---

# Example

```python
geometry = Geometry()

...

material = Material(

    color=(0.0,1.0,0.4)

)

renderable = Renderable(

    geometry=geometry,

    material=material

)

frame.add(renderable)
```

Notice there are

- no shaders
- no OpenGL
- no GPU calls

---

# Cached Rendering

The first frame

```
Geometry

↓

Build Mesh

↓

Upload
```

Later frames

```
Reuse Mesh

↓

Draw
```

This dramatically reduces CPU work.

---

# Dirty Workflow

Imagine a waveform.

```
New Samples

↓

Geometry Changes

↓

Dirty = True

↓

Rebuild Mesh

↓

Upload
```

Now imagine a static grid.

```
Geometry

↓

Upload Once

↓

Dirty = False

↓

Draw Forever
```

---

# Render Ordering

Today

Renderables are processed in submission order.

Future versions may support

```
Layer

Priority

Depth

Render Queue
```

without changing the Renderable API.

---

# Future Extensions

The Renderable class has intentionally been kept minimal.

Future additions may include

```
Clipping

Instancing

Picking

Visibility Masks

Layer IDs

Bounding Volumes

Custom Uniforms

LOD

Animation
```

Modules should remain unaffected.

---

# Performance

The renderer assumes

- many Renderables
- many frames
- frequent updates

Therefore

Renderables are lightweight objects.

GPU resources remain cached.

Only Geometry changes.

---

# Best Practices

Keep one logical object per Renderable.

Examples

Good

```
Grid

Wave

Cursor

Overlay
```

Poor

```
Everything In One Renderable
```

Smaller Renderables improve

- readability
- caching
- future parallelism
- renderer optimizations

---

# Mental Model

Think of a Renderable as a sentence.

Geometry is the noun.

Material is the adjective.

Transform is the location.

Together they form a complete instruction.

```
Draw

this Geometry

using this Material

at this Transform.
```

Nothing more.

Nothing less.

---

# Summary

Renderable is the fundamental object consumed by the renderer.

It combines

- Geometry
- Material
- Transform

into a complete drawable object while hiding every GPU detail from module authors.

Modules never manipulate meshes, shaders, buffers, or OpenGL.

They simply construct Renderables describing **what should exist**, leaving the renderer free to decide **how that geometry reaches the screen**.

This separation is one of the key architectural principles that makes Retroscope both easy to extend and highly optimized.