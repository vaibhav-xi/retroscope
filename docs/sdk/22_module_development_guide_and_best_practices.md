# 22 - Module Development Guide & Best Practices

Version: 1.0

---

# Introduction

This document describes the recommended practices for writing visualization modules in Retroscope.

Unlike the previous documents, which describe engine APIs and architecture, this guide focuses on **how to think** when implementing a new visualization.

If every module follows these conventions, the engine remains consistent, maintainable, and scalable regardless of how many visualizations are eventually added.

---

# The Philosophy

A Retroscope module should answer one question:

> **"What geometry should exist this frame?"**

It should **not** answer:

- How is it rendered?
- Which shader is active?
- Which OpenGL calls are required?
- How are buffers uploaded?
- Which GPU is installed?

Those are engine responsibilities.

The module simply generates procedural geometry.

---

# Think Procedurally

A module should describe a visualization mathematically.

Good examples

```
Waveform

↓

Polyline

↓

Renderable
```

```
Particle Field

↓

Many Polylines

↓

Renderable
```

```
Radar Sweep

↓

Arc

↓

Renderable
```

The module should think in terms of shapes, not rendering.

---

# A Module Owns Data

A module owns

- simulation state
- animation state
- parameters
- renderables
- internal caches

It does **not** own

- shaders
- meshes
- GPU objects
- vertex buffers
- renderer

---

# The Lifecycle

Every module follows the same pattern.

```
Construct

↓

Initialize State

↓

Update Simulation

↓

Build Geometry

↓

Renderer Draws
```

This separation should always remain clear.

---

# Separate Simulation from Rendering

Avoid writing

```python
update():

    particle.position += velocity

    frame.add(...)
```

Instead

```python
update():

    particle.position += velocity
```

and later

```python
build():

    generate geometry
```

Simulation and rendering are different responsibilities.

---

# Build Geometry, Don't Draw

Never think

```
Draw Circle
```

Instead think

```
Create Circle Geometry
```

The renderer performs the drawing.

---

# Geometry Should Be Deterministic

Given identical module state,

the generated geometry should always be identical.

Avoid hidden randomness unless explicitly desired.

---

# Store State

Persistent state belongs inside the module.

Examples

```
Particle Positions

↓

Wave Phase

↓

Radar Angle

↓

Noise Seed
```

Do not recompute long-lived state every frame.

---

# Minimize Allocations

Avoid

```python
vertices = []
```

inside every update.

Prefer

- cached lists
- reusable arrays
- persistent objects

The renderer already minimizes allocations.

Modules should too.

---

# Reuse Renderables

Don't recreate

```python
Renderable()
```

every frame.

Instead

```
Create Once

↓

Update Geometry

↓

Mark Dirty
```

This is dramatically faster.

---

# Prefer Continuous Animation

Animations should use

```
dt
```

rather than frame counts.

Good

```python
angle += speed * dt
```

Bad

```python
angle += 1
```

The first is frame-rate independent.

---

# Think in Mathematical Space

Generate geometry using

- sine
- cosine
- interpolation
- vectors
- matrices
- polar coordinates

rather than screen pixels.

---

# Keep Update Small

A good update function

```
Read Context

↓

Update State

↓

Done
```

It should not contain rendering logic.

---

# Keep Build Small

A good build function

```
Read State

↓

Generate Geometry

↓

Done
```

Nothing more.

---

# Parameters Should Drive Everything

Avoid

```python
speed = 2.5
```

Instead

```python
speed = self.parameters.speed
```

This allows

- UI
- presets
- automation
- MIDI

to control the visualization.

---

# Use Themes

Never hardcode colors.

Avoid

```python
(0,1,0)
```

Prefer

```python
theme.primary
```

This keeps modules visually consistent.

---

# Don't Import OpenGL

A module should never contain

```python
from OpenGL.GL import *
```

or

```python
glDrawArrays(...)
```

Rendering belongs to the engine.

---

# Don't Import Native Objects

Modules shouldn't know about

```
Mesh

Shader

VertexBuffer
```

Those belong below the Geometry Builder.

---

# Favor Composition

Instead of one huge Renderable,

consider multiple smaller Renderables when they represent distinct logical objects.

Example

```
Radar

↓

Grid

↓

Sweep

↓

Targets
```

Each can have its own Material and Transform.

---

# Think in Layers

Visualizations often consist of

```
Background

↓

Structure

↓

Animation

↓

Highlights
```

Model these as separate renderables.

---

# Design for Audio

Ask

> What happens when the sound gets louder?

> What happens on a beat?

> What happens at low frequencies?

Even non-audio visualizations should consider how audio could influence them.

---

# Design for Themes

Ask

> Would this still look good in Amber?

> Blue?

> Cyberpunk?

Avoid baking assumptions about colors into the algorithm.

---

# Use Dirty Flags

Only regenerate geometry when necessary.

If nothing changes,

reuse existing geometry.

This is one of the biggest performance optimizations in the engine.

---

# Think About Scale

A module should continue to work if

```
100 particles

↓

1,000 particles

↓

100,000 particles
```

The algorithm should degrade gracefully.

---

# Avoid Global State

Never rely on module-level globals.

Everything should live inside

```
Module

↓

State
```

This makes modules reusable and testable.

---

# Keep Modules Independent

A module should never directly depend on another module.

Instead use

- Context
- Signals
- shared engine services

This prevents circular dependencies.

---

# Prototype First

When creating a new visualization

1. Make it work.
2. Make it clean.
3. Profile it.
4. Optimize if necessary.

Avoid premature optimization.

---

# Typical Module Structure

A mature module often contains

```
Parameters

↓

Persistent State

↓

Simulation

↓

Geometry Generation

↓

Helper Functions
```

Each section should remain clearly separated.

---

# Naming Conventions

Prefer descriptive names.

Examples

```
Particle

RadarSweep

WaveGenerator

Snowflake

FrequencyRing
```

Avoid abbreviations unless universally understood.

---

# Documentation

Complex mathematics should always include comments explaining

- the equation
- the reasoning
- the intended visual effect

Future contributors should understand *why* the code exists, not only *what* it does.

---

# Testing

Whenever possible,

build small standalone prototypes before integrating into the engine.

Examples

- microphone test
- FFT viewer
- particle sandbox
- geometry debugger

This keeps engine debugging simple.

---

# Inspiration

A Retroscope module is not limited to oscilloscopes.

Possible visualizations include

- holographic globes
- particle storms
- snow simulations
- sand physics
- radar systems
- DNA helices
- volumetric fields
- Lissajous figures
- fluid flow
- force-directed graphs
- procedural galaxies

The engine is designed to support all of these using the same API.

---

# The Golden Rule

Every module should be able to answer this question:

> **If the renderer disappeared tomorrow, could this module still describe its geometry?**

If the answer is yes,

the module is properly separated from rendering.

---

# Mental Model

Imagine a module as an architect.

The architect designs a building.

They do not pour concrete, fabricate steel, or operate cranes.

The construction company handles those tasks.

Likewise, a Retroscope module designs geometry.

The engine constructs, uploads, and renders it.

---

# Future Vision

As Retroscope evolves into a complete procedural visualization platform, modules should become increasingly expressive while becoming increasingly unaware of the rendering implementation beneath them.

A module written years from now should still resemble a module written today:

- update state
- generate geometry
- expose parameters
- react to context

Everything else should remain the engine's responsibility.

---

# Summary

The Retroscope module architecture is intentionally minimal.

A module owns simulation and procedural geometry generation, while the engine owns rendering, GPU resources, shaders, memory management, and platform abstraction.

Following the practices described in this guide ensures that modules remain portable, performant, reusable, and visually consistent across themes, platforms, and future engine capabilities. By thinking in terms of mathematics, geometry, and state rather than rendering APIs, developers can create sophisticated visualizations that naturally integrate into the Retroscope ecosystem.