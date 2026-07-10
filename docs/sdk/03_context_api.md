# 03 - Context API

Version: 1.0

---

# Introduction

The Context is the engine's shared state object.

Every module receives the same Context instance every frame.

```python
def update(

    self,

    context,

):
```

The Context answers questions like

- What time is it?
- How large is the window?
- What is the current FPS?
- What theme is active?
- What is the current audio level?
- Which keys are pressed?
- Which services are available?

A module should **never** need to import global objects from elsewhere in the engine.

Instead, everything should come through Context.

---

# Philosophy

The Context exists for one reason.

To make modules completely independent from the rest of the engine.

Instead of

```python
from renderer import renderer

from inputs.keyboard import keyboard

from services.logger import logger
```

a module simply receives

```python
context
```

Everything it needs is accessible through that object.

---

# Ownership

The Application owns the Context.

```
Application

↓

Context

↓

Modules
```

Modules never create a Context.

Modules never destroy a Context.

There is exactly one Context.

---

# Lifetime

The Context is created during application startup.

```
App()

↓

Context()

↓

Entire Lifetime

↓

Destroy
```

Unlike a Frame,

the Context is **persistent**.

---

# Responsibilities

The Context stores engine-wide state.

It does **not** perform rendering.

It does **not** own GPU resources.

It does **not** generate geometry.

Instead it exposes information.

---

# Current Structure

Conceptually,

the Context looks like

```python
Context

├── dt

├── elapsed

├── frame

├── fps

├── width

├── height

├── mouse

├── keyboard

├── touch

├── gpio

├── audio

├── theme

├── settings

├── logger

├── profiler

├── recorder

└── signals
```

Some fields already exist.

Others are planned.

The API is intentionally designed to grow without changing modules.

---

# Time

One of the most commonly used fields.

```python
context.dt
```

Represents

```
Seconds

since previous frame.
```

Example

```python
self.phase += context.dt
```

Always use delta time.

Never assume a fixed frame rate.

---

# Elapsed Time

```
context.time
```

or

```
context.elapsed
```

Represents total running time.

Example

```python
math.sin(

    context.time

)
```

Useful for

- oscillation
- animation
- procedural noise
- continuous effects

---

# Frame Number

```
context.frame
```

Represents

```
Current Frame Number
```

Example

```python
if context.frame % 60 == 0:

    ...
```

Useful for diagnostics.

---

# FPS

```
context.fps
```

Current rendering frequency.

Useful for

- diagnostics
- overlays
- adaptive quality

Should not normally affect simulation.

Use

```
dt
```

instead.

---

# Display Size

```
context.width

context.height
```

Represent the current viewport.

Example

```python
center = (

    context.width * 0.5,

    context.height * 0.5

)
```

---

# Aspect Ratio

Future versions may expose

```python
context.aspect
```

instead of requiring

```python
width / height
```

inside every module.

---

# Mouse

Current mouse state.

Conceptually

```python
context.mouse
```

may expose

```python
position

buttons

wheel

delta
```

Example

```python
x = context.mouse.x

y = context.mouse.y
```

---

# Keyboard

Keyboard state.

Conceptually

```python
context.keyboard
```

Example

```python
if context.keyboard.space:

    ...
```

Future versions may support

```
Pressed

Released

Held
```

events.

---

# Touch

Touch input.

Example

```python
context.touch.points
```

Supports

- multitouch
- gestures
- tablets

depending on platform.

---

# GPIO

Available on Raspberry Pi.

Example

```python
context.gpio.read(17)
```

Future modules may react to

- buttons
- rotary encoders
- switches
- sensors

without platform-specific code.

---

# Audio

Probably the most important future subsystem.

Instead of opening microphones,

modules consume processed audio.

Example

```python
context.audio
```

---

# Planned Audio Fields

Future audio analysis may expose

```python
context.audio

rms

peak

fft

waveform

bass

mid

treble

centroid

beat

tempo
```

Modules remain completely independent from the audio implementation.

---

# Example

```python
level = context.audio.rms
```

or

```python
if context.audio.beat:

    ...
```

---

# Theme

Current application theme.

Example

```python
context.theme
```

Typical fields

```python
primary

secondary

grid

background

highlight

warning

success
```

Modules should avoid hardcoded colors whenever possible.

---

# Example

```python
material.color = (

    context.theme.primary

)
```

Changing themes updates every module automatically.

---

# Settings

Application configuration.

```python
context.settings
```

Examples

```
Fullscreen

Brightness

Theme

Audio Device

Target FPS

Window Size
```

Modules should never parse configuration files directly.

---

# Logger

Shared logging service.

```python
context.logger.info(...)
```

Useful for

- diagnostics
- warnings
- debugging

Avoid excessive logging during every frame.

---

# Profiler

Performance measurements.

```python
context.profiler.begin(

    "Snow"

)
```

and

```python
context.profiler.end(

    "Snow"

)
```

Allows modules to contribute timing information.

---

# Recorder

Future recording interface.

Example

```python
context.recorder.start()
```

Modules never write video directly.

---

# Screenshot

Future screenshot interface.

Example

```python
context.screenshot.capture()
```

---

# Signals

Future event system.

Example

```python
context.signals.publish(...)
```

or

```python
context.signals.subscribe(...)
```

Modules communicate indirectly.

---

# Camera

Future versions may expose

```python
context.camera
```

Modules should never create cameras themselves.

---

# Renderer

Notice what is missing.

There is intentionally **no**

```python
context.renderer
```

Modules should never access the renderer.

This keeps rendering completely decoupled from visualization.

---

# OpenGL

Similarly,

there is intentionally no

```python
context.gl
```

or

```python
context.shader
```

Modules never issue GPU commands.

---

# Mutability

Some Context fields change every frame.

Examples

```
dt

fps

mouse

audio
```

Others rarely change.

```
theme

settings

services
```

Modules should treat the Context itself as read-only.

---

# Thread Safety

Modules should assume

Context remains stable throughout one frame.

It is updated before

```
update()
```

is called.

It does not change while modules are executing.

---

# Access Pattern

Typical module

```python
def update(

    self,

    context,

):

    self.phase += context.dt

    level = context.audio.rms

    mouse = context.mouse.position
```

Notice

Everything comes from Context.

Nothing comes from globals.

---

# Why Not Globals?

Imagine

```python
global_mouse

global_theme

global_logger

global_audio
```

Every module becomes tightly coupled.

Testing becomes difficult.

Replacing implementations becomes difficult.

Context solves this problem.

---

# Future Growth

One of the design goals of Context is stability.

New systems can simply be added.

Example

```python
context.midi

context.network

context.bluetooth

context.camera

context.osc

context.serial
```

Existing modules continue working.

---

# Best Practices

✔ Read from Context.

✔ Never modify Context.

✔ Store long-lived state inside your module.

✔ Treat Context as engine state.

✔ Cache values locally if used repeatedly.

---

# Anti-Patterns

Never

```python
Context()
```

inside a module.

Never

```python
global_logger
```

Never

```python
global_audio
```

Never

```python
global_renderer
```

Always use

```python
context
```

---

# Mental Model

Imagine Context as a dashboard.

The module is driving a car.

The dashboard tells you

- speed
- fuel
- engine temperature
- RPM

It does not drive the car.

Similarly,

Context informs the module about the engine.

The module decides what to do with that information.

---

# Example Module

```python
class AudioBars(Module):

    def update(

        self,

        context,

    ):

        self.level = context.audio.rms

        self.phase += context.dt

    def build(

        self,

        frame,

    ):

        ...
```

Notice

No globals.

No imports from engine internals.

Everything flows through Context.

---

# Summary

The Context is the central gateway between visualization modules and the rest of the Retroscope engine.

It provides controlled, read-only access to shared engine state including

- time
- display information
- input devices
- audio analysis
- themes
- services
- settings

while deliberately hiding rendering details.

By routing all shared information through a single object, Retroscope achieves loose coupling, simplifies testing, improves portability, and allows the engine to evolve without breaking existing modules.

A module should think of Context as **its window into the engine**—the only window it needs.