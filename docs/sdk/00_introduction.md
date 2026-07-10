# Retroscope Module SDK

Version: 1.0 (Development)

---

# Welcome

Welcome to the Retroscope Module SDK.

This document is the official reference for writing modules, extending the rendering pipeline, contributing to the engine, and understanding how every subsystem works together.

Unlike a traditional game engine, Retroscope is designed specifically for **real-time procedural visualization**.

Everything in the engine—from a simple oscilloscope trace to a future holographic particle simulation—is built upon the same small set of abstractions.

If you understand those abstractions, you understand the entire engine.

This SDK explains those abstractions in detail.

---

# What is Retroscope?

Retroscope is a real-time procedural visualization engine.

Its primary goal is to generate animated geometric scenes that react to external data such as

- audio
- sensors
- MIDI
- GPIO
- OSC
- simulation
- user interaction

Unlike a traditional game engine,

Retroscope has

- no physics engine
- no scene editor
- no level files
- no animation timeline

Instead,

everything is generated procedurally every frame.

For this reason, the engine is intentionally much smaller and much more focused than Unity, Unreal or Godot.

---

# Design Goals

Retroscope was designed around several principles.

## Simplicity

Every subsystem should have one responsibility.

Example

```
Module

↓

Generate geometry
```

```
Renderer

↓

Render geometry
```

```
Mesh

↓

Own GPU buffers
```

Responsibilities should never overlap.

---

## Separation of Concerns

Modules should never contain OpenGL code.

The renderer should never know how a waveform is generated.

Geometry should never know how it will be rendered.

Every layer has a single job.

---

## Cross Platform

The engine currently targets

- macOS
- Raspberry Pi
- Linux

The rendering backend is written to support both

OpenGL 4.x

and

OpenGL ES 2.0

through a shared native abstraction layer.

Whenever possible, platform differences are hidden behind small compatibility headers such as

```
gl_platform.h
```

The goal is that visualization modules remain completely platform independent.

---

## Native Performance

Retroscope intentionally moves expensive operations into C.

Examples include

- stroke tessellation
- geometry generation
- vertex storage
- GPU uploads
- mesh management
- shader compilation

Python remains responsible for

- orchestration
- application logic
- visualization behaviour

while native code performs the heavy numerical work.

---

## Minimal API Surface

A module should only need to understand a handful of concepts.

```
Module

↓

Frame

↓

Renderable

↓

Geometry

↓

Material

↓

Transform
```

Everything else is handled by the engine.

---

## Data Driven Rendering

Modules never issue OpenGL commands.

Instead,

modules describe

"What should exist."

The renderer decides

"How to render it."

This distinction is one of the most important concepts in Retroscope.

---

# Engine Philosophy

Imagine an orchestra.

The conductor never plays every instrument.

Instead,

each musician performs one task.

The same applies to Retroscope.

```
Modules

↓

Generate content

Renderer

↓

Draw content

Audio

↓

Capture sound

Profiler

↓

Measure performance

Theme

↓

Provide colors
```

Each subsystem focuses on exactly one responsibility.

---

# High Level Architecture

The entire engine can be summarized as

```
Application

↓

Modules

↓

Frame

↓

Renderables

↓

Geometry Builder

↓

Native Vertex Buffer

↓

Mesh

↓

Renderer

↓

GPU
```

This pipeline is executed continuously while the application is running.

---

# Frame Pipeline

Every frame follows the same sequence.

```
Application Loop

↓

Read Input

↓

Update Modules

↓

Create Frame

↓

Modules Build Geometry

↓

Renderer Builds Meshes

↓

Upload Dirty Meshes

↓

Execute Render Graph

↓

Swap Buffers

↓

Repeat
```

Everything ultimately flows through this pipeline.

---

# Layered Architecture

Retroscope is intentionally layered.

```
Visualization Modules

↓

Rendering Abstractions

↓

Native Rendering

↓

OpenGL
```

Each layer only communicates with the layer directly below it.

This keeps the architecture maintainable.

---

# Module Responsibilities

A visualization module is responsible for

- simulation
- animation
- procedural generation
- state management

A module is **not** responsible for

- OpenGL
- shaders
- VBOs
- VAOs
- GPU uploads
- draw calls

Those are handled elsewhere.

---

# Rendering Responsibilities

The renderer is responsible for

- building meshes
- caching GPU resources
- uploading geometry
- binding shaders
- issuing draw calls

The renderer knows nothing about

- audio
- sine waves
- snow particles
- oscilloscopes
- music visualization

It only renders Renderables.

---

# Native Layer Responsibilities

The native layer exists to accelerate operations that are expensive in Python.

Examples include

```
Polyline Tessellation

↓

Native C

Vertex Storage

↓

Native C

GPU Upload

↓

Native C

Mesh Draw

↓

Native C
```

The goal is to minimize Python overhead inside the render loop.

---

# Why Python?

Python is used because it excels at

- experimentation
- procedural generation
- rapid iteration
- scientific computing
- NumPy integration

Visualization ideas can often be tested within minutes.

Performance-critical sections are then moved into native code when necessary.

---

# Why C?

Certain operations are simply much faster in C.

Examples

```
Generating

500,000 vertices
```

or

```
Uploading

large VBOs
```

Keeping those operations inside native extensions allows the engine to maintain interactive frame rates even on devices such as the Raspberry Pi.

---

# Rendering Backend

Retroscope currently uses OpenGL.

Internally,

the renderer abstracts differences between

```
Desktop OpenGL

↓

macOS
```

and

```
OpenGL ES 2.0

↓

Raspberry Pi
```

Most visualization code never notices the difference.

---

# Procedural First

Retroscope is built around procedural generation.

Examples include

- oscilloscopes
- holographic displays
- particle systems
- radar sweeps
- flowing grids
- sand simulations
- waveform visualizers

Almost every visual effect is generated mathematically.

Assets are optional.

Geometry is primary.

---

# Why Geometry?

Instead of relying heavily on textures,

Retroscope generates geometry directly.

Advantages include

- infinite resolution
- easy animation
- mathematical precision
- small memory footprint
- CRT aesthetics

This philosophy resembles classic vector displays and oscilloscopes.

---

# Current Rendering Pipeline

Today's renderer roughly performs

```
Renderable

↓

Geometry Builder

↓

Vertex Buffer

↓

Mesh

↓

Shader

↓

Draw
```

Every object follows this path.

---

# Future Direction

Retroscope has been designed to grow.

Planned features include

- audio spectrum analysis
- beat detection
- particle instancing
- bloom
- CRT persistence
- phosphor simulation
- scanlines
- framebuffer pipelines
- multi-pass rendering
- camera support
- instanced rendering
- compute shaders (where available)

The current architecture intentionally leaves room for these additions.

---

# Target Hardware

The engine is designed to run efficiently on

- Raspberry Pi 3
- Raspberry Pi 4
- Raspberry Pi 5
- Apple Silicon Macs
- Linux desktops

A major design constraint has always been maintaining good performance on relatively modest hardware.

Optimizations are therefore considered part of the architecture rather than an afterthought.

---

# Coding Philosophy

Retroscope favors

- readability
- explicit code
- small classes
- few abstractions
- predictable ownership
- minimal hidden behavior

The codebase intentionally avoids unnecessary frameworks.

Most systems can be understood by reading only a handful of files.

---

# Documentation Philosophy

This SDK is intended to answer two questions.

## Conceptual

Why does the engine work this way?

## Practical

How do I write code that integrates with it?

Both are equally important.

Understanding the philosophy behind the architecture makes it much easier to extend correctly.

---

# Reading Order

This SDK is organized so that each chapter builds upon the previous one.

Recommended order

1. Introduction
2. Engine Overview
3. Module API
4. Context API
5. Frame API
6. Renderable API
7. Geometry API
8. Material API
9. Transform API
10. Renderer Pipeline
11. Native Pipeline
12. Audio Pipeline
13. Themes
14. Services
15. Performance
16. Cookbook

Each chapter assumes familiarity with the previous ones.

---

# Intended Audience

This SDK is written for

- visualization developers
- contributors
- engine developers
- future maintainers
- anyone wishing to create new procedural modules

No prior knowledge of the engine is assumed.

Basic familiarity with Python is sufficient for writing modules.

Knowledge of OpenGL is helpful for renderer development but not required for visualization modules.

---

# Conventions Used

Throughout this documentation

```
Module
```

refers to a visualization module.

```
Renderable
```

refers to a renderable object submitted to a Frame.

```
Geometry
```

refers to CPU-side procedural geometry.

```
Mesh
```

refers to GPU-side geometry.

```
Frame
```

refers to the scene description for a single render cycle.

---

# Final Thoughts

Retroscope is intentionally much smaller than a traditional graphics engine.

Rather than exposing hundreds of APIs, it focuses on a handful of carefully designed concepts.

Once you understand

- Module
- Context
- Frame
- Renderable
- Geometry
- Material
- Transform

you can understand nearly every visualization ever written for the engine.

The remaining chapters explain each of these concepts in progressively greater detail, beginning with the complete engine architecture and then moving through the module API, rendering pipeline, native layer, performance considerations, and practical examples.

Welcome to Retroscope.