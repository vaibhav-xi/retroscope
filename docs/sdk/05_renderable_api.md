# 05 - Renderable API

Version: 1.0

---

# Introduction

The **Renderable** is the central rendering object in Retroscope.

Every object that appears on screen is ultimately represented by a Renderable.

Examples include

- waveform
- grid
- particles
- radar sweep
- holographic sphere
- HUD overlay
- text
- debugging primitives

Modules never submit Geometry directly.

Modules submit Renderables.

```
Module

↓

Renderable

↓

Frame

↓

Renderer

↓

GPU
```

---

# Philosophy

A Renderable answers one question:

> "How should this object appear?"

It combines

- geometry
- material
- transform
- GPU cache

into a single object.

It deliberately contains **no simulation logic**.

---

# Relationship to Modules

Modules own Renderables.

```
Module

↓

Renderable
```

The renderer only borrows them.

Ownership never changes.

---

# Relationship to Geometry

A Renderable references Geometry.

```
Renderable

↓

Geometry
```

Geometry describes

- vertices
- lines
- circles
- paths
- polygons

The Renderable describes how that geometry should be rendered.

---

# Relationship to Material

Every Renderable owns a Material.

```
Renderable

↓

Material
```

The Material describes appearance.

Examples

- color
- opacity
- blend mode

---

# Relationship to Transform

Every Renderable owns a Transform.

```
Renderable

↓

Transform
```

The Transform determines

- translation
- rotation
- scaling

---

# Relationship to Mesh

Every Renderable owns one Mesh.

```
Renderable

↓

Mesh
```

Unlike Geometry,

the Mesh is GPU-side.

The renderer updates it automatically.

Modules never touch it.

---

# Complete Structure

Conceptually a Renderable looks like

```python
Renderable

├── geometry

├── material

├── transform

├── mesh

├── cached_geometry

├── is_dirty

├── is_dynamic

└── is_visible
```

Each field has a specific responsibility.

---

# geometry

```python
renderable.geometry
```

Contains the logical geometry.

Examples

```
Polyline

Circle

Rectangle

Grid

Particles

Custom Geometry
```

Geometry lives entirely on the CPU.

---

# Example

```python
renderable.geometry = geometry
```

Changing Geometry does **not** immediately affect the GPU.

---

# cached_geometry

```python
renderable.cached_geometry
```

Used internally by the renderer.

Its purpose is to avoid rebuilding identical geometry.

Modules should generally ignore this field.

---

# material

```python
renderable.material
```

Describes appearance.

Typical fields include

```
Color

Opacity

Blend Mode

Line Width

Future Shader Parameters
```

Materials may be shared.

---

# transform

```python
renderable.transform
```

Stores spatial information.

Examples

```
Position

Rotation

Scale
```

Future versions may include full matrices.

---

# mesh

```python
renderable.mesh
```

Owns native GPU resources.

Internally

```
VAO

VBO

Vertex Count
```

Modules never upload vertices.

Modules never bind buffers.

The renderer manages the Mesh automatically.

---

# is_dirty

Probably the most important field.

```python
renderable.is_dirty
```

When

```
False
```

the renderer reuses existing GPU buffers.

When

```
True
```

geometry is rebuilt.

---

# Dirty Pipeline

```
Geometry Changed

↓

is_dirty = True

↓

Geometry Builder

↓

Vertex Buffer

↓

GPU Upload

↓

is_dirty = False
```

---

# Example

```python
renderable.geometry.points = points

renderable.is_dirty = True
```

Nothing else is required.

---

# is_dynamic

```python
renderable.is_dynamic
```

Indicates expected update frequency.

Typical values

```
True

↓

changes frequently
```

```
False

↓

mostly static
```

Future renderer optimizations may use this.

---

# is_visible

```python
renderable.is_visible
```

Current visibility flag.

Invisible Renderables may be skipped by the renderer.

Modules often control visibility simply by not submitting them.

---

# Construction

The default constructor creates every required object.

Conceptually

```python
Renderable()
```

automatically creates

```
Material

Transform

Mesh
```

The module only needs to provide Geometry.

---

# Typical Construction

```python
self.renderable = Renderable()
```

This happens once inside

```
__init__()
```

---

# Reuse

Renderables are designed to be reused.

Good

```python
self.renderable
```

Bad

```python
Renderable()
```

inside

```
build()
```

every frame.

---

# Typical Lifetime

```
Module Created

↓

Renderable Created

↓

Frame 1

↓

Frame 2

↓

Frame 3

↓

Application Exit
```

A Renderable usually lives for the lifetime of the module.

---

# Updating Geometry

Typical workflow

```python
self.renderable.geometry = geometry

self.renderable.is_dirty = True
```

The renderer performs the expensive work.

---

# Updating Material

Example

```python
renderable.material.color = (

    0.0,

    1.0,

    0.4

)
```

Changing material does not necessarily require rebuilding geometry.

---

# Updating Transform

Example

```python
renderable.transform.position = (

    100,

    200

)
```

Future renderer optimizations may avoid rebuilding geometry entirely.

---

# Sharing Materials

Multiple Renderables may share one Material.

```
Material

↓

Grid

↓

Wave

↓

Overlay
```

Useful for consistent coloring.

---

# Sharing Geometry

Possible,

but generally discouraged.

Geometry usually belongs to one Renderable.

---

# Sharing Meshes

Never.

Each Renderable owns exactly one Mesh.

---

# Relationship with the Frame

The Frame stores references to Renderables.

```
Frame

↓

Renderable

↓

Mesh
```

Destroying the Frame does not destroy the Renderable.

---

# Relationship with Geometry Builder

During rendering

```
Renderable

↓

Dirty?

↓

Geometry Builder

↓

Vertex Buffer

↓

Mesh Upload
```

This process is automatic.

---

# Renderer Responsibilities

The renderer

- checks dirty flags
- rebuilds geometry
- uploads buffers
- binds shaders
- issues draw calls

The module performs none of these tasks.

---

# Example

```python
class Wave(Module):

    def __init__(self):

        self.renderable = Renderable()
```

Later

```python
frame.add(

    self.renderable
)
```

That's the entire interaction.

---

# Multiple Renderables

Complex modules often own many.

```
Radar

↓

Grid

↓

Sweep

↓

Targets

↓

Overlay
```

Each is an independent Renderable.

---

# Static Geometry

Example

```
Background Grid
```

Created once.

Never changes.

```
is_dirty

↓

False
```

Renderer simply reuses the existing Mesh forever.

---

# Dynamic Geometry

Example

```
Audio Waveform
```

Changes every frame.

```
Geometry

↓

Dirty

↓

Rebuild

↓

Upload

↓

Draw
```

---

# Memory Ownership

```
Module

owns

↓

Renderable

owns

↓

Material

Transform

Mesh

references

↓

Geometry
```

Ownership is intentionally straightforward.

---

# Future Extensions

Future Renderables may additionally contain

```
Bounding Box

Layer

Visibility Mask

Picking ID

Instancing Information

LOD Information
```

The public API is designed to accommodate these without breaking existing modules.

---

# Best Practices

✔ Create Renderables once.

✔ Reuse them.

✔ Modify Geometry only when necessary.

✔ Mark dirty after Geometry changes.

✔ Let the renderer rebuild GPU resources.

✔ Keep simulation outside the Renderable.

---

# Anti-Patterns

Never

```python
glBindBuffer(...)
```

Never

```python
Mesh.draw()
```

Never

```python
glUseProgram(...)
```

Never

```python
glDrawArrays(...)
```

inside modules.

The Renderable is purely descriptive.

---

# Mental Model

Think of a Renderable as a finished blueprint.

Geometry defines the shape.

Material defines the paint.

Transform defines where it sits.

Mesh stores the manufactured hardware.

The renderer simply follows the blueprint.

---

# Example

A holographic sphere module may own

```python
self.sphere = Renderable()

self.grid = Renderable()

self.labels = Renderable()
```

During build

```python
frame.add(self.grid)

frame.add(self.sphere)

frame.add(self.labels)
```

The renderer transforms these three Renderables into GPU commands without the module ever touching OpenGL.

---

# Summary

The Renderable is the fundamental rendering object in Retroscope.

It combines Geometry, Material, Transform, and a cached GPU Mesh into a single reusable object.

Modules create Renderables once, update them as their simulation evolves, mark them dirty when geometry changes, and submit them to the current Frame.

The renderer handles everything else, making Renderables the clean boundary between procedural visualization code and the graphics backend.