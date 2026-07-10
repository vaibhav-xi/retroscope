# docs/reference/cookbook.md

# Retroscope Cookbook

Version: 1.0

---

# Introduction

The Cookbook is a collection of common implementation patterns used throughout Retroscope.

Unlike the SDK, which explains architecture and APIs, this document focuses on solving practical problems.

Each recipe demonstrates a common task using the engine's conventions and explains why that approach is preferred.

Whenever possible, modules should follow these patterns rather than inventing their own solutions.

---

# Recipe Index

Current recipes

- Creating a new module
- Rendering a polyline
- Rendering multiple objects
- Reusing geometry
- Audio-reactive animation
- Time-based animation
- Theme-aware rendering
- Parameters
- Dirty flags
- Multiple renderables
- Geometry caching
- Randomness
- Module communication
- Performance
- Native candidates

Future recipes can be added without affecting the existing structure.

---

# Recipe — Create a Module

Minimum structure

```python
class MyModule(Module):

    def __init__(self):

        super().__init__()
```

Always inherit from `Module`.

Always call the base constructor.

---

# Recipe — Persistent Renderables

Good

```python
self.wave = Renderable()
```

Create once.

Reuse forever.

Avoid

```python
Renderable()
```

inside `update()`.

---

# Recipe — Audio Reactive Radius

```python
radius =

base_radius +

context.audio.rms * scale
```

Simple.

Stable.

Frame-rate independent.

---

# Recipe — Frame-Rate Independent Animation

Correct

```python
phase +=

speed * dt
```

Incorrect

```python
phase += 0.01
```

Always use elapsed time.

---

# Recipe — Use Theme Colors

Preferred

```python
renderable.material.color =

context.theme.primary
```

Avoid

```python
(0,1,0)
```

---

# Recipe — Dirty Flags

Only rebuild geometry when needed.

```python
if radius_changed:

    renderable.is_dirty = True
```

---

# Recipe — Multiple Renderables

Instead of

```
HugeRenderable
```

prefer

```
Grid

Wave

Overlay

Labels
```

Each Renderable should represent one visual concept.

---

# Recipe — Geometry Caching

Static geometry

```
Create

↓

Reuse
```

Animated geometry

```
Dirty

↓

Rebuild
```

Never regenerate static geometry every frame.

---

# Recipe — Randomness

Good

```python
rng = random.Random(seed)
```

Avoid

```python
random.random()
```

directly if reproducibility matters.

Modules should support deterministic output whenever practical.

---

# Recipe — Smooth Audio

Instead of

```python
value = rms
```

Prefer

```python
value +=

(rms - value) * smoothing
```

Produces more visually pleasing motion.

---

# Recipe — Layering

Typical ordering

```
Background

↓

Grid

↓

Visualization

↓

Particles

↓

Overlay

↓

Text
```

---

# Recipe — Performance

Before writing optimized code, ask

- Can this be cached?
- Can this move to C?
- Does geometry actually change?
- Can a Transform solve this instead?

---

# Recipe — Native Candidate

Good candidates

- tessellation
- FFT
- particle updates
- interpolation
- geometry generation

Poor candidates

- module orchestration
- configuration
- architecture

---

# Common Mistakes

Avoid

- OpenGL inside modules
- hardcoded colors
- rebuilding geometry every frame
- creating Renderables repeatedly
- storing rendering state inside Geometry
- mixing simulation and rendering

---

# Summary

The Cookbook is intended to grow alongside the engine.

Whenever a useful implementation pattern emerges, it should become a new recipe so future module authors can benefit from it.