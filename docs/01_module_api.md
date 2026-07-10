# 01 - Module API

# Introduction

A Retroscope visualization is implemented as a **Module**.

Modules are the highest-level building blocks of the engine.

Every visible effect—whether it is a sine wave, a particle system, a holographic sphere, an oscilloscope, or a radar display—is implemented as a module.

Modules are intentionally isolated from the rendering backend.

A module never interacts with:

- OpenGL
- GPU buffers
- Vertex arrays
- Shaders
- Native rendering code

Instead, a module is responsible only for simulation and geometry generation.

This separation keeps modules simple, portable, and easy to compose.

---

# Responsibilities

A module is responsible for:

- maintaining simulation state
- updating animation
- consuming inputs
- consuming audio
- producing geometry
- exposing configurable parameters

A module is **not** responsible for:

- rendering
- GPU uploads
- shaders
- framebuffers
- OpenGL
- mesh generation

---

# Lifecycle

Every frame, each module follows the same lifecycle.

```
start()

↓

update()

↓

build()

↓

stop()
```

Only `update()` and `build()` execute every frame.

---

# Module Execution

The application owns a ModuleManager.

The ModuleManager owns every active module.

Each frame:

```
for module in modules:

    module.update(context)

for module in modules:

    module.build(frame)
```

This separation is deliberate.

Simulation is completed before any geometry is generated.

This guarantees deterministic behavior regardless of module ordering.

---

# Base Class

Every visualization derives from the base Module class.

```python
class Module:

    ...
```

The base class defines the public lifecycle.

---

# Initialization

Construction should allocate simulation state only.

Example:

```python
class Snow(Module):

    def __init__(self):

        self.particles = []
```

Avoid:

- OpenGL
- loading GPU resources
- creating meshes

Construction should be inexpensive.

---

# start()

Called once when the module becomes active.

Typical uses:

- allocate simulation objects
- load presets
- initialize particle systems
- initialize random state

Example:

```python
def start(self):

    self.reset()
```

---

# stop()

Called once before the module is destroyed.

Typical uses:

- release files
- close devices
- stop background threads

Rendering resources should never be released here because modules never own rendering resources.

---

# update()

update() performs simulation.

It answers:

> What should exist now?

Typical work includes:

- physics
- animation
- timers
- particle integration
- audio analysis
- smoothing
- interpolation

Example:

```python
def update(self, context):

    self.phase += context.dt
```

Nothing is rendered here.

---

# build()

build() converts simulation into renderables.

It answers:

> What geometry should be rendered?

Example:

```python
def build(self, frame):

    frame.add(

        Renderable(...)

    )
```

No simulation should occur inside build().

---

# Separation of update() and build()

This distinction is important.

Correct:

```
update()

↓

simulation

↓

build()

↓

geometry
```

Incorrect:

```
build()

↓

simulation

↓

geometry
```

Keeping simulation independent allows:

- deterministic execution
- offline rendering
- recording
- replay
- caching

---

# Context

update() receives a Context.

Example:

```python
def update(self, context):
```

Context provides access to shared engine state.

Typical information includes:

- delta time
- screen size
- input
- theme
- audio
- services

Context is discussed in detail later.

---

# Frame

build() receives a Frame.

Example:

```python
def build(self, frame):
```

The Frame is where renderables are submitted.

Modules never interact with the renderer directly.

---

# Stateless Rendering

A module should think of build() as rebuilding the scene every frame.

Example:

```
Frame

↓

empty

↓

module adds geometry

↓

renderer consumes geometry

↓

frame discarded
```

Modules should not attempt to cache rendering state.

The renderer already performs caching internally.

---

# Geometry Ownership

Modules own simulation.

The renderer owns rendering.

Example:

```
Module

↓

Polyline

↓

Renderer

↓

Triangles

↓

GPU
```

The module never sees the generated triangles.

---

# Multiple Renderables

A module may submit any number of renderables.

Example:

```python
frame.add(grid)

frame.add(axis)

frame.add(cursor)

frame.add(label)
```

Large visualizations are typically composed from many renderables.

---

# Dynamic Geometry

Dynamic geometry changes every frame.

Example:

- oscilloscope traces
- particles
- flowing lines
- lightning

These are rebuilt continuously.

---

# Static Geometry

Static geometry changes rarely.

Example:

- borders
- calibration marks
- static grids

The renderer may cache these internally.

Modules simply submit them normally.

---

# Parameters

Modules may expose configurable parameters.

Example:

```python
frequency

amplitude

speed

density

radius

line_width
```

These should be stored as ordinary Python attributes.

Future versions of Retroscope may automatically expose these through a user interface.

---

# Audio

Modules may react to audio.

Typical workflow:

```
update()

↓

read audio state

↓

update simulation

↓

build geometry
```

Audio should never be read inside build().

---

# Randomness

Procedural modules frequently use randomness.

Examples:

- snow
- stars
- particles
- lightning

Whenever possible, randomness should be deterministic.

Example:

```python
random.Random(seed)
```

This enables reproducible visualizations.

---

# Performance

Modules should prefer simple algorithms.

Avoid:

- rebuilding large Python lists unnecessarily
- allocating many temporary objects
- unnecessary copying

Simulation should generate logical geometry.

The native backend performs expensive work.

---

# Threading

Modules execute on the main thread.

Modules should assume:

```
single-threaded execution
```

Future background systems (audio analysis, asset loading, etc.) will communicate through Context or Services.

---

# Communication Between Modules

Modules should remain independent.

Preferred communication:

```
Context

Signals

Shared Services
```

Avoid directly calling methods on other modules.

Loose coupling keeps modules reusable.

---

# Module Composition

Small modules are encouraged.

Instead of one enormous visualization:

```
EverythingModule
```

Prefer:

```
Grid

+

Audio

+

Particles

+

Overlay

+

Radar
```

These combine naturally inside the Frame.

---

# Example Module

```python
class Wave(Module):

    def __init__(self):

        self.phase = 0.0

    def update(self, context):

        self.phase += context.dt

    def build(self, frame):

        geometry = ...

        renderable = Renderable(

            geometry=geometry,

            material=...

        )

        frame.add(renderable)
```

Notice the complete absence of rendering code.

---

# Things Modules Must Never Do

Modules should never:

- import OpenGL
- call glDrawArrays()
- allocate VBOs
- compile shaders
- upload vertices
- bind textures
- call native rendering functions directly

Those responsibilities belong exclusively to the renderer.

---

# Mental Model

A good way to think about a module is this:

```
Input

↓

Simulation

↓

Geometry

↓

Done
```

Everything after geometry belongs to the engine.

---

# Summary

A Retroscope module is a pure procedural geometry generator.

Its responsibilities end the moment it submits Renderables into the Frame.

The rendering backend handles everything else:

- tessellation
- mesh generation
- GPU uploads
- shader management
- draw calls

This strict separation is one of the core architectural principles of Retroscope and is what allows visualization modules to remain simple, expressive, portable, and independent of the underlying graphics API.