# 04 - Frame API

Version: 1.0

---

# Introduction

The **Frame** is the scene description produced during every render cycle.

A module does not render directly.

Instead, it contributes Renderables to the current Frame.

The renderer later consumes that Frame and converts it into GPU draw calls.

The Frame is therefore the bridge between simulation and rendering.

```
Module

↓

Frame

↓

Renderer

↓

GPU
```

The Frame contains **what should be rendered**, not **how to render it**.

---

# Philosophy

Think of the Frame as a shopping basket.

Modules place Renderables into the basket.

The renderer later checks out everything inside it.

Modules never render immediately.

Instead they simply describe the scene.

---

# Ownership

The Frame is owned by the Application.

```
Application

↓

Frame

↓

Renderer
```

Modules never construct Frames.

Modules never destroy Frames.

---

# Lifetime

Unlike Context,

the Frame is temporary.

```
Frame N

↓

Build

↓

Render

↓

Destroy

↓

Frame N+1

↓

Build

↓

Render

↓

Destroy
```

A new Frame is created every render cycle.

Nothing inside a Frame should survive into the next frame.

---

# Responsibilities

A Frame is responsible for

- collecting Renderables
- preserving render order
- representing one complete scene

A Frame is **not** responsible for

- OpenGL
- shaders
- meshes
- GPU uploads
- rendering

---

# Current Structure

Conceptually,

the Frame is extremely small.

```python
Frame

└── renderables
```

That simplicity is intentional.

---

# Renderables

Internally,

a Frame stores an ordered collection of Renderables.

Conceptually

```python
frame.renderables
```

contains

```
Grid

Wave

Particles

Overlay

Text
```

The renderer walks this list sequentially.

---

# Primary API

The single most important method is

```python
frame.add(...)
```

Every visualization module uses this method.

---

# Example

```python
frame.add(

    self.renderable

)
```

This schedules one Renderable for rendering.

Nothing is drawn immediately.

---

# Multiple Renderables

Modules may submit as many Renderables as needed.

```python
frame.add(

    self.grid

)

frame.add(

    self.wave

)

frame.add(

    self.overlay

)
```

This is extremely common.

---

# Render Order

Renderables are rendered in the order they are added.

Example

```python
frame.add(grid)

frame.add(wave)

frame.add(text)
```

Execution becomes

```
Grid

↓

Wave

↓

Text
```

Later Renderables appear on top of earlier ones.

---

# Layering

Current layering is simply insertion order.

```
First Added

↓

Bottom

↓

...

↓

Last Added

↓

Top
```

Future versions may expose explicit render layers.

---

# Example

A radar visualization might generate

```
Background Grid

↓

Radar Sweep

↓

Detected Targets

↓

HUD

↓

Labels
```

Each element is its own Renderable.

---

# Empty Frames

A Frame may legally contain zero Renderables.

```
Frame

↓

Renderer

↓

Nothing Drawn
```

No special handling is required.

---

# Duplicate Renderables

The same Renderable may be submitted multiple times.

```python
frame.add(

    self.cursor

)

frame.add(

    self.cursor

)
```

Although possible,

this is rarely useful.

---

# Shared Renderables

Multiple modules generally should **not** share Renderables.

Instead,

each module owns its own objects.

This simplifies ownership.

---

# Removal

Renderables are never removed from a Frame.

Instead,

the Frame is discarded after rendering.

Next frame,

modules simply choose not to add an object.

Example

Frame N

```
Grid

Wave
```

Frame N+1

```
Grid
```

The Wave simply disappears.

---

# Visibility

Modules control visibility by choosing whether to submit a Renderable.

Instead of

```python
renderable.visible = False
```

the module simply omits

```python
frame.add(...)
```

---

# Dynamic Scenes

Because a new Frame is built every render cycle,

dynamic scenes are naturally supported.

Example

```
Frame 1

↓

100 particles

Frame 2

↓

120 particles

Frame 3

↓

94 particles
```

No cleanup is required.

---

# Static Scenes

Static geometry works exactly the same way.

The module simply keeps submitting the same Renderable.

The renderer recognizes that nothing changed.

```
Renderable

↓

Dirty?

↓

No

↓

Reuse Mesh
```

This minimizes GPU work.

---

# Dirty Flags

The Frame itself does not track dirty state.

Dirty tracking belongs to the Renderable.

```
Renderable

↓

is_dirty

↓

Geometry Builder
```

---

# Memory Ownership

The Frame does **not** own Renderables.

Modules own them.

The Frame only stores references.

```
Module

↓

Renderable

↓

Frame Reference
```

Destroying a Frame does not destroy any Renderables.

---

# Typical Usage

Every build() function follows the same pattern.

```python
def build(

    self,

    frame,

):

    frame.add(

        self.renderable

    )
```

This is the canonical Retroscope rendering API.

---

# Large Modules

Complex modules typically own many Renderables.

Example

```
Planet

↓

Atmosphere

↓

Clouds

↓

Lightning

↓

Labels

↓

Debug Overlay
```

Each becomes

```python
frame.add(...)
```

---

# Example

```python
frame.add(

    self.planet

)

frame.add(

    self.clouds

)

frame.add(

    self.labels
)
```

---

# Iteration

The renderer later performs something conceptually similar to

```python
for renderable in frame.renderables:

    render(renderable)
```

Modules never perform this iteration.

---

# Scene Graph?

Notice what the Frame is **not**.

It is **not** a scene graph.

There are no

- parent nodes
- child nodes
- transforms
- hierarchies

The Frame is intentionally flat.

---

# Why Flat?

Flat structures are

- faster
- simpler
- easier to debug
- cache friendly

Complex hierarchy belongs inside modules,

not inside the renderer.

---

# Rebuilding Every Frame

A common question is

> Why rebuild the Frame every frame?

Because scene generation is cheap.

GPU work is expensive.

The renderer automatically caches expensive GPU objects.

Modules therefore remain simple.

---

# Typical Pipeline

Every frame follows the same sequence.

```
Frame Created

↓

Modules Build Scene

↓

Frame Complete

↓

Renderer Executes

↓

Frame Destroyed
```

---

# Interaction with Context

Context is persistent.

Frame is temporary.

```
Context

↓

update()

↓

Frame

↓

build()

↓

Renderer
```

Modules receive both,

but they serve completely different purposes.

---

# Interaction with Renderables

Modules own Renderables.

The Frame references them.

The renderer consumes them.

```
Module

↓

Renderable

↓

Frame

↓

Renderer
```

Ownership never changes.

---

# Interaction with Geometry

Geometry is never added directly.

Incorrect

```python
frame.add(

    geometry

)
```

Correct

```python
frame.add(

    renderable

)
```

The renderer understands Renderables,

not raw Geometry.

---

# Interaction with Materials

Likewise,

Materials are attached to Renderables.

Never

```python
frame.add(

    material

)
```

Instead

```
Renderable

↓

Material

↓

Frame
```

---

# Future Extensions

The Frame may eventually support

```python
frame.clear()

frame.reserve()

frame.sort()

frame.statistics()
```

These are renderer conveniences.

Modules should rarely need them.

---

# Best Practices

✔ Keep Renderables alive.

✔ Reuse them every frame.

✔ Add only what should be visible.

✔ Let insertion order determine layering.

✔ Avoid allocations during build().

---

# Anti-Patterns

Never

```python
Frame()
```

inside a module.

Never

```python
Renderer.render(...)
```

Never

```python
glDrawArrays(...)
```

Never

```python
Mesh.draw(...)
```

Modules only describe the scene.

---

# Mental Model

Imagine a movie production.

Each module hands the director a list of actors that should appear in the next shot.

The Frame is that list.

The renderer is the camera crew.

The GPU is the cinema projector.

The Frame itself never performs any rendering—it simply describes the scene.

---

# Example

A simple waveform module may build the Frame like this.

```python
def build(

    self,

    frame,

):

    frame.add(

        self.grid

    )

    frame.add(

        self.wave

    )

    frame.add(

        self.overlay

    )
```

The renderer later draws

```
Grid

↓

Wave

↓

Overlay
```

exactly in that order.

---

# Summary

The Frame is the transient scene container used during every render cycle.

Modules populate it with Renderables.

The renderer later consumes those Renderables, rebuilds dirty geometry when necessary, uploads data to the GPU, and finally renders the completed scene.

The Frame deliberately contains almost no logic. Its job is simply to answer one question:

> **"What should be rendered this frame?"**

Everything else belongs elsewhere in the engine.