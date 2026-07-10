# 24 - Complete Module Walkthrough

Version: 1.0

---

# Introduction

This document walks through the complete development of a Retroscope module from an empty Python file to a fully integrated visualization.

Unlike the previous SDK documents, which describe engine systems individually, this guide demonstrates how they work together in practice.

By the end of this walkthrough you will understand how to create a module that integrates naturally into the Retroscope engine while following its architectural principles.

This guide intentionally mirrors the style used by the built-in modules.

---

# What We're Building

For demonstration purposes we will create a simple visualization called

```
Ball
```

The visualization renders a circle in the center of the screen whose radius reacts to microphone input.

Although simple, it demonstrates almost every important engine concept.

It includes

- Module lifecycle
- Parameters
- Renderables
- Geometry
- Material
- Theme integration
- Audio reactivity
- Dirty flags
- Geometry generation
- Performance considerations

Once you understand this example, you can build virtually any visualization in Retroscope.

---

# Final Result

The finished module behaves like this.

```
Microphone

↓

RMS Level

↓

Ball Radius

↓

Geometry Rebuilt

↓

Renderer

↓

Display
```

The renderer, GPU uploads, and OpenGL are handled entirely by the engine.

The module simply generates geometry.

---

# Step 1 — Create the Module Directory

Create a new directory inside

```
modules/
```

Example

```
modules/

└── ball/

    ├── __init__.py

    └── module.py
```

Every visualization module follows this layout.

Future versions may include additional files for helper classes, generators, or simulation.

---

# Step 2 — Create the Module Class

Inside

```
module.py
```

Create the module.

```python
from core.module import Module


class Ball(Module):

    pass
```

This is the minimum valid Retroscope module.

At this point it does nothing.

---

# Step 3 — Construct the Module

Every module initializes its persistent state.

Example

```python
class Ball(Module):

    def __init__(self):

        super().__init__()
```

Always call the base class constructor.

Future engine versions may initialize internal systems here.

---

# Step 4 — Create Renderables

The visualization needs something to render.

Create a Renderable.

```python
from render.renderable import Renderable


self.ball = Renderable()
```

The Renderable becomes the permanent visual object owned by the module.

Create it once.

Reuse it forever.

---

# Step 5 — Register the Renderable

Modules contribute Renderables to the Frame.

Conceptually

```
Module

↓

Renderable

↓

Frame
```

During the build stage

```python
frame.add(

    self.ball
)
```

The renderer discovers Renderables exclusively through the Frame.

---

# Step 6 — Create Geometry

A Renderable references Geometry.

Conceptually

```
Renderable

↓

Geometry

↓

Primitives
```

Initially

```python
self.ball.cached_geometry = Geometry()
```

The Geometry object stores one or more primitives.

---

# Step 7 — Add a Primitive

Suppose the engine contains a Circle primitive.

Example

```python
Circle(

    center=(0,0),

    radius=0.25

)
```

The Geometry now contains one primitive.

Later

```
Geometry Builder

↓

Triangles

↓

GPU
```

---

# Step 8 — Configure the Material

Every Renderable owns a Material.

Example

```python
self.ball.material.color = (

    0,

    1,

    0

)
```

Eventually

```python
context.theme.primary
```

should replace literal colors.

---

# Step 9 — Initialize Simulation State

Modules own simulation.

Example

```python
self.radius = 0.25

self.phase = 0.0
```

Persistent state belongs inside the module.

Not inside the renderer.

---

# Step 10 — Add Parameters

Avoid hardcoded constants.

Instead

```python
self.speed = 1.0

self.max_radius = 0.5
```

Future versions become

```python
FloatParameter(...)
```

allowing UI editing.

---

# Step 11 — Update

The update stage modifies simulation.

Example

```python
def update(

    self,

    context,

    dt

):

    self.phase += dt
```

Nothing is rendered here.

Only simulation changes.

---

# Step 12 — Audio Reactivity

Suppose

```python
context.audio.rms
```

exists.

Update becomes

```python
self.radius = (

    0.2 +

    context.audio.rms * 0.4

)
```

The module reacts to sound without knowing anything about microphones.

---

# Step 13 — Mark Dirty

Changing geometry requires rebuilding.

Example

```python
self.ball.is_dirty = True
```

The renderer now knows the cached mesh is outdated.

---

# Step 14 — Build Geometry

The build stage generates primitives.

Conceptually

```python
Circle(

    radius=self.radius
)
```

Old geometry is replaced.

The Geometry Builder later converts it into triangles.

---

# Step 15 — Submit to Frame

Finally

```python
frame.add(

    self.ball
)
```

The module's work is finished.

---

# Complete Frame Flow

Every frame

```
Update

↓

Radius Changes

↓

Dirty

↓

Build Geometry

↓

Frame

↓

Renderer
```

The renderer handles everything afterwards.

---

# Theme Integration

Instead of

```python
(0,1,0)
```

use

```python
context.theme.primary
```

Changing themes automatically recolors the visualization.

---

# Animation

Time-based animation

```python
angle +=

speed *

dt
```

Avoid frame-dependent animation.

---

# Audio Example

Future

```python
energy =

context.audio.bass
```

Drive

- radius
- brightness
- particle count
- glow
- rotation

without changing the renderer.

---

# Transform

Instead of changing geometry,

sometimes only the Transform changes.

Example

```python
renderable.transform.position
```

This avoids rebuilding geometry.

Use geometry changes only when topology actually changes.

---

# Multiple Renderables

Complex modules often own multiple Renderables.

Example

```
Ball

Glow

Orbit

Particles
```

Each becomes

```
One Renderable
```

This allows independent Materials and Transforms.

---

# Layered Design

Instead of one giant object

```
Radar
```

prefer

```
Grid

↓

Sweep

↓

Targets

↓

Overlay
```

This produces much cleaner code.

---

# Dirty Strategy

Good

```
Radius Changes

↓

Dirty
```

Bad

```
Always Dirty
```

The latter rebuilds geometry unnecessarily.

---

# Common Mistakes

## Recreating Renderables

Bad

```python
Renderable()
```

every frame.

Good

```
Create Once

↓

Reuse
```

---

## Importing OpenGL

Never

```python
glDrawArrays()
```

inside a module.

---

## GPU Knowledge

Modules should not know about

```
Mesh

VBO

VAO

Shader
```

Those belong to the renderer.

---

## Hardcoded Colors

Bad

```python
(0,1,0)
```

Good

```python
theme.primary
```

---

## Mixing Update and Build

Bad

```
Update

↓

Generate Geometry
```

Good

```
Update

↓

State

Build

↓

Geometry
```

Keep responsibilities separate.

---

# Performance Tips

✔ Create Renderables once.

✔ Reuse Geometry where possible.

✔ Mark dirty only when necessary.

✔ Avoid temporary allocations.

✔ Store persistent state.

✔ Keep update lightweight.

---

# Scaling Up

Exactly the same architecture supports

```
Snow

Particles

Radar

Jarvis Globe

DNA

Force Fields

Sand

Galaxies
```

Only the geometry generation becomes more sophisticated.

The engine remains unchanged.

---

# Testing

Before integrating a complex visualization,

prototype the mathematics independently.

Examples

```
FFT Viewer

↓

Particle Sandbox

↓

Noise Generator

↓

Flow Field
```

Once correct,

move the algorithm into a Module.

---

# Module Checklist

Before committing a new module, verify

- Does it inherit from `Module`?
- Are Renderables persistent?
- Are colors obtained from the Theme?
- Is animation driven by `dt`?
- Does it avoid OpenGL calls?
- Does it expose configurable parameters?
- Does it rebuild geometry only when necessary?
- Does it keep simulation separate from rendering?
- Does it avoid unnecessary allocations?
- Does it integrate cleanly with the Frame?

If the answer is "yes" to all of these, the module follows Retroscope's architecture.

---

# Mental Model

A Retroscope module is like a scientist describing an experiment.

The scientist defines

- equations
- parameters
- initial conditions

The laboratory performs the experiment.

Similarly,

the module defines geometry and behavior.

The engine performs rendering, GPU management, optimization, and presentation.

Keeping these responsibilities separate is the key to writing modules that remain clean, reusable, and future-proof.

---

# Summary

This walkthrough demonstrates the complete lifecycle of a Retroscope visualization module, from creation through simulation, geometry generation, and rendering.

By focusing solely on procedural geometry and engine-facing abstractions such as Renderables, Geometry, Materials, and Context, modules remain independent of rendering implementation details. This allows the same module to benefit automatically from future engine improvements—including new render passes, native optimizations, themes, audio analysis, and platform support—without requiring any changes to the module itself.

For most visualization developers, this document should serve as the primary practical reference for writing new Retroscope modules.