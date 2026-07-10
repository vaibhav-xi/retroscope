# 08 - Material API

Version: 1.0

---

# Introduction

A **Material** defines the visual appearance of a Renderable.

Geometry describes **shape**.

Transform describes **position**.

Material describes **appearance**.

These three objects are intentionally independent.

```
Geometry

↓

"What is it?"

Material

↓

"What does it look like?"

Transform

↓

"Where is it?"
```

Together they completely describe a Renderable.

---

# Philosophy

A Material should contain **appearance only**.

It should never contain

- geometry
- transforms
- simulation
- OpenGL objects
- meshes
- shaders

A Material answers questions such as

- What color?
- How transparent?
- How should it blend?
- How thick should lines be?
- Should it glow?

Nothing more.

---

# Ownership

A Material belongs to exactly one Renderable.

```
Module

↓

Renderable

↓

Material
```

Multiple Renderables may reference the same Material if desired.

---

# Lifetime

Materials are long-lived objects.

Typical lifetime

```
Module Created

↓

Material Created

↓

Updated

↓

Updated

↓

Application Exit
```

They should **not** be recreated every frame.

---

# Current Material

Today the Material class is intentionally minimal.

Conceptually

```python
Material

└── color
```

This simplicity is deliberate.

The rendering pipeline is designed to expand later without changing module code.

---

# Current API

Typical construction

```python
Material(

    color=(0.0, 1.0, 0.4)

)
```

Every Renderable automatically owns one.

---

# Color

Current field

```python
material.color
```

Type

```python
tuple[float, float, float]
```

Range

```
0.0

↓

1.0
```

Example

```python
material.color = (

    0.2,

    0.9,

    0.5

)
```

---

# Color Space

Retroscope currently uses normalized RGB.

```
(1,0,0)

↓

Red

(0,1,0)

↓

Green

(0,0,1)

↓

Blue
```

Future color spaces may be added,

but RGB remains the public API.

---

# Shader Interaction

During rendering,

the renderer uploads

```python
material.color
```

to the shader.

Conceptually

```
Material

↓

Shader Uniform

↓

Fragment Shader
```

Modules never call

```cpp
glUniform3f(...)
```

directly.

---

# Theme Integration

Rather than hardcoding colors,

modules should use the active theme.

Good

```python
material.color =

context.theme.primary
```

Bad

```python
material.color = (

    0,

    1,

    0

)
```

This allows the appearance of the application to change without modifying modules.

---

# Material Reuse

Many Renderables may share one Material.

Example

```
Shared Material

↓

Grid

↓

Axes

↓

Waveform
```

Changing the Material changes every object using it.

---

# Mutable Properties

Materials are intended to be mutable.

Example

```python
self.renderable.material.color = (

    1,

    0,

    0

)
```

Changing a Material does **not** require rebuilding geometry.

Only shader state changes.

---

# Dirty State

Currently,

Material changes do not use dirty flags.

The renderer simply uploads the latest values before drawing.

Future versions may cache material state automatically.

---

# Relationship with Geometry

Geometry determines

```
Vertices
```

Material determines

```
Appearance
```

Changing one does not require changing the other.

Example

```
Same Geometry

↓

Green

↓

Blue

↓

Red
```

No geometry rebuild occurs.

---

# Relationship with Transform

Likewise,

changing position does not affect Material.

```
Move Object

↓

Same Color
```

Everything remains independent.

---

# Future Material Fields

The current Material intentionally contains only color,

but the API is designed to grow.

Possible future properties include

```python
Material(

    color=...,

    opacity=...,

    line_width=...,

    point_size=...,

    glow=...,

    emission=...,

    additive=...,

    blend_mode=...,

    texture=...,

    shader=...
)
```

None of these require changing the Renderable API.

---

# Opacity

Future

```python
material.opacity
```

Range

```
0.0

↓

1.0
```

Used for

- fading
- overlays
- ghosting
- persistence

---

# Line Width

Although today's stroke width belongs to the Polyline,

future point or wireframe primitives may also expose

```python
material.line_width
```

---

# Glow

Future CRT pipeline

```
Material

↓

Glow

↓

Bloom Pass
```

Modules simply enable glow.

The renderer performs the effect.

---

# Blend Modes

Future

```python
material.blend_mode
```

Examples

```
Normal

Additive

Multiply

Screen
```

Useful for

- holograms
- particles
- neon
- radar

---

# Emission

Future

```python
material.emission
```

Determines how strongly an object contributes to bloom.

---

# Textures

Eventually

```python
material.texture
```

may reference

```
Texture Object
```

Current oscilloscope rendering does not require textures,

but the architecture supports them.

---

# Shader Parameters

Future custom shader values

```python
material.uniforms

["frequency"]

["noise"]

["time"]
```

This avoids exposing OpenGL directly to modules.

---

# Animation

Materials can be animated exactly like any other object.

Example

```python
material.color = (

    math.sin(t),

    1,

    0

)
```

No renderer changes required.

---

# Example

Pulse effect

```python
level = context.audio.rms

material.color = (

    level,

    1.0,

    level
)
```

Simple,

yet completely renderer-independent.

---

# Material Ownership

Ownership hierarchy

```
Module

↓

Renderable

↓

Material
```

The renderer only reads Material values.

It never owns them.

---

# Memory

Materials are intentionally tiny.

Current implementation

```
RGB Color
```

Future implementation

```
Small collection of appearance parameters
```

No GPU resources live inside the Material.

---

# Best Practices

✔ Reuse Materials.

✔ Use Themes.

✔ Keep Materials lightweight.

✔ Separate appearance from geometry.

✔ Animate Material values instead of rebuilding geometry when possible.

---

# Anti-Patterns

Never

```python
glUniform3f(...)
```

Never

```python
glUseProgram(...)
```

Never

```python
glBindTexture(...)
```

Never

```python
Shader(...)
```

inside modules.

Material should remain a pure data object.

---

# Mental Model

Imagine painting a sculpture.

The sculpture already exists.

Changing the paint does not change the sculpture.

Changing the sculpture does not change the paint.

Geometry is the sculpture.

Material is the paint.

Transform decides where the sculpture sits.

---

# Example

A radar sweep may use

```
Geometry

↓

Arc

Material

↓

Green

Transform

↓

Rotate
```

The renderer combines these three pieces to produce the final image.

---

# Future-Proof Design

One of the design goals of Material is stability.

Modules should never need to know

- which shader is active
- how uniforms are uploaded
- how bloom works
- how transparency works

Those details belong entirely to the renderer.

A module simply modifies Material properties.

The renderer interprets them.

---

# Summary

The Material object defines the visual appearance of a Renderable.

Today it contains only color, but it is intentionally designed to grow into a complete appearance description including opacity, glow, blending, textures, and shader parameters.

By separating appearance from geometry and transforms, Retroscope allows modules to animate visuals efficiently while keeping rendering concerns isolated inside the renderer.

A Material should be thought of as **the appearance description** of a Renderable—nothing more, nothing less.