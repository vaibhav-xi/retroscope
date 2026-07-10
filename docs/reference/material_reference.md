# docs/reference/material_reference.md

# Material Reference

Version: 1.0

---

# Introduction

A **Material** describes **how** geometry should appear when rendered.

It is important to understand that a Material does **not** describe geometry.

Geometry answers

> **What should be drawn?**

Material answers

> **How should it look?**

This separation is fundamental to the Retroscope architecture.

```
Module

↓

Renderable

↓

Geometry

+

Material

↓

Renderer

↓

GPU
```

A Material is entirely renderer-independent.

---

# Philosophy

Geometry should never contain appearance.

Appearance should never contain geometry.

For example,

a Circle remains exactly the same Circle whether it is

- green
- blue
- transparent
- glowing
- thick
- thin

Only its Material changes.

---

# Ownership

Every Renderable owns exactly one Material.

```
Renderable

├── Geometry

├── Material

└── Transform
```

This allows identical geometry to be rendered with different appearances.

---

# Current Material

The current implementation is intentionally minimal.

Example

```python
Material(

    color=(0.0, 1.0, 0.4)

)
```

Today the renderer primarily consumes

```
color
```

Future versions will expand the Material system without changing module APIs.

---

# Color

Color is the primary material property.

Example

```python
material.color = (

    0.0,

    1.0,

    0.4

)
```

Values are normalized.

```
0.0 → 1.0
```

per component.

---

# RGB

Current colors are stored as

```
(R,

 G,

 B)
```

Future versions may also support

```
RGBA
```

for transparency.

---

# Theme Integration

Modules should avoid hardcoded colors.

Instead of

```python
(0,1,0)
```

prefer

```python
context.theme.primary
```

This allows visualizations to automatically adapt to

- Amber
- Cyberpunk
- Oscilloscope
- Blue

without modifying module code.

---

# Semantic Colors

Themes should expose semantic names rather than literal colors.

Examples

```
Primary

Secondary

Accent

Grid

Background

Warning

Highlight
```

Modules request meaning,

not specific RGB values.

---

# Opacity (Future)

Future Material

```python
material.opacity =

0.5
```

Allows

- fading
- overlays
- ghosting

---

# Line Width (Future)

Although current stroke width belongs to Polyline generation,

future renderers may expose additional appearance control.

Example

```python
material.line_width
```

The renderer decides whether hardware support exists.

---

# Blending (Future)

Possible modes

```
Opaque

Alpha

Additive

Multiply

Screen
```

Useful for

- holograms
- particles
- bloom
- CRT effects

---

# Additive Rendering

Example

```
Particle

+

Particle

↓

Brighter
```

Very common for energy effects.

---

# Glow (Future)

Rather than manually implementing bloom,

a Material may simply request

```python
material.glow = True
```

The renderer determines how glow is produced.

---

# Emissive Intensity (Future)

Example

```python
material.emission =

2.5
```

Useful for HDR pipelines.

---

# Point Size (Future)

Useful for

- stars
- particles
- point clouds

without modifying geometry.

---

# Dash Patterns (Future)

Polyline appearance

```
──────

↓

- - - -

↓

······
```

Should eventually become a Material property.

---

# Cap Style (Future)

Polyline endings

```
Round

Square

Butt
```

Renderer controlled.

---

# Join Style (Future)

Polyline corners

```
Miter

Round

Bevel
```

Again,

renderer implementation.

---

# Anti-Aliasing (Future)

Materials may eventually request

```
Smooth

Fast

Disabled
```

depending on performance requirements.

---

# Depth (Future)

Future 3D support

```
Depth Test

↓

Enabled

Disabled
```

Modules remain renderer-independent.

---

# Render Queue (Future)

Materials may specify rendering order.

Examples

```
Background

Geometry

Transparent

Overlay

UI
```

Useful for layered scenes.

---

# Text Materials

Future text rendering may expose

```
Font

Outline

Shadow

Glow

Alignment
```

while still using the same Material abstraction.

---

# Texture Support (Future)

Eventually

```python
material.texture
```

may become available.

The geometry remains unchanged.

---

# Shader Parameters

Long-term,

custom shader inputs should be expressed through Material rather than direct shader manipulation.

Example

```
Distortion

Glow

Noise

Pulse

Gradient
```

This keeps modules renderer-independent.

---

# Material Reuse

Multiple Renderables may share identical Materials.

Example

```
Grid

↓

Green Material

↓

Wave

↓

Same Green Material
```

Future versions may internally cache Materials.

---

# Dynamic Materials

Modules are free to animate Material properties.

Example

```python
material.color =

theme.primary * intensity
```

Only appearance changes.

Geometry remains unchanged.

---

# Dirty State

Changing only the Material should **not** rebuild geometry.

Instead

```
Material Changed

↓

Renderer Updates Uniforms

↓

Draw
```

Geometry stays cached.

---

# Relationship With Geometry

Good

```
Circle Radius

↓

Geometry
```

Good

```
Circle Color

↓

Material
```

These responsibilities should never overlap.

---

# Relationship With Themes

Themes define

```
Default Appearance
```

Materials define

```
Current Appearance
```

A Material may reference Theme colors directly.

---

# Relationship With Shaders

Materials should never compile shaders.

Instead

```
Material

↓

Renderer

↓

Shader Uniforms
```

The renderer performs binding.

---

# Performance

Changing Material properties is usually much cheaper than rebuilding geometry.

Whenever possible,

animate

- colors
- opacity
- glow

instead of regenerating vertices.

---

# Best Practices

✔ Keep Materials lightweight.

✔ Separate appearance from geometry.

✔ Use Theme colors.

✔ Reuse Materials when appropriate.

✔ Let the renderer interpret Material properties.

---

# Anti-Patterns

Avoid

- OpenGL handles
- shader compilation
- GPU state
- vertex data
- geometry generation

inside Materials.

A Material is descriptive,

not executable.

---

# Future Material System

The long-term Material API may resemble

```python
Material(

    color,

    opacity,

    glow,

    additive,

    emission,

    texture,

    line_style,

    point_size,

    render_queue
)
```

Modules using only high-level Material properties will automatically benefit from future renderer improvements.

---

# Mental Model

Imagine painting a sculpture.

The sculpture represents Geometry.

The paint represents the Material.

Changing the paint does not change the sculpture.

Changing the sculpture does not determine the paint.

Retroscope preserves this distinction throughout the rendering pipeline.

---

# Summary

The Material system defines the visual appearance of geometry while remaining completely independent of the geometry itself. By separating appearance from shape, Retroscope allows the same procedural geometry to be rendered using different themes, colors, blending modes, and future rendering techniques without modifying module code.

As the engine evolves, Materials will become the primary mechanism for expressing visual intent while the renderer determines the optimal implementation for the current rendering backend.