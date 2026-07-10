# 00 - Overview

# Retroscope

## Introduction

Retroscope is a real-time procedural visualization engine designed for building oscilloscope-inspired graphics, scientific visualizations, holographic interfaces, audio-reactive art, particle systems, and experimental visual effects.

Unlike a traditional graphics engine or game engine, Retroscope is built around one central idea:

> **Everything is geometry.**

Modules do not render pixels.

Modules do not issue OpenGL commands.

Modules do not know about shaders, buffers, textures or GPU memory.

Instead, every module produces logical geometry.

The renderer is responsible for converting that geometry into GPU commands.

This separation is one of the fundamental design decisions of the project and is the reason the rendering backend has been almost completely rewritten in native C without affecting existing modules.

---

# Design Philosophy

Retroscope separates the engine into two completely independent worlds.

## Simulation

Simulation answers the question:

> What exists?

Examples:

- A sine wave
- A grid
- Snow particles
- A holographic sphere
- A radar sweep
- A DNA helix
- A galaxy
- A lightning bolt

Simulation is entirely implemented in Python.

Simulation knows nothing about OpenGL.

---

## Rendering

Rendering answers the question:

> How is it displayed?

Rendering owns:

- OpenGL
- Vertex buffers
- Meshes
- Shaders
- GPU uploads
- Draw calls
- Render passes

Rendering does not know why geometry exists.

It only knows how to display it.

---

# Separation of Responsibilities

The engine intentionally separates responsibilities into small independent systems.

```
Simulation
      │
      ▼
Geometry
      │
      ▼
Renderer
      │
      ▼
GPU
      │
      ▼
Display
```

Every stage has exactly one responsibility.

---

# What Retroscope Is Not

Retroscope is **not**:

- a game engine
- an immediate-mode graphics library
- a GUI toolkit
- a retained-mode scene graph
- a CAD system

Although it shares concepts with those systems, its primary purpose is procedural visualization.

---

# Core Principles

Every part of the engine follows a few important rules.

---

## Rule 1

Modules never call OpenGL.

OpenGL belongs exclusively inside the rendering backend.

A module should never import:

```
OpenGL.GL
```

or create GPU resources.

---

## Rule 2

Modules generate geometry.

They do not generate pixels.

For example:

```
Correct

Polyline
Circle
Arc
Spline
Grid
Particles
```

Not

```
Incorrect

glDrawArrays()

glBindBuffer()

glUniform()

glBufferData()
```

---

## Rule 3

The renderer is centralized.

There is only one renderer.

Individual modules never own renderers.

This keeps rendering deterministic and allows multiple modules to coexist.

---

## Rule 4

Data always flows forward.

```
Inputs

↓

Simulation

↓

Geometry

↓

Renderer

↓

Display
```

There is never any backward dependency.

The renderer never modifies simulation.

---

## Rule 5

Python describes.

Native executes.

Python is responsible for expressing ideas.

Native code is responsible for performance.

For example:

Python

```
Create a polyline.

Use this color.

Place it here.
```

Native

```
Generate triangles.

Upload vertices.

Bind buffers.

Draw.
```

---

# High-Level Architecture

The complete execution pipeline looks like this.

```
main.py

↓

App

↓

Module Manager

↓

Modules

↓

Frame

↓

Geometry Builder

↓

Render Graph

↓

Native Renderer

↓

GPU

↓

Display
```

Each stage is described below.

---

# Application

The application owns the lifetime of the program.

Responsibilities include:

- initialization
- window creation
- frame timing
- module updates
- renderer execution
- shutdown

There is only one application.

---

# Modules

Modules are where visualizations live.

Examples:

```
Wave

Grid

Audio

Snow

Particles

Radar

Galaxy

Lightning
```

Every module follows the same lifecycle.

```
update()

↓

build()
```

update()

simulates state.

build()

produces geometry.

Modules never communicate directly with the GPU.

---

# Frame

The Frame represents everything that should be rendered during the current frame.

Modules submit Renderables into the Frame.

The renderer later consumes the Frame.

The Frame is recreated every frame.

Think of it as a command buffer describing the current scene.

---

# Geometry

Geometry describes shapes.

Examples include:

- polylines
- circles
- splines
- rectangles
- polygons

Geometry is renderer-independent.

Geometry contains no OpenGL resources.

---

# Renderables

A Renderable combines geometry with visual appearance.

A Renderable owns:

- Geometry
- Material
- Transform
- Cached Mesh

It represents a single drawable object.

---

# Geometry Builder

The Geometry Builder converts logical geometry into triangles.

Example:

```
Polyline

↓

Stroke Builder

↓

Triangle Strip
```

This stage is responsible for tessellation.

---

# Vertex Buffer

The generated triangles are written into a native VertexBuffer.

The VertexBuffer owns:

- raw float memory
- capacity management
- resizing
- reuse

It exists entirely in native code.

Python never manipulates vertex memory directly.

---

# Mesh

A Mesh owns GPU resources.

Responsibilities:

- Vertex Array Object
- Vertex Buffer Object
- GPU uploads
- draw calls

Meshes are persistent.

Geometry is uploaded only when necessary.

---

# Shader

Shaders are compiled and linked by the renderer.

The renderer owns shader lifetime.

Modules never reference shader programs.

---

# Render Graph

Rendering is organized into passes.

Current example:

```
Geometry Pass
```

Future passes:

```
Shadow Pass

Bloom Pass

CRT Pass

Glow Pass

Overlay Pass

UI Pass
```

The Render Graph determines execution order.

---

# Native Backend

The rendering backend is implemented primarily in C.

Current native systems include:

- Stroke Builder
- VertexBuffer
- Mesh
- Shader

These systems execute nearly all expensive rendering operations.

Python performs orchestration only.

---

# Why Geometry?

Geometry provides several advantages.

## Renderer Independence

The same geometry could be rendered by:

- OpenGL ES
- OpenGL
- Vulkan
- Metal

without changing modules.

---

## Caching

Geometry can be cached.

Static objects do not need rebuilding every frame.

---

## Optimization

Geometry generation can be optimized independently of rendering.

---

## Flexibility

Different renderers may interpret the same geometry differently.

---

# Why Modules?

Modules make the engine composable.

Instead of one enormous visualization, Retroscope becomes a collection of independent systems.

Example:

```
Grid

+

Audio

+

Particles

+

Overlay

+

Radar
```

All rendered together.

Each module is unaware of the others.

---

# Why Native Rendering?

Python excels at expressing procedural algorithms.

C excels at executing repetitive work.

Examples of native work:

- tessellation
- vertex generation
- GPU uploads
- draw calls

Examples of Python work:

- procedural generation
- animation
- simulation
- composition

The result combines Python's productivity with native performance.

---

# Current Rendering Pipeline

Today, a single polyline follows this path.

```
Module

↓

Geometry

↓

Renderable

↓

Frame

↓

Geometry Builder

↓

Stroke Builder (native)

↓

VertexBuffer (native)

↓

Mesh (native)

↓

Shader (native)

↓

GPU

↓

Screen
```

Every visualization in Retroscope ultimately follows this pipeline.

---

# Long-Term Vision

Retroscope is not intended to be a single application.

It is intended to become a procedural visualization platform.

The long-term vision is a library of reusable visualization modules that can be combined to create entirely new scenes.

For example:

```
Microphone

↓

Audio Analysis

↓

Holographic Sphere

↓

Particle Field

↓

Lightning

↓

CRT Pipeline

↓

Display
```

Or

```
Physics Simulation

↓

Particle System

↓

Scientific Overlay

↓

Recording

↓

Video Export
```

The engine remains the same.

Only the modules change.

---

# Philosophy Summary

Retroscope is built on one simple principle:

> **Modules describe geometry. The renderer decides how that geometry reaches the screen.**

By keeping simulation independent from rendering, the engine remains portable, extensible, and highly optimized while allowing new visualizations to be developed rapidly without requiring any knowledge of graphics APIs or GPU programming.