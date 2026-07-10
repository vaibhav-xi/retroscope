# 11 - Renderer API

Version: 1.0

---

# Introduction

The Renderer is responsible for converting the abstract scene produced by modules into pixels on the screen.

It is the final stage of the Retroscope pipeline.

Modules never communicate with OpenGL directly.

Instead, every module contributes Renderables to a Frame.

The Renderer consumes the Frame and produces the final image.

```
Modules

↓

Frame

↓

Geometry Builder

↓

Render Packet

↓

Render Graph

↓

Render Passes

↓

OpenGL

↓

Display
```

The Renderer is intentionally ignorant of where geometry originated.

It simply renders what it receives.

---

# Philosophy

The Renderer has one responsibility:

> Draw the current frame.

It should never contain

- simulation
- module logic
- procedural generation
- audio processing
- input handling

Those belong elsewhere.

The Renderer is purely a rendering system.

---

# High-Level Responsibilities

The renderer performs the following work every frame.

```
Clear screen

↓

Build geometry

↓

Execute render graph

↓

Present image
```

Everything else in the application exists to feed these steps.

---

# Current Implementation

Current implementation lives in

```
render_es2/

renderer.py
```

This file owns the rendering pipeline.

---

# Initialization

During startup the renderer creates

```
Shader

↓

Profiler

↓

RenderGraph

↓

GeometryPass
```

This initialization occurs only once.

The render loop itself is extremely small.

---

# Current Render Loop

Conceptually

```python
render(frame)
```

performs

```
glClear()

↓

GeometryBuilder.build()

↓

RenderGraph.execute()
```

Nothing more.

---

# Stage 1

Clear

```
glClear()

↓

Color Buffer
```

Every frame begins with a clean framebuffer.

Future versions may clear

- depth
- stencil
- offscreen targets

---

# Stage 2

Geometry Build

The renderer invokes

```
GeometryBuilder.build(frame)
```

The builder converts

```
Geometry

↓

Vertex Buffers

↓

Meshes
```

Only dirty Renderables are rebuilt.

---

# Stage 3

Render Packet

The Geometry Builder produces

```
RenderPacket
```

Conceptually

```
Frame

↓

Render Packet
```

The packet contains everything required to render the scene.

---

# Stage 4

Render Graph

The Render Packet is submitted to

```
RenderGraph.execute()
```

The Render Graph determines

- pass ordering
- dependencies
- rendering sequence

---

# Stage 5

Geometry Pass

Current engine executes

```
GeometryPass
```

This pass renders

all visible Renderables.

---

# Geometry Pass

For each Renderable

```
Shader.use()

↓

Shader.set_color()

↓

Mesh.draw()
```

Notice what does **not** happen.

No geometry generation.

No OpenGL buffer uploads.

Those already occurred.

---

# Draw Order

Current draw order is

```
Frame

↓

Renderable 1

↓

Renderable 2

↓

Renderable 3
```

Future versions may introduce explicit layers.

---

# Visibility

Invisible Renderables are skipped.

Conceptually

```
Renderable

↓

is_visible

↓

Draw?

↓

Yes / No
```

No Mesh upload occurs.

No draw call occurs.

---

# Dirty Objects

Dirty Renderables are rebuilt before drawing.

Clean Renderables reuse their Mesh.

```
Dirty

↓

Geometry Builder

↓

Upload

↓

Draw
```

versus

```
Clean

↓

Draw
```

This dramatically reduces CPU work.

---

# Renderer Ownership

The renderer owns

```
Shader

Render Graph

Profiler
```

The renderer does **not** own

```
Modules

Geometry

Frame

Scene Logic
```

---

# Renderer Independence

The renderer does not know

```
Grid

Wave

Particles

Audio

Radar
```

Every object is simply

```
Renderable
```

This allows entirely new visualization modules without renderer changes.

---

# Current Shader Usage

Today's renderer uses one shader.

```
Simple Shader
```

Every object shares it.

Future renderers may support

- material shaders
- custom shaders
- multipass rendering

---

# Native Rendering

Significant portions of rendering have already moved into native C.

Current native objects include

```
Mesh

Shader

VertexBuffer

Stroke Builder
```

The Python renderer coordinates these objects.

The heavy work occurs natively.

---

# Render Graph

Instead of hardcoding rendering,

the renderer delegates work to

```
Render Graph
```

This makes future rendering techniques much easier.

---

# Why A Render Graph?

Instead of

```
Geometry

↓

Bloom

↓

CRT

↓

UI
```

being hardcoded,

each stage becomes an independent pass.

Future pipelines become

```
Geometry

↓

Bloom

↓

Persistence

↓

CRT

↓

Post FX

↓

UI
```

without modifying Renderer itself.

---

# Current Pass List

Today

```
GeometryPass
```

Future

```
ShadowPass

↓

GeometryPass

↓

GlowPass

↓

PersistencePass

↓

BloomPass

↓

CRTPass

↓

OverlayPass

↓

UIPass
```

---

# Profiler Integration

The renderer profiles major stages.

Current samples include

```
GeometryBuilder

RenderGraph
```

Future versions may profile individual passes.

---

# Platform Independence

The renderer intentionally avoids

platform-specific code.

Platform abstraction occurs lower,

inside

```
gl_platform.h

Mesh

Shader
```

Renderer code remains identical on

- macOS

- Raspberry Pi

- Linux

---

# OpenGL Knowledge

The renderer knows

```
Shaders

Meshes

Framebuffers
```

Modules know none of these.

This is intentional.

---

# Performance Goals

Current renderer emphasizes

- minimal Python overhead
- persistent GPU objects
- native geometry generation
- minimal allocations
- reusable meshes

These design goals are especially important on Raspberry Pi.

---

# Future Features

The renderer architecture already supports

- deferred rendering
- HDR
- bloom
- CRT effects
- temporal persistence
- offscreen rendering
- multiple framebuffers
- multisampling

Most of these only require new render passes.

---

# Module Perspective

From a module's point of view,

the renderer is invisible.

A module simply does

```
Create Geometry

↓

Mark Dirty

↓

Done
```

The renderer handles everything else.

---

# Data Flow

Complete data flow

```
Module

↓

Primitive

↓

Geometry

↓

Renderable

↓

Frame

↓

Geometry Builder

↓

Vertex Buffer

↓

Mesh

↓

Render Packet

↓

Render Graph

↓

Geometry Pass

↓

Shader

↓

OpenGL

↓

Screen
```

Every stage has a single responsibility.

---

# Things Modules Should Never Do

Modules should never

```python
glDrawArrays()
```

Never

```python
glBindBuffer()
```

Never

```python
glUseProgram()
```

Never

```python
glUniform3f()
```

Never

```python
glClear()
```

Those are renderer responsibilities.

---

# Mental Model

Think of the renderer as the projection booth in a movie theater.

Modules create the film.

The renderer projects it.

The projector doesn't know whether the movie is

- science fiction
- documentary
- animation

It simply projects frames.

Likewise,

Retroscope's renderer doesn't know whether a Renderable represents

- a waveform
- particles
- a radar
- a hologram
- snowfall

It simply renders Renderables.

---

# Future Direction

The renderer is intentionally becoming thinner over time.

More work continues moving into native code.

Already migrated

✔ Stroke generation

✔ Vertex buffers

✔ Meshes

✔ Shader management

Future candidates include

- render passes
- framebuffers
- textures
- post-processing

The Python renderer will increasingly orchestrate rather than execute.

---

# Summary

The Renderer is the execution engine of Retroscope's graphics pipeline.

It transforms the abstract scene assembled by modules into pixels by coordinating geometry generation, render passes, shaders, and GPU resources.

Modules never interact with it directly. They simply describe what should exist in the scene. The renderer determines how that scene is efficiently built, cached, and displayed.

This strict separation between scene generation and rendering is one of the core architectural principles of Retroscope and is what allows the engine to scale from simple oscilloscope traces to complex real-time procedural visualizations without changing the module API.