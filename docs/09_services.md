# 09 - Services

# Introduction

Services are long-lived engine components that provide functionality shared across the entire application.

Unlike Modules, Services do not generate visuals.

Unlike Renderables, Services are never rendered.

Instead, Services perform supporting tasks that every part of the engine may rely upon.

Examples include

- logging
- profiling
- screenshots
- recording
- settings
- asset loading
- networking
- telemetry

A Service exists independently of any particular visualization.

---

# Philosophy

Modules should focus entirely on visualization.

If a feature is useful to many modules, it belongs in a Service.

For example,

A Wave module should generate wave geometry.

It should **not** know

- how screenshots are written
- how log files are formatted
- where recordings are stored
- how profiling works

Those responsibilities belong to Services.

---

# High Level Architecture

```
                Application
                      │
              Service Manager
                      │
     ┌────────┬────────┬────────┐
     │        │        │        │
 Logger   Profiler  Recorder  Settings
     │        │        │        │
     └────────┴────────┴────────┘
                      │
                  Context
                      │
                   Modules
```

Modules never instantiate Services.

They simply use them.

---

# Lifetime

Services are created once during application startup.

```
Application Start

↓

Create Services

↓

Entire Runtime

↓

Shutdown
```

Unlike Frames,

Services are persistent.

---

# Ownership

The Application owns every Service.

```
Application

↓

Service Manager

↓

Individual Services
```

Modules never own Services.

---

# Why Services Exist

Imagine every module writing log files independently.

```
Wave

↓

wave.log

Grid

↓

grid.log

Particles

↓

particles.log
```

This quickly becomes unmanageable.

Instead,

everyone shares

```
Logger
```

---

# Access Through Context

Modules should access Services through Context.

Example

```python
context.logger.info(
    "Beat detected"
)
```

or

```python
context.profiler.begin(
    "Particles"
)
```

The Context acts as the gateway.

---

# Logger Service

Purpose

```
Messages

↓

Console

↓

File

↓

Remote
```

Responsibilities

- informational messages
- warnings
- errors
- debugging

Example

```python
context.logger.info(
    "Audio initialized"
)
```

---

# Logging Philosophy

Modules should log meaningful events.

Examples

Good

```
Loaded preset

Audio device changed

Shader compilation failed
```

Poor

```
Loop iteration

Vertex generated

Every frame
```

Avoid excessive logging.

---

# Profiler Service

The profiler measures execution time.

Example

```
Geometry Builder

↓

0.73 ms
```

Current renderer output already resembles

```
GeometryBuilder

StrokeBuilder

RenderGraph
```

Future modules may contribute their own timings.

---

# Typical Usage

```python
context.profiler.begin(
    "Snow"
)

...

context.profiler.end(
    "Snow"
)
```

This automatically appears in performance reports.

---

# Recorder Service

The Recorder captures application output.

Possible formats

- PNG sequence
- video
- geometry
- replay
- diagnostics

Modules should never write video directly.

---

# Screenshot Service

Provides

```
Current Frame

↓

PNG
```

Future UI buttons may simply call

```python
context.screenshot.capture()
```

---

# Settings Service

Provides access to application configuration.

Examples

```
Brightness

Fullscreen

Theme

Window Size

Audio Device
```

Modules should avoid reading configuration files directly.

---

# Asset Service (Future)

Responsible for loading

- textures
- fonts
- icons
- sounds
- shaders

Instead of

```python
open(...)
```

modules would request

```python
context.assets.load(...)
```

---

# Audio Service

Future audio modules should never open microphones.

Instead,

```
Audio Service

↓

Microphone

↓

FFT

↓

Beat Detection

↓

Context
```

Modules consume processed information.

---

# Input Service

Similarly,

Keyboard

Mouse

Touch

GPIO

can all be managed centrally.

Modules remain platform-independent.

---

# Theme Service

Instead of importing theme files,

modules use

```python
context.theme.primary
```

Changing themes affects every module automatically.

---

# Signal Service

Future versions may expose an event bus.

```
Audio

↓

Beat

↓

Signal

↓

Particles
```

Modules remain independent.

---

# Recorder Example

Suppose a user presses Record.

```
UI

↓

Recorder Service

↓

Capture Frames
```

The visualization module never changes.

---

# Screenshot Example

```
User

↓

Screenshot Service

↓

Current Frame

↓

PNG
```

Again,

modules remain unaware.

---

# Profiler Example

```
Wave Module

↓

Profiler

↓

0.45 ms
```

Developers can immediately identify expensive modules.

---

# Dependency Injection

Modules should never construct Services.

Bad

```python
logger = Logger()
```

Good

```python
context.logger
```

This guarantees there is exactly one Logger.

---

# Global State

Services intentionally replace global variables.

Instead of

```python
GLOBAL_SETTINGS
```

use

```python
context.settings
```

Instead of

```python
global_logger
```

use

```python
context.logger
```

---

# Threading

Services may internally use worker threads.

Modules should never assume how a Service performs its work.

For example,

Recording may happen asynchronously.

Logging may buffer writes.

Asset loading may occur in the background.

The interface remains unchanged.

---

# Future Services

Potential additions include

```
Network

OSC

MIDI

DMX

Bluetooth

Serial

OSCilloscope Capture

Camera

Motion Capture

WebSocket

REST API
```

All become available through Context.

---

# Testing

Services make testing easier.

A fake Logger can replace the real Logger.

A fake Audio Service can provide deterministic audio.

Modules require no changes.

---

# Performance

Services should generally

- allocate once
- reuse memory
- avoid per-frame allocations
- avoid unnecessary synchronization

Modules should assume Services are inexpensive to access.

---

# Best Practices

Good

```python
context.logger.warning(...)
```

Good

```python
context.profiler.begin(...)
```

Good

```python
context.settings.theme
```

Avoid

```python
Logger()

Settings()

Recorder()

AudioAnalyzer()
```

inside modules.

---

# Mental Model

Imagine Modules as musicians.

Services are the crew behind the stage.

The musicians perform.

The crew

- controls lighting
- records the show
- adjusts microphones
- manages cameras
- operates the mixing desk

The performers never need to know how those systems work.

They simply perform.

---

# Current Services

The current Retroscope engine already contains or is structured around several core services.

```
Logger

Profiler

Recorder

Screenshot

Settings
```

These provide the foundation for future engine features while remaining independent of rendering.

---

# Future Direction

As Retroscope grows,

most new engine-wide functionality should become Services.

This keeps

Modules

↓

Visualization

and

Services

↓

Infrastructure

cleanly separated.

---

# Summary

Services provide reusable engine functionality that exists independently of rendering.

They perform supporting tasks such as

- logging
- profiling
- recording
- screenshots
- settings management
- asset loading
- audio processing

Modules access Services exclusively through the Context, ensuring loose coupling and avoiding global state.

This architecture allows visualization code to remain focused solely on generating geometry while infrastructure concerns are centralized into reusable, testable components shared across the entire application.