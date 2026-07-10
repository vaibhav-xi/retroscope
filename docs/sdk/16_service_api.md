# 16 - Services API

Version: 1.0

---

# Introduction

Services are long-lived engine systems that provide functionality shared across the entire application.

Unlike Modules, which create visualizations, Services provide infrastructure.

Examples include

- logging
- profiling
- screenshots
- settings
- recording
- future networking
- asset management

A Service does not render geometry.

A Service does not simulate visuals.

A Service provides capabilities to the engine.

---

# Philosophy

Retroscope separates

```
Visualization

↓

Modules

Infrastructure

↓

Services
```

This keeps modules focused entirely on creating visuals while common functionality remains centralized.

---

# Current Services

Current directory

```
services/

├── logger.py

├── profiler.py

├── recorder.py

├── screenshot.py

└── settings.py
```

Each service has one clearly defined responsibility.

---

# Why Services Exist

Imagine every module containing

```
logging

↓

profiling

↓

saving screenshots

↓

configuration loading
```

Every module becomes cluttered.

Instead,

modules delegate these tasks to Services.

---

# Ownership

Services belong to the application.

```
App

↓

Services

↓

Modules
```

Modules never own services.

---

# Lifetime

Typical lifetime

```
Application Starts

↓

Services Created

↓

Used Entire Runtime

↓

Application Exits

↓

Services Destroyed
```

Services are persistent objects.

---

# Access Pattern

Eventually,

services are accessed through Context.

Example

```python
context.logger

context.profiler

context.settings
```

This avoids global imports.

---

# Logger Service

Purpose

Provide consistent logging throughout the engine.

Instead of

```python
print(...)
```

future modules may use

```python
context.logger.info(

    "Loaded Grid Module"

)
```

---

# Logging Levels

Future

```
Debug

Info

Warning

Error

Critical
```

This allows filtering and structured output.

---

# Example

```python
context.logger.warning(

    "Microphone disconnected"

)
```

---

# Profiler Service

Current implementation already exists.

Purpose

Measure execution time.

Example

```python
context.profiler.begin(

    "Particle Update"

)

...

context.profiler.end(

    "Particle Update"

)
```

Useful for optimization.

---

# Current Usage

The renderer currently profiles

```
Geometry Builder

↓

Render Graph
```

Future versions will profile

- modules
- render passes
- audio processing
- simulation

---

# Recorder Service

Future purpose

Record

- screenshots
- animations
- audio
- parameter changes

Useful for demonstrations and debugging.

---

# Example

```python
context.recorder.start()
```

Future

```
Record

↓

MP4

↓

GIF

↓

PNG Sequence
```

---

# Screenshot Service

Purpose

Capture the current framebuffer.

Future

```python
context.screenshot.capture()
```

Modules never interact directly with OpenGL framebuffers.

---

# Settings Service

Purpose

Expose application configuration.

Example

```python
context.settings.fullscreen

context.settings.vsync

context.settings.show_grid
```

Modules observe settings rather than storing global configuration.

---

# Asset Service (Future)

Potential

```python
context.assets.load_image()

context.assets.load_font()

context.assets.load_sound()
```

This removes filesystem logic from modules.

---

# Resource Cache

Future asset service may automatically cache

```
Fonts

Textures

Images

Shaders
```

avoiding repeated loading.

---

# Audio Service

Although Audio has its own API,

internally it is also a Service.

```
Audio Device

↓

Audio Service

↓

Context.audio
```

Modules never own microphones.

---

# Input Services

Future

```
Keyboard

Mouse

Touch

GPIO
```

will internally be services,

even if exposed through Context.

---

# Theme Service

Future

```
context.theme
```

may itself be backed by a Theme Service.

Modules only see the public API.

---

# Event Service

Future

```
context.signals
```

may internally use a Service responsible for

- subscriptions
- dispatch
- events

---

# Configuration Service

Eventually

```
Presets

↓

Themes

↓

Settings

↓

Persistence
```

may all share a common configuration service.

---

# Network Service (Future)

Potential

```
OSC

MIDI

WebSocket

REST

Remote Control
```

Modules remain unaware of networking implementation.

---

# MIDI Service

Possible future

```python
context.midi
```

Allowing visualizations to react to

- keyboards
- synthesizers
- drum pads

without platform-specific code.

---

# File Watcher

Development builds may expose

```
Shader Reload

Theme Reload

Module Reload
```

through a background service.

---

# Threading

Services may internally use worker threads.

Modules should treat services as thread-safe interfaces rather than managing synchronization themselves.

---

# Communication

Modules communicate with services.

Services generally should not communicate directly with modules.

Example

```
Module

↓

Logger

✓

Logger

↓

Module

✗
```

This keeps dependencies one-directional.

---

# Singleton Avoidance

Although services behave similarly to singletons,

Retroscope avoids exposing true global singletons.

Instead,

everything flows through Context.

This makes testing much easier.

---

# Dependency Injection

Context effectively injects all required services.

Instead of

```python
Logger()

Profiler()

Settings()
```

inside every module,

the engine constructs them once.

---

# Responsibilities

A Service should

✔ perform one infrastructure task

✔ be reusable

✔ be long-lived

✔ avoid visualization logic

---

# Things That Are NOT Services

Modules

Geometry

Meshes

Shaders

Materials

Renderables

These belong to the rendering pipeline,

not the infrastructure layer.

---

# Best Practices

✔ Keep services focused.

✔ Expose simple APIs.

✔ Access services through Context.

✔ Keep modules independent of implementations.

---

# Anti-Patterns

Avoid

```python
print(...)
```

for engine diagnostics.

Avoid

```python
open("settings.json")
```

inside modules.

Avoid

duplicating profiler logic.

Use existing services instead.

---

# Mental Model

Think of the Services layer as the operating system of Retroscope.

Modules are applications.

Applications shouldn't implement

- file systems
- networking
- logging
- scheduling

They simply ask the operating system to perform those tasks.

Likewise,

Retroscope modules should rely on Services for infrastructure while focusing entirely on visualization.

---

# Future Vision

As Retroscope evolves,

the Services layer is expected to grow significantly.

Future services may include

- Asset Management
- MIDI
- OSC
- Networking
- Preset Management
- Plugin Loading
- AI-assisted parameter generation
- Remote control
- Shader hot-reloading
- Performance telemetry

All of these can be introduced without changing the module architecture because Services remain isolated behind stable interfaces.

---

# Summary

Services provide the shared infrastructure that powers Retroscope.

They encapsulate logging, profiling, recording, screenshots, settings, and future engine-wide functionality while remaining independent of visualization modules.

By accessing services through the Context rather than through globals or direct imports, modules stay lightweight, testable, and focused solely on generating procedural visuals.

Services are the engine's infrastructure layer—the unseen systems that support every visualization without becoming part of the visualization itself.