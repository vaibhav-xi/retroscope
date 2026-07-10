# 02 - Module API

Version: 1.0

---

# Introduction

Every visualization in Retroscope is implemented as a **Module**.

Modules are the highest-level programming abstraction exposed by the engine.

They are responsible for

- procedural generation
- simulation
- animation
- responding to audio
- responding to user input
- creating Renderables

Modules are **not** responsible for

- rendering
- OpenGL
- GPU resources
- shaders
- vertex buffers
- meshes

Those responsibilities belong entirely to the renderer.

---

# Philosophy

A Module answers one question:

> "What should exist during this frame?"

It never answers

> "How should it be rendered?"

That distinction is the foundation of the Retroscope architecture.

---

# Where Modules Live

Every visualization module lives inside

```
modules/
```

Example

```
modules/

    grid/

        grid.py

    wave/

        module.py

    audio/

        audio.py

    overlay/

        overlay.py

    snow/

        module.py

    radar/

        module.py
```

Every directory normally represents one visualization.

---

# Module Lifetime

A Module exists for the entire lifetime of the application.

```
Application

↓

Create Module

↓

Run

↓

Run

↓

Run

↓

Destroy Module
```

Modules are **persistent objects**.

They are not recreated every frame.

---

# Module Responsibilities

A Module owns

- simulation state
- animation variables
- timers
- procedural generators
- cached renderables
- user parameters

A Module should **not** own

- renderer
- meshes
- shaders
- GPU objects
- OpenGL state

---

# High-Level Lifecycle

A typical lifecycle looks like

```
Construct

↓

start()

↓

update()

↓

build()

↓

update()

↓

build()

↓

...

↓

stop()

↓

Destroyed
```

---

# Complete Lifecycle

```
Application

↓

Module()

↓

start()

↓

Loop

    update()

    build()

↓

Loop

    update()

    build()

↓

stop()

↓

Destroy
```

---

# Constructor

The constructor initializes long-lived state.

Typical responsibilities include

- creating Renderables
- creating Geometry
- allocating arrays
- initializing parameters

Example

```python
class Grid(Module):

    def __init__(self):

        self.renderable = Renderable()

        self.spacing = 50

        self.opacity = 0.5
```

Avoid expensive computation here.

---

# start()

Called once after construction.

Typical uses

- allocate resources
- load files
- initialize hardware
- subscribe to signals

Example

```python
def start(self):

    print("Grid started")
```

Many modules do not need this callback.

---

# stop()

Called once before destruction.

Typical uses

- unsubscribe signals
- close devices
- flush recordings
- release external resources

Example

```python
def stop(self):

    microphone.close()
```

---

# update(context)

Called once every frame.

Purpose

Update simulation state.

Examples

- advance timers
- animate particles
- process audio
- move objects

Example

```python
def update(self, context):

    self.phase += context.dt
```

---

# What Belongs In update()

Good examples

```
Particle simulation

Noise generation

Physics

Beat detection

Animation

State machines
```

Bad examples

```
OpenGL

glDrawArrays()

GPU uploads

Shader compilation
```

---

# build(frame)

Called once every frame.

Purpose

Describe everything that should be rendered.

Most modules spend the majority of their time here.

Typical implementation

```python
def build(self, frame):

    frame.add(

        self.renderable

    )
```

---

# update() vs build()

This distinction is extremely important.

update()

```
Simulation
```

build()

```
Scene generation
```

Renderer

```
Rendering
```

Never mix the three responsibilities.

---

# Example

Good

```python
update()

↓

Move particles

↓

build()

↓

Generate geometry

↓

Renderer

↓

Draw
```

Bad

```python
update()

↓

glDrawArrays()
```

---

# resize()

Optional callback.

Called whenever the viewport changes.

Example

```python
def resize(

    self,

    width,

    height,

):
    ...
```

Typical uses

- regenerate grids
- reposition overlays
- update cached geometry

---

# Context Access

Modules receive engine state through Context.

Example

```python
def update(

    self,

    context,

):

    mouse = context.mouse

    dt = context.dt

    theme = context.theme
```

Modules should never use globals.

---

# Frame Access

The Frame exists only during build().

Example

```python
def build(

    self,

    frame,

):

    frame.add(

        self.renderable

    )
```

Never store

```
self.frame
```

Frames are temporary.

---

# State

Modules own persistent state.

Example

```python
class Wave(Module):

    def __init__(self):

        self.phase = 0.0

        self.frequency = 2.0

        self.points = []
```

State survives across frames.

---

# Cached Objects

Objects that rarely change should be created once.

Good

```python
self.renderable = Renderable()
```

Bad

```python
def build():

    renderable = Renderable()
```

every frame.

---

# Dirty Geometry

When geometry changes

```python
renderable.is_dirty = True
```

The renderer rebuilds GPU resources automatically.

Modules should not perform GPU uploads.

---

# Multiple Renderables

A module may own many Renderables.

Example

```
Radar

↓

Sweep

↓

Grid

↓

Labels

↓

Cursor
```

Each is submitted separately.

---

# Example

```python
def build(

    self,

    frame,

):

    frame.add(

        self.grid

    )

    frame.add(

        self.cursor

    )

    frame.add(

        self.overlay

    )
```

---

# Geometry Ownership

Modules own Geometry.

Renderables reference Geometry.

Renderer consumes Geometry.

```
Module

↓

Geometry

↓

Renderable

↓

Renderer
```

---

# Material Ownership

Modules also own Materials.

Example

```python
self.material = Material(

    color=(0,1,0)

)
```

Multiple Renderables may share one Material.

---

# Transform Ownership

Likewise

```python
self.transform
```

belongs to the module.

Modules animate transforms.

Renderer simply uses them.

---

# Parameters

Modules should expose configurable values.

Examples

```
Amplitude

Frequency

Speed

Opacity

Density

Color

Radius
```

Future UI systems will automatically expose these.

---

# Audio Reactive Modules

Future modules should consume

```python
context.audio
```

Never open microphones directly.

Example

```python
level = context.audio.rms
```

---

# Theme Usage

Avoid hardcoded colors.

Instead

```python
context.theme.primary
```

or

```python
context.theme.grid
```

This allows themes to change dynamically.

---

# Communication

Modules should not reference each other.

Avoid

```python
wave_module.phase
```

Instead use

```
Signals

or

Context
```

---

# Memory

Allocate long-lived objects once.

Good

```python
__init__()
```

Bad

```python
build()

↓

allocate

↓

destroy

↓

repeat
```

---

# Threading

Modules should assume

```
update()

↓

build()
```

are called on the main thread.

They should not assume concurrent execution.

Future worker threads will remain transparent.

---

# Performance Rules

Good

Reuse Renderables

Reuse Geometry

Reuse NumPy arrays

Reuse buffers

Bad

Allocate lists every frame

Compile shaders

Open files

Create Renderables repeatedly

---

# Directory Layout

A typical module

```
snow/

    module.py

    generator.py

    parameters.py

    presets.py

    README.md
```

Large modules should separate simulation from visualization.

---

# Example Module

```python
class Grid(Module):

    def __init__(self):

        self.renderable = Renderable()

    def update(

        self,

        context,

    ):

        pass

    def build(

        self,

        frame,

    ):

        frame.add(

            self.renderable

        )
```

Despite its simplicity,

this demonstrates the entire Retroscope programming model.

---

# Anti-Patterns

Never do this

```python
glDrawArrays()
```

Never

```python
glBindBuffer()
```

Never

```python
glUseProgram()
```

Never

```python
glUniform...
```

Never

```python
Renderer()
```

Never

```python
Frame()
```

Never

```python
Shader()
```

inside a visualization module.

---

# Best Practices

✔ Keep update() purely about simulation.

✔ Keep build() purely about scene generation.

✔ Cache expensive objects.

✔ Reuse Geometry.

✔ Reuse Renderables.

✔ Use Context.

✔ Use Themes.

✔ Use Parameters.

✔ Mark dirty objects.

✔ Let the renderer do the rendering.

---

# Mental Model

Think of a Module as a film director.

The director decides

- what actors appear
- where they stand
- what they do

The director never operates the camera.

The renderer is the camera crew.

The GPU is the projector.

The Module simply describes the scene.

---

# Summary

A Module is the primary extension point of Retroscope.

It owns persistent simulation state, responds to engine events, generates Renderables, and submits them to the current Frame.

Modules remain completely independent from the rendering backend by delegating all GPU work to the renderer.

This strict separation keeps visualization code simple, portable, and highly reusable while allowing the rendering pipeline to evolve independently.