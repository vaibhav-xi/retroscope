# 20 - Coordinate System & Geometry Space

Version: 1.0

---

# Introduction

One of the most important design decisions in any graphics engine is the coordinate system.

Every visualization module creates geometry.

If different modules use different coordinate systems, nothing aligns correctly.

Retroscope therefore defines a single logical world space that every module operates within.

The renderer is responsible for converting that logical space into GPU coordinates.

Modules never perform viewport transforms or OpenGL coordinate conversion themselves.

---

# Philosophy

Modules should think in terms of

```
Geometry
```

not

```
Pixels
```

nor

```
OpenGL Clip Space
```

This allows exactly the same visualization to work on

- Raspberry Pi
- macOS
- Linux
- Future WebGPU
- Different window sizes

without changing module code.

---

# Current Coordinate Space

Today, geometry is generated directly into normalized OpenGL coordinates.

```
Left

↓

-1

Center

↓

0

Right

↓

+1
```

Likewise

```
Top

↓

+1

Center

↓

0

Bottom

↓

-1
```

Current viewport

```
(-1,+1)

+-------------------+

|                   |

|                   |

|        (0,0)      |

|                   |

|                   |

+-------------------+

(-1,-1)
```

---

# Why Normalized Coordinates?

Advantages

- resolution independent
- extremely simple
- identical on every platform
- no camera required
- OpenGL-ready

The Geometry Builder produces vertices directly in this space.

---

# Current Pipeline

Today

```
Module

↓

Geometry

↓

Vertex Buffer

↓

GPU
```

No additional transforms occur.

---

# Vertex Example

Example vertex

```python
(-0.5, 0.25)
```

means

```
Halfway Left

Quarter Up
```

regardless of

- window size
- monitor resolution
- operating system

---

# Window Independence

A waveform rendered on

```
800×480
```

looks identical on

```
1920×1080
```

because geometry is normalized.

---

# Primitive Space

Every primitive stores positions using engine coordinates.

Example

```
Polyline

↓

list[(x,y)]
```

where

```
-1 ≤ x ≤ 1

-1 ≤ y ≤ 1
```

---

# Geometry Builder

The Geometry Builder assumes

every point already exists in engine space.

It performs no scaling.

It performs no projection.

It simply tessellates.

---

# OpenGL Relationship

Current vertex shader

effectively performs

```
Position

↓

gl_Position
```

No matrix multiplication occurs.

---

# Current Vertex Shader

Conceptually

```glsl
gl_Position =

vec4(

    a_position,

    0,

    1

);
```

This is intentionally simple.

---

# Origin

Current origin

```
(0,0)
```

is

```
Screen Center
```

Positive X

↓

Right

Positive Y

↓

Up

---

# Advantages

Center-origin coordinates are ideal for

- oscilloscopes
- radar
- particles
- polar geometry
- procedural animation
- physics

Many mathematical equations naturally assume an origin-centered space.

---

# Module Example

Wave module

```
sin(x)

↓

Polyline

↓

Geometry Builder
```

No viewport math required.

---

# Grid Example

Grid module simply generates

```
Vertical Lines

Horizontal Lines
```

between

```
-1

↓

+1
```

No knowledge of pixels.

---

# Future Camera

Current engine has

```
No Camera
```

Everything exists directly in screen space.

---

# Planned Camera

Future architecture introduces

```
World Space

↓

Camera

↓

View Matrix

↓

Projection

↓

Clip Space
```

without changing module APIs.

---

# Camera Transform

Future pipeline

```
Geometry

↓

Transform

↓

Camera

↓

Renderer
```

The module still creates geometry exactly the same way.

---

# Transform Space

Renderable transforms will eventually convert

```
Local

↓

World
```

while the camera converts

```
World

↓

Screen
```

---

# World Coordinates

Future

Modules may generate geometry in

```
Meters

Units

Kilometers

Logical Space
```

rather than normalized coordinates.

The renderer performs projection automatically.

---

# Pixel Coordinates

Some future modules

(UI)

may use

```
Pixels
```

instead.

Those will likely use a dedicated orthographic camera.

---

# UI Space

Future pipeline

```
UI Geometry

↓

Pixel Coordinates

↓

Orthographic Projection

↓

Screen
```

Separate from visualization geometry.

---

# Aspect Ratio

Current engine assumes normalized coordinates.

Future camera support will automatically compensate for

```
16:9

↓

4:3

↓

21:9
```

without modifying modules.

---

# Resize Handling

When the window resizes

```
Viewport Changes

↓

Renderer Updates

↓

Modules Unchanged
```

No geometry regeneration is required.

---

# Polar Coordinates

Many future modules will naturally generate

```
Radius

Angle
```

Examples

```
Radar

Jarvis Globe

Particle Rings

Frequency Wheels
```

These convert to engine coordinates before submission.

---

# Procedural Geometry

Example

```python
x = cos(theta)

y = sin(theta)
```

Already produces normalized coordinates.

No scaling necessary.

---

# Audio Geometry

FFT visualizations

```
Frequency

↓

Radius

↓

Position
```

also naturally fit the current coordinate system.

---

# Future 3D

Although Retroscope is currently 2D,

future versions may introduce

```
x

y

z
```

without changing the renderer architecture.

The camera simply gains perspective projection.

---

# Geometry Independence

Modules should never know

```
Viewport Size

Projection Matrix

OpenGL Clip Space
```

These belong entirely to the renderer.

---

# Coordinate Conversion

Future utility functions may exist

```
Screen

↓

World

World

↓

Screen
```

Useful for interaction.

---

# Precision

Current geometry uses

```
float32
```

throughout the pipeline.

This provides excellent GPU performance while remaining more than accurate enough for visualization.

---

# Best Practices

✔ Generate geometry in engine coordinates.

✔ Think mathematically.

✔ Let the renderer handle projection.

✔ Avoid pixel arithmetic whenever possible.

---

# Anti-Patterns

Never

```python
glViewport(...)
```

Never

```python
glOrtho(...)
```

Never

```python
glMatrixMode(...)
```

Never

perform manual screen scaling inside modules.

---

# Mental Model

Imagine drawing on an infinitely thin sheet of graph paper centered at the origin.

Every module simply places points on that sheet.

The renderer is responsible for photographing the sheet and displaying it on the monitor.

The modules never worry about camera lenses, monitor resolution, or display hardware.

---

# Future Vision

The current normalized coordinate system is intentionally minimal.

As Retroscope evolves, the same module architecture will support

- world-space cameras
- zoom
- panning
- multiple viewports
- split-screen rendering
- HUD overlays
- 3D procedural scenes

without requiring existing visualization modules to be rewritten.

The renderer will become more sophisticated while module code remains simple.

---

# Summary

Retroscope currently uses a normalized, origin-centered coordinate system where all geometry is expressed directly in logical engine space.

Modules generate geometry without any knowledge of pixels, window size, or OpenGL projection. The renderer is solely responsible for mapping that geometry onto the display.

This separation keeps visualization code mathematically clean, resolution independent, and ready for future additions such as cameras, world-space rendering, and 3D graphics without changing the module API.