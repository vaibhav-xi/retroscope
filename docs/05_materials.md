# 05 - Materials

# Introduction

A Material describes **how geometry should appear**.

Geometry defines shape.

Transform defines position.

Material defines appearance.

Together they form a complete Renderable.

```
Geometry

+

Material

+

Transform

↓

Renderable
```

Materials contain no geometry.

They never modify points, curves or meshes.

Instead, they describe visual properties such as color, transparency, blending, and rendering style.

---

# Philosophy

Retroscope intentionally separates geometry from appearance.

Imagine two objects:

```
Circle

↓

Green

```

and

```
Circle

↓

Amber
```

The geometry is identical.

Only the Material changes.

Likewise,

```
Waveform

↓

Blue Theme
```

and

```
Waveform

↓

Cyberpunk Theme
```

are the same geometry with different materials.

---

# Why Materials Exist

Without Materials every module would need to hard-code rendering decisions.

Instead,

modules describe

```
What
```

while Materials describe

```
How
```

This makes visual styles reusable.

---

# Current Material

The current Material is intentionally very small.

Today it primarily contains

```
Color
```

Example

```python
Material(

    color=(0.0, 1.0, 0.4)

)
```

The renderer uploads this color to the shader before drawing.

---

# Material Lifetime

Materials are persistent objects.

Unlike Geometry,

they are usually created once.

Example

```python
green = Material(

    color=(0.0,1.0,0.4)

)
```

Every frame,

Renderables simply reference the same Material.

---

# Sharing Materials

Materials are designed to be shared.

Example

```
Green Material

↓

Grid

↓

Wave

↓

Cursor

↓

Overlay
```

Changing one Material updates every Renderable using it.

---

# Material Ownership

A Material belongs to the application.

Renderables reference Materials.

Multiple Renderables may reference the same Material.

---

# Current Fields

Today

```
Material

└── Color
```

Future versions will expand this considerably.

---

# Color

Color is represented as

```
(r, g, b)
```

Each component is

```
float

0.0

↓

1.0
```

Example

```python
Material(

    color=(0.0,1.0,0.4)

)
```

---

# Color Philosophy

Colors should normally come from Themes,

not from modules.

Good

```python
material.color = theme.primary
```

Avoid

```python
material.color = (0.0,1.0,0.4)
```

unless the color is intrinsic to the visualization.

---

# Future Alpha

Materials will eventually support transparency.

```
alpha

0.0

↓

1.0
```

Example

```
Grid

↓

25% opacity
```

while the waveform remains fully opaque.

---

# Future Line Width

Current line thickness is stored inside Geometry.

Future versions may move styling into Materials.

Example

```
Material

↓

line_width = 3
```

allowing the same geometry to be drawn differently.

---

# Glow

Future CRT and holographic effects will likely expose

```
glow_strength

glow_radius

glow_color
```

These become inputs to post-processing passes rather than geometry generation.

---

# Blending

Future materials may define

```
Opaque

Alpha

Additive

Multiply

Screen
```

Example

```
Particles

↓

Additive
```

while

```
Grid

↓

Opaque
```

---

# Depth

Future materials may control depth behaviour.

Example

```
Depth Test

On

Off
```

Useful for

HUDs

Overlays

Debug text

---

# Point Size

If point primitives are introduced,

Materials may specify

```
Point Size
```

independent of geometry.

---

# Dash Patterns

Future procedural lines may support

```
Solid

Dashed

Dotted

Custom Pattern
```

Again,

this is appearance,

not geometry.

---

# Animated Materials

Eventually Materials themselves may animate.

Example

```
Pulse

Glow

Color Shift

Noise

Scan

Gradient
```

Geometry remains unchanged.

---

# Shader Independence

Modules never reference shaders.

Instead,

they configure Materials.

The renderer decides how to translate Material properties into shader uniforms.

Example

```
Material

↓

Shader Uniforms
```

---

# Themes

Themes produce Materials.

For example

```
Oscilloscope Theme

↓

Primary Green

↓

Material
```

Changing themes updates Materials.

Geometry remains untouched.

---

# Example

```python
grid = Material(

    color=theme.grid

)

wave = Material(

    color=theme.primary

)
```

The renderer treats both identically.

Only their colors differ.

---

# Material Reuse

Suppose there are

```
500

Grid Lines
```

All may share

```
One Material
```

No duplication is required.

---

# Material Cache

Because Materials change rarely,

the renderer may cache

```
Uniform Locations

GPU State

Pipeline State
```

This minimizes redundant work.

---

# Future Material Types

Eventually there may be specialized Materials.

Examples

```
Solid Material

Glow Material

CRT Material

Particle Material

Gradient Material

Text Material

Hologram Material
```

All inherit the same basic concept.

---

# Design Goals

Materials should be

Simple

Reusable

Independent

Renderer Agnostic

Future Proof

They should never contain rendering code.

---

# Material vs Geometry

A common mistake is confusing

shape

with

appearance.

Changing Geometry changes

```
What Exists
```

Changing Material changes

```
How It Looks
```

These responsibilities should remain completely independent.

---

# Mental Model

Think of Geometry as a wireframe sculpture.

Material is the paint applied to it.

The sculpture does not change.

Only its appearance changes.

---

# Summary

Materials define the visual appearance of Geometry.

Today they primarily contain color.

Future versions will expand Materials to include

- opacity
- glow
- blending
- gradients
- line styles
- CRT effects
- holographic effects
- particle rendering
- post-processing hints

By separating appearance from geometry, Retroscope allows the same procedural visualization to adopt entirely different visual identities without changing a single point of geometry.

This separation is essential for themes, reusable rendering styles, and future rendering pipelines.