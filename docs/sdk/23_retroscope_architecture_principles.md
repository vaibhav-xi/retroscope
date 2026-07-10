# 23 - Retroscope Architecture Principles

Version: 1.0

---

# Introduction

This document describes the architectural principles that guide every design decision in Retroscope.

Unlike the previous documents, which describe APIs and engine systems, this document explains **why** the engine is built the way it is.

These principles should be considered "laws" of the project.

Whenever a new feature is added, it should reinforce these principles rather than work against them.

---

# Principle 1 — Separation of Responsibilities

Every part of the engine should have one clear responsibility.

Examples

```
Module

↓

Creates visualizations
```

```
Geometry Builder

↓

Converts primitives into geometry
```

```
Mesh

↓

Owns GPU buffers
```

```
Renderer

↓

Draws the current frame
```

```
Audio

↓

Provides analyzed audio
```

A class should have one reason to change.

---

# Principle 2 — Modules Never Render

Modules should never perform rendering.

They should never know about

- OpenGL
- GPU buffers
- shaders
- VAOs
- VBOs
- draw calls

Instead they produce

```
Geometry
```

The renderer decides how that geometry reaches the GPU.

---

# Principle 3 — Rendering Is a Pipeline

Rendering is not one function.

It is a sequence of transformations.

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

GPU
```

Each stage transforms data into a form that is more suitable for the next stage.

---

# Principle 4 — Data Flows Downward

Dependencies should always point downward.

```
Module

↓

Renderable

↓

Geometry

↓

Mesh

↓

GPU
```

Never the opposite.

The renderer should never know about specific modules.

---

# Principle 5 — High-Level Python

Python is responsible for

- orchestration
- architecture
- simulation
- procedural logic
- engine organization

Python should describe systems, not execute low-level rendering work.

---

# Principle 6 — Heavy Work Belongs in Native Code

Whenever profiling identifies a bottleneck,

that work should migrate to native code.

Current examples

✔ Stroke Builder

✔ Vertex Buffer

✔ Mesh

✔ Shader

Future examples

- particle simulation
- framebuffers
- textures
- FFT
- render passes

Python remains expressive while native code remains fast.

---

# Principle 7 — OpenGL Should Be Hidden

The long-term goal is that visualization modules never import OpenGL.

Instead

```
Module

↓

Renderable

↓

Mesh

↓

Renderer

↓

OpenGL
```

Eventually almost every OpenGL call should exist inside the native layer.

---

# Principle 8 — Engine Before Features

If adding a feature requires breaking the architecture,

improve the architecture first.

Never add shortcuts that future systems will need to remove.

---

# Principle 9 — Composition Over Inheritance

Prefer combining small systems rather than creating large inheritance hierarchies.

Example

```
Renderable

+

Geometry

+

Material

+

Transform
```

instead of

```
AnimatedGlowingRadarRenderable
```

Small reusable components scale much better.

---

# Principle 10 — Platform Independence

Retroscope should run on

- Raspberry Pi
- macOS
- Linux

without changing module code.

Platform differences belong inside

```
gl_platform.h
```

or other platform abstraction layers.

---

# Principle 11 — Data-Oriented Thinking

Whenever possible,

operate on contiguous data.

Examples

```
VertexBuffer

↓

float*

↓

GPU
```

rather than deeply nested Python objects.

Cache-friendly memory layouts are preferred.

---

# Principle 12 — Persistent Objects

Allocate once.

Reuse forever.

Preferred

```
Create Mesh

↓

Reuse Mesh
```

Avoid

```
Create

↓

Destroy

↓

Create

↓

Destroy
```

every frame.

---

# Principle 13 — Dirty Instead of Rebuild

Nothing should rebuild unless necessary.

```
Changed?

↓

Yes

↓

Rebuild

No

↓

Reuse
```

This applies to

- geometry
- meshes
- renderables
- GPU uploads

---

# Principle 14 — Stable APIs

Module APIs should change very rarely.

Internal implementation may evolve dramatically,

but module code written today should continue working years later.

---

# Principle 15 — Mathematical First

Visualization algorithms should be driven by mathematics rather than rendering tricks.

Examples

- sine waves
- Perlin noise
- polar coordinates
- interpolation
- FFT
- vector fields

The renderer simply displays the result.

---

# Principle 16 — Theme Independence

A module should not care whether the current theme is

- Amber
- Cyberpunk
- Oscilloscope
- Medical
- Radar

It simply requests semantic colors.

---

# Principle 17 — Context Is the Public API

Modules should obtain engine state from Context.

Avoid

- globals
- singleton access
- platform imports

Context should become the stable interface between modules and the engine.

---

# Principle 18 — Signals Describe Events

State belongs in Context.

Events belong in Signals.

Example

```
Theme

↓

Context.theme
```

```
Theme Changed

↓

Signal
```

These concepts should never be mixed.

---

# Principle 19 — Services Provide Infrastructure

Infrastructure belongs in Services.

Examples

- logging
- screenshots
- profiling
- recording
- settings

Visualization modules should remain free of infrastructure code.

---

# Principle 20 — The Renderer Is Replaceable

The renderer should eventually become just one backend.

Future possibilities

```
OpenGL ES

OpenGL

Metal

Vulkan

WebGPU
```

Modules should remain identical regardless of rendering backend.

---

# Principle 21 — The Engine Is Procedural

Retroscope is fundamentally a procedural graphics engine.

Geometry is generated algorithmically rather than authored manually.

This enables

- infinite variation
- audio reactivity
- parameter animation
- generative art
- scientific visualization

---

# Principle 22 — Prototype, Then Generalize

Build small experiments first.

Once an idea proves useful,

integrate it into the engine.

Examples from Retroscope include

- microphone prototype
- native mesh prototype
- shader prototype
- stroke builder prototype

The engine has grown by evolving successful prototypes into reusable systems.

---

# Principle 23 — Profile Before Optimizing

Never assume where time is being spent.

Instead

```
Measure

↓

Identify Bottleneck

↓

Optimize

↓

Measure Again
```

Architecture decisions should be guided by evidence.

---

# Principle 24 — Build for the Next Ten Modules

When implementing a feature,

don't ask

> "Will this solve today's problem?"

Ask

> "Will this still make sense after fifty visualization modules?"

The architecture should become stronger as the project grows.

---

# Principle 25 — Make the Engine Feel Small

Although Retroscope contains many subsystems,

a module author should only need to understand a few concepts:

```
Module

↓

Renderable

↓

Geometry

↓

Material

↓

Transform

↓

Frame

↓

Context
```

Everything else should remain hidden behind the engine.

This is the ultimate architectural goal.

---

# The Long-Term Vision

Retroscope is not simply an oscilloscope.

It is intended to become a procedural visualization platform capable of powering

- music visualizers
- scientific displays
- radar interfaces
- holographic user interfaces
- particle simulations
- generative art
- embedded Raspberry Pi installations
- museum exhibits
- interactive installations
- educational tools

using one consistent architecture.

The APIs described throughout this SDK exist to support that vision.

---

# Final Summary

Every subsystem in Retroscope exists to preserve one simple idea:

> **Modules should only describe procedural geometry and behavior.**

Everything else—rendering, GPU management, audio acquisition, themes, parameters, services, performance optimization, and platform abstraction—is the responsibility of the engine.

By rigorously maintaining this separation, Retroscope remains scalable, portable, performant, and pleasant to extend. A new visualization should feel like adding a new instrument to an orchestra rather than modifying the orchestra itself.

These architectural principles are the foundation upon which all future development should be built.