# 01 - Engine Overview

---

# Introduction

Retroscope is built around a deliberately simple architecture.

Unlike traditional game engines, there is no scene graph, no entity-component system, no scripting VM, and no complex asset pipeline.

Instead, every frame is generated procedurally from a collection of visualization modules.

Those modules describe **what should exist**.

The renderer decides **how to render it**.

This separation is the core architectural principle of the engine.

---

# The Entire Engine

At the highest level, the engine consists of only a handful of major systems.

```
                    User

                      │

                      ▼

                 Application

                      │

      ┌───────────────┴───────────────┐

      ▼                               ▼

  Input System                 Module Manager

                                      │

                                      ▼

                             Visualization Modules

                                      │

                                      ▼

                                   Frame

                                      │

                                      ▼

                                Renderables

                                      │

                                      ▼

                             Geometry Builder

                                      │

                                      ▼

                              Native Pipeline

                                      │

                                      ▼

                                 GPU Meshes

                                      │

                                      ▼

                                Render Graph

                                      │

                                      ▼

                                  OpenGL

                                      │

                                      ▼

                                  Display
```

Everything inside Retroscope ultimately participates in this pipeline.

---

# Directory Layout

The project is intentionally organized into small independent packages.

```
core/

inputs/

modules/

render/

render_es2/

themes/

services/

ui/

assets/
```

Each directory has exactly one responsibility.

---

# core/

The **core** package contains the application itself.

Think of it as the operating system of Retroscope.

It is responsible for

- application lifecycle
- window management
- frame timing
- module execution
- context creation
- render scheduling

The core package does **not** generate visuals.

Instead, it coordinates every other subsystem.

---

# render/

The render package defines the engine's rendering abstractions.

These are high-level concepts.

Examples include

```
Renderable

Primitive

Transform
```

Nothing inside this package talks directly to OpenGL.

Instead, it defines data structures used by the renderer.

---

# render_es2/

This is the actual rendering backend.

It is responsible for converting Renderables into pixels.

Its responsibilities include

- geometry generation
- vertex buffering
- shaders
- meshes
- renderer
- render graph
- render passes

Unlike render/,

this package owns GPU resources.

---

# render_es2/_native/

This is the native acceleration layer.

It is implemented in C.

Current native systems include

```
Stroke Builder

Geometry

Vertex Buffer

Mesh

Shader
```

Its goal is simple.

Move computationally expensive operations out of Python.

---

# modules/

Everything visible on screen ultimately originates from a module.

Examples

```
Grid

Wave

Overlay

Audio
```

Modules generate Renderables.

Modules never perform rendering.

---

# inputs/

This package contains hardware interfaces.

Examples

```
Keyboard

Mouse

Touch

GPIO

Audio
```

These systems collect information from the outside world.

Modules consume this information through Context.

---

# themes/

Themes define appearance.

They provide

- colors
- palettes
- styling

Changing a theme changes the appearance of every module without changing module code.

---

# services/

Services provide infrastructure.

Examples

```
Logger

Profiler

Recorder

Screenshot

Settings
```

Services are shared across the entire engine.

---

# ui/

Future user interfaces live here.

Examples

```
Web UI

WebSocket

REST API
```

Visualization modules remain completely independent from the UI.

---

# assets/

Contains external resources.

Examples

```
Fonts

Images

Sounds
```

Retroscope intentionally relies far less on assets than traditional engines.

Geometry is generated procedurally whenever possible.

---

# The Main Loop

The application repeatedly executes the same sequence.

```
Initialize

↓

Loop

↓

Read Inputs

↓

Update Modules

↓

Build Frame

↓

Render Frame

↓

Present

↓

Repeat
```

This loop continues until the application exits.

---

# Startup Sequence

The startup process is deterministic.

```
main.py

↓

App()

↓

Window

↓

OpenGL Context

↓

Renderer

↓

Context

↓

Modules

↓

Run Loop
```

Every subsystem is initialized exactly once.

---

# Shutdown Sequence

Shutdown occurs in reverse order.

```
Stop Loop

↓

Destroy Modules

↓

Release GPU Resources

↓

Destroy Window

↓

Exit
```

Native resources are released before the application terminates.

---

# Frame Flow

The frame pipeline is the heart of Retroscope.

```
Frame N

↓

Modules Update

↓

Modules Build

↓

Renderer

↓

GPU

↓

Display
```

This sequence repeats approximately sixty times per second.

---

# Simulation vs Rendering

Retroscope intentionally separates simulation from rendering.

Simulation

```
Wave Position

Particle Motion

Audio Analysis
```

Rendering

```
Geometry

GPU Upload

Draw
```

This separation makes the engine significantly easier to maintain.

---

# Visualization Pipeline

Every visualization follows the same path.

```
Audio

↓

Module

↓

Renderable

↓

Geometry

↓

Vertex Buffer

↓

Mesh

↓

GPU

↓

Display
```

Every module, regardless of complexity, follows this pipeline.

---

# Data Flow

Information flows in one direction.

```
Input

↓

Context

↓

Modules

↓

Frame

↓

Renderer

↓

Display
```

The renderer never modifies module state.

Modules never modify renderer state.

---

# Ownership Hierarchy

Ownership is intentionally simple.

```
Application

owns

↓

Context

Renderer

Module Manager

Services

Window
```

The Module Manager owns

```
Modules
```

Modules create

```
Renderables
```

Renderables own

```
Geometry

Material

Transform

Mesh
```

Meshes own

```
GPU Buffers
```

This ownership model avoids ambiguity.

---

# The Rendering Backend

The renderer is internally composed of several layers.

```
Renderer

↓

Render Graph

↓

Render Pass

↓

Geometry Builder

↓

Mesh

↓

Shader

↓

OpenGL
```

Each layer has one responsibility.

---

# Why A Render Graph?

The Render Graph allows rendering to evolve without affecting modules.

Today

```
Geometry Pass
```

Tomorrow

```
Geometry

↓

Bloom

↓

CRT

↓

Persistence

↓

Overlay
```

Modules remain unchanged.

---

# Native Pipeline

Python performs orchestration.

Native C performs heavy computation.

```
Python

↓

Geometry Request

↓

Native Builder

↓

Vertex Buffer

↓

Mesh Upload

↓

GPU
```

This architecture keeps Python code clean while achieving native performance.

---

# Current Native Components

Today the native layer contains

```
Stroke Builder

VertexBuffer

Mesh

Shader

GPU Upload
```

Future additions may include

- instancing
- batching
- texture management
- framebuffer management

---

# Module Isolation

Modules are intentionally isolated.

A module cannot directly access another module.

Instead,

communication occurs through

```
Context

Signals

Shared Services
```

This prevents tight coupling.

---

# Memory Lifetime

Retroscope distinguishes between temporary and persistent objects.

Temporary

```
Frame

Geometry

Scratch Buffers
```

Persistent

```
Modules

Meshes

Shaders

Themes

Services
```

Understanding object lifetime is essential for writing efficient modules.

---

# CPU vs GPU

The engine clearly separates CPU objects from GPU objects.

CPU

```
Geometry

Renderable

Frame

Context
```

GPU

```
Mesh

Shader

Buffer

Vertex Array
```

Modules operate almost exclusively on CPU-side objects.

---

# Dirty Objects

To avoid unnecessary work,

Renderables maintain dirty state.

```
Geometry Changed

↓

Dirty

↓

Rebuild Mesh

↓

Upload

↓

Clean
```

Static geometry remains cached.

---

# Platform Abstraction

The renderer supports multiple OpenGL implementations.

```
macOS

↓

Desktop OpenGL
```

```
Raspberry Pi

↓

OpenGL ES 2.0
```

Differences are hidden behind

```
gl_platform.h
```

Visualization code remains identical.

---

# Current Optimization Strategy

Performance is achieved through

- native geometry generation
- persistent GPU buffers
- dirty flags
- cached meshes
- minimal Python allocations

Rather than relying on one large optimization,

the engine combines many small optimizations.

---

# Design Principles

Throughout the engine, the following principles appear repeatedly.

Single Responsibility

Data-Oriented Design

Ownership Clarity

Minimal Hidden State

Platform Independence

Predictable Lifetime

These principles guide every subsystem.

---

# Reading The Source

Developers are encouraged to read the engine in roughly this order.

```
main.py

↓

core/app.py

↓

core/module.py

↓

core/frame.py

↓

render/renderable.py

↓

render/primitives.py

↓

render_es2/geometry_builder.py

↓

render_es2/renderer.py

↓

render_es2/_native/
```

This follows the same path taken by a frame.

---

# Mental Model

Imagine a factory.

Modules manufacture parts.

The Frame collects them.

The Geometry Builder assembles them.

The Mesh uploads them.

The Renderer paints them.

The GPU displays them.

Every subsystem has one station in the production line.

No station attempts to perform another station's work.

---

# Summary

Retroscope is intentionally built from a small number of focused systems.

The core package manages execution.

Modules generate procedural content.

The Frame collects that content.

Renderables describe what should be drawn.

The renderer converts those descriptions into GPU commands.

Native code accelerates expensive operations.

The GPU finally produces the image seen on screen.

Every feature in Retroscope—whether it is a waveform, holographic sphere, particle simulation, or audio-reactive sand effect—ultimately travels through this same pipeline.

Understanding this flow is the foundation for understanding every other chapter in this SDK.