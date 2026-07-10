# 07 - Context

# Introduction

The Context represents the current state of the application.

Every module receives a Context during its update step.

```
update(context)
```

The Context acts as the module's interface to the rest of the engine.

Instead of exposing global variables or allowing modules to directly access engine internals, Retroscope centralizes all shared state inside the Context.

This keeps modules independent, testable, and portable.

---

# Philosophy

A module should never ask

> "Where do I get the current mouse position?"

or

> "How do I access the renderer?"

Instead, it should simply ask the Context.

The Context is the module's view of the world.

It answers questions like

- What time is it?
- What is the screen size?
- What is the audio level?
- What theme is active?
- Which keys are pressed?
- Which services are available?

---

# The World View

Conceptually

```
Application

↓

Context

↓

Modules
```

Modules never communicate directly with the Application.

Everything flows through Context.

---

# Lifetime

There is exactly one Context.

```
Application

↓

Context

↓

Entire lifetime
```

It exists for the duration of the application.

Every module receives a reference to the same Context.

---

# Responsibilities

Context owns no rendering logic.

It owns no simulation.

Instead, it exposes shared engine state.

Examples

```
Time

Display

Input

Audio

Theme

Settings

Services

Signals
```

---

# Why A Context Exists

Without Context, modules would need code like

```python
from renderer import renderer

from audio import microphone

from keyboard import keyboard

from settings import settings
```

Every module becomes tightly coupled to the engine.

Instead

```python
def update(self, context):
```

Everything becomes

```
context.audio

context.theme

context.mouse

context.keyboard
```

This greatly simplifies development.

---

# Current Structure

Conceptually

```
Context

├── Time

├── Display

├── Audio

├── Theme

├── Input

├── Services

├── Settings

└── Signals
```

Some systems already exist.

Others are planned.

---

# Time

One of the most frequently used pieces of Context.

Typical fields

```
dt

elapsed

frame

fps
```

Example

```python
self.phase += context.dt
```

Every animation should use delta time.

Avoid fixed increments.

---

# Delta Time

Delta time is measured in seconds.

Example

```
60 FPS

↓

dt ≈ 0.0167
```

```
30 FPS

↓

dt ≈ 0.0333
```

Animations should always use dt.

---

# Elapsed Time

Elapsed time represents the application's running time.

Example

```python
math.sin(context.time)
```

Useful for

- oscillation
- procedural animation
- repeating effects

---

# Frame Counter

Context may expose

```
frame_number
```

Useful for

- diagnostics
- recording
- deterministic effects

---

# Screen Information

Context exposes display information.

Typical fields

```
Width

Height

Aspect Ratio
```

Example

```python
center = (

    context.width / 2,

    context.height / 2

)
```

---

# Resize Events

Modules should never query OpenGL directly.

Instead

```
context.width

context.height
```

always represent the current display.

---

# Audio

Future audio visualizations will access

```
context.audio
```

rather than opening microphones themselves.

Example

```
context.audio.rms

context.audio.peak

context.audio.fft

context.audio.bass
```

Audio modules become reusable across platforms.

---

# Input

Mouse

Keyboard

Touch

GPIO

All belong inside Context.

Example

```
context.mouse.position

context.mouse.buttons

context.keyboard.keys

context.touch.points
```

Modules remain platform-independent.

---

# Theme

The current visual theme is exposed through Context.

Example

```
context.theme.primary

context.theme.grid

context.theme.background
```

Modules should generally avoid hardcoded colors.

---

# Services

Shared engine services also live inside Context.

Examples

```
Logger

Profiler

Recorder

Screenshot

Settings
```

Example

```python
context.logger.info(...)
```

or

```python
context.profiler.begin(...)
```

---

# Settings

User settings are available through Context.

Examples

```
Fullscreen

VSync

Theme

Audio Device

Brightness
```

Modules should never read configuration files directly.

---

# Signals

Future versions will expose an event system.

Example

```
context.signals.publish(...)

context.signals.subscribe(...)
```

allowing modules to communicate without referencing one another.

---

# Renderer

Modules should **not** receive the renderer.

This is intentional.

Modules should never call

```
context.renderer.draw()
```

Doing so would break the architecture.

---

# OpenGL

Context intentionally exposes no OpenGL objects.

No

```
VBO

VAO

Shader

Framebuffer
```

appear inside Context.

Those belong exclusively to the renderer.

---

# Module Communication

Suppose

```
Audio Module

↓

Beat Detection

↓

Particle Module
```

Instead of

```
particle.audio_module
```

the Audio Module publishes

```
context.audio.beat
```

or emits a Signal.

This keeps modules independent.

---

# Future Camera

If cameras are introduced,

they belong inside Context.

Example

```
context.camera
```

rather than being globally accessible.

---

# Future Physics

If a physics engine is added,

modules would access it through

```
context.physics
```

Again,

the Context remains the single gateway.

---

# Example

```python
def update(

    self,

    context,

):

    self.phase += context.dt

    level = context.audio.rms

    if context.keyboard.space:

        self.reset()
```

Notice that the module has no knowledge of where any of this data originates.

---

# Ownership

Context owns references to engine systems.

Modules never own those systems.

```
Application

↓

Context

↓

Shared Systems
```

This prevents duplication.

---

# Thread Safety

Modules should assume Context is updated before update() begins.

Context should remain stable throughout the frame.

This guarantees deterministic behaviour.

---

# Best Practices

Always obtain shared state through Context.

Good

```python
context.audio.rms
```

Bad

```python
AudioService.instance()
```

Good

```python
context.theme.primary
```

Bad

```python
from themes.green import GREEN
```

The Context should always be the single source of truth.

---

# Design Goals

The Context should be

Simple

Stable

Centralized

Platform Independent

Extensible

It should expose engine state without exposing engine implementation.

---

# Mental Model

Imagine every module living inside its own room.

The module cannot see the rest of the application directly.

Instead,

the Context is a window.

Everything outside the room is visible through that window.

If a module needs information,

it looks through the Context.

It never leaves the room.

---

# Summary

The Context is the central interface between modules and the engine.

It provides controlled access to shared state including

- time
- display
- input
- audio
- themes
- services
- settings
- signals

while intentionally hiding rendering details.

By routing all shared engine state through a single object, Retroscope keeps modules independent from the application, renderer, and platform.

This makes modules easier to write, easier to test, and dramatically easier to reuse across different visualizations.