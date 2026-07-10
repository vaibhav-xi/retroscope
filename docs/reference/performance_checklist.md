# docs/reference/performance_checklist.md

# Performance Checklist

Version: 1.0

---

# Introduction

Retroscope is designed to render complex procedural geometry in real time on both desktop systems and constrained hardware such as the Raspberry Pi.

Maintaining this level of performance requires discipline.

This document serves as the official checklist for evaluating new code before it becomes part of the engine.

It is intended to answer one question:

> **"Is this implementation consistent with Retroscope's performance philosophy?"**

Every visualization module, rendering optimization, and native subsystem should be evaluated against these guidelines.

---

# Core Philosophy

Performance is not achieved through clever tricks.

It is achieved through architecture.

The most important optimization is usually

```
Avoid Doing Work
```

rather than

```
Do Work Faster
```

---

# The Golden Rule

Before optimizing anything, ask

> **Can this work be avoided entirely?**

Avoiding computation is always preferable to accelerating unnecessary computation.

---

# Profiling First

Never optimize based on intuition.

Workflow

```
Observe

↓

Measure

↓

Identify Bottleneck

↓

Optimize

↓

Measure Again
```

Performance work should always begin with evidence.

---

# Frame Budget

Typical targets

```
60 FPS

↓

16.67 ms
```

Everything performed during a frame must fit within that budget.

For Raspberry Pi,

maintaining consistent frame pacing is often more important than achieving extremely high peak frame rates.

---

# CPU Checklist

Before merging code,

ask

- Is this algorithm executed every frame?
- Can work be cached?
- Can values be reused?
- Can loops be reduced?
- Can memory allocations be eliminated?

---

# Allocation Checklist

Avoid allocations inside per-frame code.

Bad

```python
def update(...):

    vertices = []
```

every frame.

Better

```python
self.vertices.clear()
```

or

reuse existing buffers.

---

# Geometry Checklist

Ask

- Is geometry changing?
- Or only appearance?
- Or only position?

Only rebuild geometry when topology changes.

---

# Dirty Flags

Use dirty flags aggressively.

Good

```
State Changes

↓

Dirty

↓

Rebuild
```

Bad

```
Every Frame

↓

Rebuild
```

---

# Renderable Lifetime

Create Renderables once.

Bad

```
Frame

↓

Renderable()

↓

Destroy
```

Good

```
Startup

↓

Create

↓

Reuse Forever
```

---

# Geometry Lifetime

Geometry should persist whenever possible.

Only regenerate

- changed curves
- changed meshes
- changed topology

Static geometry should remain cached indefinitely.

---

# Mesh Lifetime

GPU meshes are expensive.

Avoid

```
Upload

↓

Delete

↓

Upload
```

every frame.

Persistent GPU resources are preferred.

---

# Shader Lifetime

Shaders should compile once.

Bad

```
Compile

↓

Draw

↓

Compile
```

Good

```
Compile Once

↓

Reuse Forever
```

---

# Buffer Uploads

Uploading data to the GPU is expensive.

Ask

> Does this data actually need to change?

Static buffers should remain on the GPU.

---

# OpenGL State Changes

State changes are surprisingly expensive.

Avoid unnecessary

- shader switches
- buffer binds
- framebuffer switches
- texture binds

Batch similar work whenever possible.

---

# Draw Calls

Each draw call has overhead.

Prefer

```
One Large Draw
```

instead of

```
Hundreds of Tiny Draws
```

where appropriate.

---

# Python Checklist

Python is excellent for

- orchestration
- algorithms
- module logic

Python is not ideal for

- millions of iterations
- geometry tessellation
- buffer generation

These are native candidates.

---

# Native Checklist

Before moving code to C,

verify

✔ profile confirms bottleneck

✔ isolated functionality

✔ stable API

✔ measurable improvement

Do not port code prematurely.

---

# Cache Local Values

Instead of repeatedly accessing

```python
context.audio.rms
```

inside a loop,

cache

```python
rms = context.audio.rms
```

before the loop.

Small improvements compound.

---

# Math

Avoid repeated expensive operations.

Examples

```
sqrt

pow

sin

cos
```

inside inner loops unless necessary.

Cache reusable values.

---

# Trigonometry

If

```
sin(angle)
```

is computed multiple times,

compute it once.

---

# Temporary Objects

Avoid creating

- tuples
- lists
- dictionaries

inside tight loops.

Persistent objects are generally preferable.

---

# Python Function Calls

Function calls have overhead.

In performance-critical loops,

consider reducing unnecessary call depth.

Maintain readability where practical.

---

# Branches

Avoid excessive branching inside inner loops.

Prefer predictable code paths.

---

# Memory Locality

Data-oriented layouts outperform scattered object graphs.

Good

```
float[]

float[]

float[]
```

Less ideal

```
Object

↓

Object

↓

Object
```

for large datasets.

---

# Module Checklist

Before committing a module,

verify

- no OpenGL imports
- no unnecessary allocations
- uses dirty flags
- uses persistent Renderables
- animation driven by `dt`
- geometry rebuilt only when needed

---

# Geometry Builder Checklist

Verify

- contiguous memory
- no duplicate calculations
- reuse temporary buffers
- avoid Python object creation

This stage often dominates CPU time.

---

# Native Extension Checklist

Every native object should

- free resources
- own allocations
- avoid leaks
- avoid unnecessary copies
- expose minimal Python APIs

---

# Raspberry Pi Checklist

Always test on constrained hardware.

Questions

- Is frame rate stable?
- Is CPU utilization acceptable?
- Are allocations reasonable?
- Is GPU upload minimized?

Performance characteristics often differ dramatically from desktop systems.

---

# Cross-Platform Checklist

Verify

- macOS
- Raspberry Pi
- Linux

Platform abstraction should hide implementation differences.

---

# Measuring Success

Good optimization should produce

- measurable FPS improvement
- lower CPU usage
- reduced memory usage
- cleaner architecture

If an optimization only makes code more complicated,

it may not be worthwhile.

---

# Things Worth Optimizing

Typically

- geometry generation
- tessellation
- FFT
- particle simulation
- GPU uploads
- draw call count

---

# Things Usually Not Worth Optimizing

Usually

- initialization code
- module registration
- configuration loading
- occasional UI interaction

Focus on hot paths.

---

# Performance Workflow

The preferred workflow for performance improvements is

```
Prototype

↓

Profile

↓

Identify Hotspot

↓

Optimize

↓

Benchmark

↓

Commit
```

Skipping steps often leads to unnecessary complexity.

---

# Engine Philosophy

Retroscope should become faster because its architecture improves,

not because every function becomes increasingly clever.

Architecture scales.

Micro-optimizations rarely do.

---

# Final Checklist

Before merging performance-sensitive code,

confirm

- [ ] No unnecessary allocations
- [ ] Persistent Renderables
- [ ] Persistent Meshes
- [ ] Dirty flags used correctly
- [ ] Geometry rebuilt only when required
- [ ] Profiled before optimization
- [ ] Measured after optimization
- [ ] Works on Raspberry Pi
- [ ] Works on macOS
- [ ] Public API unchanged
- [ ] Architecture improved or preserved

If every item passes,

the implementation is consistent with Retroscope's performance philosophy.

---

# Summary

Performance in Retroscope is achieved through thoughtful architecture rather than isolated optimizations. Persistent objects, dirty flags, native acceleration, efficient memory usage, and careful profiling form the foundation of the engine's performance model.

By following this checklist, contributors help ensure that new features remain scalable across platforms—from desktop workstations to Raspberry Pi—while preserving the clean architectural principles that make Retroscope maintainable as it continues to grow.