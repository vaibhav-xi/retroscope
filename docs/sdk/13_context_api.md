# 13 - Context API

Version: 1.0

---

# Introduction

The **Context** object is the shared runtime environment of Retroscope.

Every major subsystem has its own responsibility.

```
Modules

↓

Context

↓

Engine Services
```

Rather than allowing modules to access global variables, the engine exposes a single Context object containing everything a module should know about the running application.

The Context is the primary communication interface between the engine and visualization modules.

---

# Philosophy

A module should never ask

```
Where is the renderer?

Where is the audio engine?

Where is the profiler?

Where is the theme?

Where are the settings?
```

Instead it receives

```
Context
```

The Context becomes the module's "window" into the engine.

---

# Design Goals

The Context should

- avoid global variables
- avoid singleton abuse
- provide read-only engine state
- expose useful services
- remain stable over time

The Context is intentionally designed so that modules rarely need anything outside it.

---

# Ownership

The application owns the Context.

```
App

↓

Context

↓

Modules
```

Modules should never construct their own Context.

---

# Lifetime

The Context lives for the duration of the application.

```
Application Start

↓

Context Created

↓

Used Every Frame

↓

Destroyed At Exit
```

---

# Current Context

Today the Context is intentionally lightweight.

It primarily exists to provide a stable API for future expansion.

As Retroscope grows, additional engine services will be added without changing existing module code.

---

# What Context Represents

Think of Context as

```
Engine State
```

rather than

```
Engine Logic
```

Modules read from it.

They rarely modify it.

---

# Typical Usage

Future module code will resemble

```python
def update(self, context):

    dt = context.dt

    mouse = context.mouse.position

    color = context.theme.primary
```

Notice that the module never imports those systems directly.

---

# Time

One of the most commonly used Context values is

```
dt
```

Conceptually

```python
context.dt
```

Represents

```
Seconds Since Previous Frame
```

Modules should use this for animation.

Example

```python
angle += speed * context.dt
```

Never assume a fixed frame rate.

---

# Elapsed Time

Future versions expose

```python
context.time
```

Representing

```
Seconds Since Application Start
```

Useful for

- oscillations
- procedural animation
- noise
- phase calculations

---

# Screen Information

Future fields

```python
context.width

context.height
```

Represent the current viewport.

Modules can build responsive layouts without accessing the window system.

---

# Viewport

Future

```python
context.viewport
```

Conceptually

```
(x, y, width, height)
```

Useful for advanced rendering modules.

---

# Theme

The active application theme is exposed through

```python
context.theme
```

Modules should obtain colors from here instead of hardcoding RGB values.

Example

```python
renderable.material.color = (

    context.theme.primary
)
```

Changing themes automatically affects every module.

---

# Audio

Audio data will be accessed through

```python
context.audio
```

Future properties include

```python
context.audio.rms

context.audio.peak

context.audio.fft

context.audio.bass

context.audio.mid

context.audio.treble
```

Modules should never communicate directly with PyAudio.

---

# Input

Future Context exposes

```
Mouse

Keyboard

Touch

GPIO
```

Example

```python
context.mouse.position

context.keyboard.keys

context.touch.points
```

Again,

modules avoid importing platform-specific code.

---

# Settings

Global application settings

```
context.settings
```

Example

```python
context.settings.show_grid
```

Future UI panels modify settings.

Modules simply observe them.

---

# Parameters

Module parameters eventually become

```python
context.parameters
```

or

```python
self.parameters
```

depending on the final design.

These values may be editable through the UI.

---

# Signals

Engine-wide events will be exposed through

```
context.signals
```

Example

```
Preset Changed

↓

Signal

↓

Modules React
```

Modules do not need direct references to one another.

---

# Logger

Future

```python
context.logger
```

Instead of

```python
print(...)
```

Modules can log consistently.

---

# Profiler

Future

```python
context.profiler
```

Allows expensive algorithms to be measured.

Example

```python
context.profiler.begin(

    "Particle Update"

)
```

---

# Recorder

Future

```python
context.recorder
```

Allows modules to record data without knowing implementation details.

---

# Screenshot Service

Future

```python
context.screenshot.capture()
```

Useful for automated exports.

---

# Resource Access

Future

```python
context.assets
```

Allows modules to locate

- images
- sounds
- fonts

without hardcoding filesystem paths.

---

# Window Information

Future

```python
context.window
```

Provides

- DPI
- fullscreen
- size
- monitor information

---

# Renderer

Modules generally should **not** access the renderer directly.

However,

future advanced modules may query limited renderer capabilities through

```python
context.renderer
```

without exposing OpenGL.

---

# Camera

Future

```python
context.camera
```

Allows modules to position objects relative to the current view.

---

# Random Generator

Instead of

```python
random.random()
```

future modules may use

```python
context.random
```

allowing deterministic playback and reproducible presets.

---

# Platform Information

Future

```python
context.platform
```

Could expose

```
macOS

Linux

Raspberry Pi

Windows
```

Only when truly necessary.

Most modules should remain platform-independent.

---

# Module Communication

Context intentionally replaces direct module references.

Instead of

```
Audio Module

↓

Wave Module
```

communication becomes

```
Audio Module

↓

Context.audio

↓

Wave Module
```

Modules remain independent.

---

# Read vs Write

Modules should mostly

```
Read
```

from Context.

Only specific services may allow modification.

Examples

Allowed

```
Read Audio

Read Time

Read Theme
```

Not recommended

```
Modify Renderer

Replace Theme

Change Window
```

---

# Dependency Injection

Context effectively provides dependency injection.

Instead of

```python
Audio()

Theme()

Renderer()
```

being constructed by every module,

the engine provides them once.

---

# Future Context Layout

Conceptually

```python
Context

├── dt

├── time

├── width

├── height

├── viewport

├── theme

├── audio

├── mouse

├── keyboard

├── touch

├── gpio

├── profiler

├── logger

├── settings

├── recorder

├── camera

├── assets

└── random
```

Not every field exists today,

but this represents the long-term design.

---

# Best Practices

✔ Read engine state from Context.

✔ Avoid global variables.

✔ Avoid importing unrelated systems.

✔ Treat Context as read-mostly.

✔ Keep modules loosely coupled.

---

# Anti-Patterns

Avoid

```python
from renderer import Renderer
```

Avoid

```python
from audio import AudioEngine
```

Avoid

```python
from theme import Theme
```

Instead,

access them through Context when appropriate.

---

# Mental Model

Imagine a pilot flying an aircraft.

The pilot doesn't connect directly to every subsystem.

Instead,

there is a dashboard containing

- altitude
- speed
- fuel
- engine status
- navigation

The pilot interacts only with the dashboard.

The Context is that dashboard.

Modules don't talk directly to the renderer, audio engine, input devices, or settings system.

They simply observe the Context.

---

# Future Evolution

As Retroscope grows,

the Context will become the primary stable API exposed to module authors.

New engine capabilities should almost always appear as new Context fields rather than new global systems.

This minimizes breaking changes and keeps modules portable across future engine versions.

---

# Summary

The Context object is Retroscope's shared runtime environment.

It provides modules with controlled access to engine state, services, timing, themes, input, audio, and future subsystems while keeping modules isolated from engine internals.

By centralizing shared information in a single object, the engine avoids global state, simplifies module development, and creates a stable API that can expand significantly without requiring changes to existing visualizations.

For module authors, the Context should be viewed as **the primary interface to the engine itself**.