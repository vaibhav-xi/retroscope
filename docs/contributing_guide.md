# 26 - Contributing Guide

Version: 1.0

---

# Introduction

This document describes the development philosophy of the Retroscope project.

Unlike a traditional contributing guide that focuses on GitHub workflows and pull requests, this guide explains **how code should be written** so that the architecture remains consistent as the engine grows.

Every contribution—whether it is a new visualization module, renderer optimization, native extension, or engine subsystem—should follow the principles described here.

The goal is that code written years apart still feels like it belongs to the same project.

---

# Philosophy

Retroscope is an engine.

Not a demo.

Not an application.

Not an oscilloscope.

Every contribution should improve

- the engine
- the architecture
- the developer experience

rather than solving only today's problem.

---

# Design Goals

Every new piece of code should satisfy at least one of the following.

✔ Simpler

✔ Faster

✔ More reusable

✔ More maintainable

✔ More portable

If it satisfies none of them,

it probably shouldn't exist.

---

# Engine Before Features

The project always prioritizes architecture over features.

Bad

```
Need hologram.

↓

Hack renderer.

↓

Done.
```

Good

```
Need hologram.

↓

Improve render pipeline.

↓

Implement hologram.

↓

Future modules benefit.
```

The second approach compounds over time.

---

# Preserve Layer Boundaries

Never mix responsibilities.

Correct

```
Module

↓

Geometry

↓

Renderer

↓

GPU
```

Incorrect

```
Module

↓

OpenGL

↓

GPU
```

The rendering pipeline exists for a reason.

---

# Respect Existing APIs

The public Module API should change rarely.

Internal implementation can evolve continuously.

If you need to improve something,

prefer improving internals rather than breaking module code.

---

# Think Like an Engine Developer

When writing code,

ask

> "Will another module benefit from this?"

If the answer is yes,

it probably belongs inside the engine rather than inside a specific module.

---

# Python First

New features should normally begin in Python.

Python provides

- fast iteration
- readability
- easy debugging
- architectural flexibility

Native code should only be introduced after profiling.

---

# Port Only Bottlenecks

Native code is justified when

✔ it runs every frame

✔ it allocates heavily

✔ it performs large loops

✔ profiling identifies it

Do not port code simply because it "feels slow."

---

# One Responsibility Per File

Avoid large files.

Good

```
mesh_object.c

shader_object.c

vertex_buffer_object.c
```

Bad

```
renderer_everything.c
```

Each file should represent one concept.

---

# Naming

Prefer explicit names.

Good

```
GeometryBuilder

RenderPacket

VertexBuffer

ParticleEmitter
```

Bad

```
Helper

Utils

Manager2

Thing
```

The codebase should be understandable without reading comments.

---

# Comments

Explain

**why**

not

**what**.

Bad

```python
# increment x

x += 1
```

Good

```python
# Advance phase based on elapsed time so
# animation remains frame-rate independent.
```

The code already explains *what*.

Comments explain *why*.

---

# Functions

Functions should be small.

Prefer

```
Build Geometry

↓

Upload Mesh

↓

Draw Mesh
```

instead of

```
RenderEverything()
```

Small functions are easier to optimize and test.

---

# Classes

Classes should own exactly one concept.

Examples

```
Mesh

Shader

Renderable

Geometry

Material

Transform
```

Avoid classes that own unrelated responsibilities.

---

# Composition Over Inheritance

Prefer

```
Renderable

+

Material

+

Transform
```

instead of deep inheritance trees.

Composition is easier to extend.

---

# Don't Duplicate Logic

If two modules share mathematics,

extract it.

If two render passes share code,

extract it.

Duplicate code almost always diverges over time.

---

# Write Reusable Systems

Whenever possible,

build

```
Particle Engine
```

rather than

```
Snow Particles
```

Reusable systems multiply the capabilities of the engine.

---

# Prefer Data-Oriented Thinking

Large procedural scenes should operate on contiguous data.

Avoid deeply nested object hierarchies when performance matters.

---

# Minimize Allocations

Prefer

```
Reserve

↓

Reuse
```

Avoid allocating inside per-frame loops.

Always ask

> Can this object live longer?

---

# Profile Before Optimizing

Never optimize blindly.

Workflow

```
Measure

↓

Identify

↓

Optimize

↓

Measure Again
```

Every optimization should have evidence.

---

# Avoid Premature Complexity

Future-proofing is good.

Speculative architecture is not.

Build what is needed,

while leaving room for growth.

---

# Keep Modules Clean

Visualization modules should remain almost mathematical.

Reading a module should feel like reading an algorithm,

not a graphics API.

---

# Avoid Platform Assumptions

Never assume

- macOS
- Raspberry Pi
- Linux

Platform-specific code belongs inside abstraction layers.

---

# Test Small

Before integrating a large system,

prototype it.

Examples

- FFT viewer
- microphone test
- shader test
- mesh test
- particle sandbox

Small prototypes dramatically reduce debugging time.

---

# Native Code Standards

Every native object should

- own its resources
- expose a minimal API
- clean up correctly
- hide OpenGL
- support multiple platforms

The Python API should remain simple.

---

# Documentation

If a subsystem required significant thought to design,

document it.

Future contributors should understand

- purpose
- architecture
- limitations

without reverse engineering the implementation.

---

# Backwards Compatibility

Avoid breaking existing modules.

If an API must change,

provide a migration path whenever possible.

---

# Pull Request Checklist

Before merging, ask

- Does this simplify the engine?
- Does it introduce unnecessary coupling?
- Does it duplicate existing functionality?
- Does it fit the architecture?
- Has it been profiled if performance-related?
- Does it work on both macOS and Raspberry Pi?
- Is it documented?
- Is it tested?

If any answer is "no,"

consider revising the implementation.

---

# Coding Style

Retroscope favors

- descriptive names
- small functions
- clear ownership
- minimal globals
- explicit data flow
- composition
- readable algorithms

The code should feel calm rather than clever.

---

# What Makes Good Retroscope Code?

Good Retroscope code usually has these characteristics:

- easy to read
- mathematically clear
- independent of rendering backend
- reusable
- deterministic
- efficient
- platform independent

If someone unfamiliar with the engine can understand a module after a few minutes, it is probably well written.

---

# Long-Term Vision

Retroscope is intended to grow into a platform that supports dozens—or eventually hundreds—of visualization modules.

That is only possible if contributors consistently prioritize architecture over convenience.

Every contribution should make the next contribution easier.

That is how healthy engines evolve.

---

# Summary

Contributing to Retroscope means contributing to an engine, not just a codebase.

The project values clean architecture, clear separation of responsibilities, stable APIs, reusable systems, and evidence-based optimization. Python remains the expressive layer for describing visualizations, while native code accelerates proven bottlenecks.

By following the principles in this guide, contributors help ensure that Retroscope remains maintainable, performant, and enjoyable to extend as it evolves into a comprehensive real-time procedural visualization platform.