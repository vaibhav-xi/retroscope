# 08 - Frame

# Introduction

The Frame represents **everything that should be rendered during the current frame**.

It is one of the central abstractions of Retroscope.

Modules never communicate directly with the renderer.

Instead, they receive a Frame and populate it with Renderables.

```
Module

↓

Frame

↓

Renderer
```

The Frame acts as a temporary scene description.

It does not render anything.

It merely describes **what should appear on the screen**.

---

# Philosophy

Think of the Frame as a shopping basket.

Each module contributes items.

```
Wave

↓

Renderable
```

```
Grid

↓

Renderable
```

```
Particles

↓

Renderable
```

Everything goes into the same basket.

Only after every module has finished does the renderer consume the basket.

---

# Why Does Frame Exist?

Without a Frame, modules would call the renderer directly.

For example

```
module.draw()

↓

OpenGL
```

This tightly couples simulation with rendering.

Instead

```
Module

↓

Frame

↓

Renderer
```

Modules become completely independent of the graphics backend.

---

# One Frame Per Refresh

Every display refresh creates a new Frame.

```
Create Frame

↓

Modules populate it

↓

Renderer consumes it

↓

Frame discarded
```

The next refresh starts with a brand new Frame.

---

# Ownership

The Application owns the Frame.

```
Application

↓

Frame

↓

Modules
```

Modules never create Frames themselves.

---

# Frame Lifetime

A Frame exists for exactly one render cycle.

```
Frame()

↓

build()

↓

render()

↓

destroy
```

The next frame starts empty.

---

# Empty by Default

When created,

a Frame contains nothing.

```
Frame

└── Renderables = []
```

Modules fill this list.

---

# Adding Geometry

Modules contribute Renderables.

Example

```python
frame.add(renderable)
```

This is the primary responsibility of build().

---

# Multiple Objects

A module may submit one object.

```
Wave
```

or hundreds.

```
Particles

↓

500 Renderables
```

The Frame simply stores them.

---

# Multiple Modules

Every module contributes to the same Frame.

```
Frame

├── Grid

├── Wave

├── Snow

├── Audio

├── Overlay

└── Cursor
```

The renderer processes them together.

---

# Order

Today,

Renderables appear in the order they are submitted.

```
Grid

↓

Wave

↓

Overlay
```

Future versions may support explicit render layers.

---

# The Frame Does Not Render

The Frame has no knowledge of

- OpenGL
- GPU buffers
- shaders
- draw calls

It simply stores Renderables.

---

# Scene Description

Another way to think about a Frame is

```
Current Scene
```

The renderer receives

```
Frame

↓

Draw Everything
```

---

# Immutability During Rendering

After modules finish building,

the Frame should be treated as read-only.

```
Modules

↓

Finished

↓

Renderer
```

The renderer assumes the Frame no longer changes.

---

# Typical Lifecycle

Every frame follows the same sequence.

```
Create Frame

↓

Module A

↓

frame.add(...)

↓

Module B

↓

frame.add(...)

↓

Module C

↓

frame.add(...)

↓

Renderer

↓

Destroy Frame
```

---

# Relationship To Modules

Modules never own the Frame.

They receive it temporarily.

```
build(frame)
```

Their only responsibility is

```
frame.add(...)
```

Nothing more.

---

# Relationship To Renderables

The Frame stores Renderables.

```
Frame

├── Renderable

├── Renderable

├── Renderable
```

The renderer iterates over this collection.

---

# Relationship To Geometry

Geometry is always contained inside a Renderable.

Therefore

```
Frame

↓

Renderable

↓

Geometry
```

The Frame never stores raw primitives.

---

# Memory

Frames are lightweight.

They own references,

not GPU resources.

The expensive objects remain cached elsewhere.

---

# Why Rebuild Every Frame?

It may seem wasteful to create a new Frame every refresh.

However,

the Frame contains only scene structure.

GPU resources are reused.

Meshes are cached.

Shaders are cached.

Vertex buffers are reused.

The Frame itself remains inexpensive.

---

# Dirty Objects

Suppose a waveform changes.

```
Renderable

↓

Dirty

↓

Geometry rebuilt
```

Suppose a grid remains unchanged.

```
Renderable

↓

Clean

↓

Reuse Mesh
```

The Frame doesn't care.

It simply stores both.

---

# Static And Dynamic Objects

The Frame may contain both.

```
Grid

↓

Static
```

```
Wave

↓

Dynamic
```

The renderer determines which objects require rebuilding.

---

# Future Render Layers

Future versions may extend the Frame.

Example

```
Frame

├── Background

├── Geometry

├── Particles

├── Overlay

└── UI
```

Modules remain unchanged.

---

# Future Cameras

Eventually

```
Frame

↓

Camera

↓

Renderer
```

The Frame may reference one or more Cameras.

Again,

modules continue submitting Renderables exactly as before.

---

# Future Multiple Viewports

One Frame could eventually produce

```
Main Display

Mini Map

Mirror

VR Eye
```

The Frame remains the same.

Only rendering changes.

---

# Future Offscreen Rendering

The renderer may later render a Frame into

```
Texture

↓

CRT

↓

Bloom

↓

Display
```

Modules remain unaware.

---

# Debugging

Because every visible object passes through the Frame,

it becomes an excellent debugging point.

Examples

```
Frame

↓

12 Renderables
```

```
Frame

↓

No Geometry
```

```
Frame

↓

Unexpected Object
```

The renderer simply consumes whatever the Frame contains.

---

# Best Practices

Modules should

- submit complete Renderables
- never cache Frames
- never modify the Frame after build()
- avoid depending on submission order

---

# Example

```python
def build(self, frame):

    geometry = Geometry(...)

    renderable = Renderable(

        geometry=geometry,

        material=self.material,

        transform=self.transform,

    )

    frame.add(renderable)
```

Notice

- no renderer
- no OpenGL
- no GPU
- no shaders

Only scene description.

---

# Mental Model

Imagine a theatre.

Actors (Modules) prepare for a performance.

Each actor walks backstage and places their props on a shared stage list.

The Stage Manager (Frame) simply records

```
Place chair.

Place table.

Place spotlight.

Place actor.
```

Only after every actor has finished does the crew (Renderer) build the stage and begin the performance.

The Frame never performs.

It only records what should be performed.

---

# Summary

The Frame is a temporary scene description created once per render cycle.

Modules populate the Frame by submitting Renderables.

The renderer later consumes the Frame and performs all rendering.

This separation allows modules to remain completely independent from the graphics backend while giving the renderer complete freedom to optimize rendering, caching, batching, and future rendering techniques without changing module code.

The Frame is the contract between simulation and rendering.

It answers one question:

> **What should exist on the screen during this frame?**