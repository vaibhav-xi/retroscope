# 21 - Performance & Native Pipeline

Version: 1.0

---

# Introduction

Performance has been one of the primary design goals of Retroscope since the beginning of the project.

Unlike a traditional UI application, Retroscope is expected to render continuously at real-time frame rates while generating large amounts of procedural geometry.

The architecture therefore separates work into two categories:

```
High-level orchestration

↓

Python

Heavy computation

↓

Native C
```

This allows the engine to remain pleasant to develop while still achieving performance suitable for embedded hardware such as the Raspberry Pi.

---

# Design Philosophy

Python is used for

- application structure
- scene management
- modules
- orchestration
- user interface
- high-level algorithms

Native C is used for

- geometry generation
- mesh management
- GPU uploads
- shader management
- OpenGL calls
- memory management

This division keeps Python code simple while moving expensive work into compiled code.

---

# Performance Goals

The engine targets

- interactive editing
- real-time visualization
- low latency
- minimal allocations
- deterministic frame time

Rather than optimizing isolated functions, the architecture is designed to reduce overhead across the entire rendering pipeline.

---

# Pipeline Overview

Current pipeline

```
Module

↓

Primitive

↓

Geometry

↓

Geometry Builder

↓

Native Vertex Buffer

↓

Native Mesh

↓

OpenGL

↓

Display
```

Every stage has a specific responsibility.

---

# Why Native Code?

Pure Python is excellent for

- architecture
- iteration
- readability

It is much less suitable for

- generating millions of vertices
- memory copies
- OpenGL driver calls
- buffer management

Those operations now occur in native code.

---

# Current Native Components

Today the native extension contains

```
Stroke Builder

Geometry

Vertex Buffer

Mesh

Shader
```

These are the foundation of the rendering pipeline.

---

# Stroke Builder

The Stroke Builder converts

```
Polyline

↓

Triangle Strip Geometry
```

This is one of the most CPU-intensive parts of the engine.

It has been fully ported to C.

---

# Vertex Buffer

Instead of Python lists,

Retroscope stores generated vertices inside a native Vertex Buffer.

Advantages

- contiguous memory
- zero Python allocations
- direct OpenGL upload
- cache friendly

---

# Mesh

The Mesh object owns

- VBO
- VAO
- vertex count

Drawing is performed entirely in native code.

Python simply calls

```python
mesh.draw()
```

---

# Shader

Shader compilation and management have also moved into native code.

Responsibilities include

- shader compilation
- linking
- uniform lookup
- program lifetime

Python no longer calls OpenGL shader functions directly.

---

# OpenGL Calls

Current philosophy

OpenGL should gradually disappear from Python.

Today,

most rendering calls already execute inside

```
Mesh

Shader
```

Future versions will continue this trend.

---

# Memory Management

A major design goal is to minimize allocations.

Instead of

```
Allocate

↓

Free

↓

Allocate

↓

Free
```

Retroscope prefers

```
Allocate Once

↓

Reuse Forever
```

---

# Persistent GPU Objects

GPU resources are persistent.

Examples

```
VBO

VAO

Shader

Program
```

They are created once and reused every frame.

---

# Dirty Geometry

One of the biggest optimizations is the dirty system.

```
Renderable Changed?

↓

Yes

↓

Rebuild

↓

Upload

↓

Draw
```

Otherwise

```
Draw
```

No rebuild occurs.

---

# Geometry Caching

Every Renderable caches

```
Geometry

↓

Mesh
```

Geometry generation only occurs when necessary.

---

# Frame Lifetime

Every frame performs

```
Update Modules

↓

Rebuild Dirty Geometry

↓

Draw
```

Rather than rebuilding the entire scene every frame.

---

# Allocation Strategy

Preferred

```
Reserve

↓

Reuse

↓

Grow Occasionally
```

Avoid

```
Allocate Every Frame
```

---

# Python Objects

Modules should avoid creating

- temporary lists
- temporary tuples
- temporary NumPy arrays

inside tight update loops.

Geometry should be reused whenever possible.

---

# Native Buffers

Current VertexBuffer

```
float*

↓

Contiguous Memory
```

This minimizes copying between Python and C.

---

# OpenGL Driver Calls

OpenGL driver calls are relatively expensive.

The engine minimizes

```
glBindBuffer

glVertexAttribPointer

glUseProgram

glUniform*

glDrawArrays
```

Future work aims to reduce these even further.

---

# Batch-Oriented Design

Rather than rendering individual vertices,

Retroscope renders batches.

```
Many Vertices

↓

One Draw Call
```

This dramatically improves performance.

---

# CPU vs GPU

The CPU should spend its time

creating geometry.

The GPU should spend its time

drawing geometry.

Avoid moving work back to the CPU once uploaded.

---

# Python Responsibilities

Python remains responsible for

- scene construction
- procedural algorithms
- module management
- scheduling
- orchestration

Not rendering internals.

---

# Native Responsibilities

Native code owns

- memory
- GPU objects
- rendering
- tessellation
- OpenGL interaction

---

# Raspberry Pi

One of the major architectural constraints is Raspberry Pi.

The engine intentionally avoids assumptions that only hold on desktop GPUs.

Examples

- OpenGL ES compatibility
- minimal draw overhead
- efficient memory usage

Many architectural decisions have been influenced by Pi performance.

---

# Cross-Platform Native Layer

The native layer is written to support

- macOS
- Raspberry Pi
- Linux

using

```
gl_platform.h
```

Platform differences are isolated here rather than scattered throughout the engine.

---

# Future Native Candidates

Several systems are likely to move into C over time.

Examples

```
Geometry Builder

Framebuffer

Texture

Render Passes

Particle Simulation

FFT Processing

Spatial Indexing

Collision Helpers
```

Only after profiling demonstrates a real need.

---

# Profiling First

Optimization should always follow measurement.

The profiler exists specifically to answer

```
What is actually slow?
```

rather than relying on assumptions.

---

# Target Performance

The architecture is intended to comfortably support

- thousands of primitives
- hundreds of renderables
- large procedural scenes
- continuous real-time rendering

while remaining responsive on embedded hardware.

The exact limits depend on the visualization and hardware, but scalability is a core design goal.

---

# Zero-Cost Abstractions

A recurring architectural principle is

```
High-Level API

↓

Minimal Runtime Cost
```

Module authors should be able to write expressive code without paying unnecessary performance penalties.

---

# Development Workflow

Typical optimization process

```
Implement

↓

Profile

↓

Identify Bottleneck

↓

Port To Native

↓

Re-profile
```

Native code is introduced only when justified.

---

# Best Practices

✔ Reuse objects.

✔ Minimize allocations.

✔ Use dirty flags.

✔ Batch geometry.

✔ Let native code handle heavy work.

✔ Profile before optimizing.

---

# Anti-Patterns

Avoid

- rebuilding static geometry every frame
- allocating large temporary arrays
- unnecessary OpenGL calls
- duplicating geometry
- premature optimization

---

# Mental Model

Think of Python as the conductor of an orchestra.

The conductor doesn't produce the sound.

Instead, it coordinates highly specialized musicians.

In Retroscope,

Python coordinates the engine.

Native C performs the heavy computational work.

This separation allows the engine to remain clean, maintainable, and fast.

---

# Future Vision

The long-term goal is for nearly all performance-critical systems to execute natively while Python remains the expressive layer used to build visualizations.

Module authors should never need to think about OpenGL optimization, memory management, or GPU synchronization.

They simply describe procedural geometry.

The engine determines the most efficient way to execute that description.

---

# Summary

Retroscope's performance architecture is based on a clear separation of responsibilities.

Python orchestrates the application and defines visualizations, while native C owns geometry generation, GPU resources, memory management, and rendering. Persistent GPU objects, dirty geometry tracking, batch rendering, and reusable native buffers allow the engine to achieve high performance on both desktop systems and constrained platforms such as the Raspberry Pi.

This architecture enables module authors to write simple, expressive visualization code while the engine transparently handles efficient execution.