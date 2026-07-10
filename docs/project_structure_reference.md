# 27 - Project Structure Reference

Version: 1.0

---

# Introduction

This document serves as the complete map of the Retroscope source tree.

Unlike the rest of the SDK, which explains systems conceptually, this document explains **every major directory and file** inside the repository.

Its goal is simple:

> A developer should be able to navigate the entire Retroscope source tree without asking where functionality lives.

This document should be treated as the architectural index of the project.

---

# Top-Level Layout

Current repository

```
retroscope/

├── assets/
├── core/
├── inputs/
├── modules/
├── plugins/
├── presets/
├── render/
├── render_es2/
├── services/
├── themes/
├── ui/
├── web/

├── config.py
├── main.py
├── README.md
└── setup.py
```

The repository is intentionally divided into high-level subsystems.

Each directory has one primary responsibility.

---

# Repository Philosophy

Retroscope separates code into three broad layers.

```
Application Layer

↓

Engine Layer

↓

Rendering Layer
```

The application orchestrates everything.

The engine describes visualization.

The renderer executes drawing.

---

# assets/

Purpose

Static resources.

Contains

```
fonts/

images/

sounds/
```

These are passive resources.

No engine logic belongs here.

Future additions may include

```
models/

icons/

shaders/
```

---

# core/

Purpose

Engine architecture.

Everything related to application flow lives here.

Current files

```
app.py

context.py

frame.py

manager.py

module.py

parameters.py

render_graph.py

settings.py

signal.py
```

---

## app.py

Application entry point.

Responsible for

- window loop
- timing
- module execution
- renderer invocation

Acts as the runtime coordinator.

---

## context.py

Shared engine state.

Eventually exposes

```
audio

theme

settings

services

time

input

window
```

Modules read Context.

They do not own it.

---

## frame.py

Temporary container for one frame.

Collects Renderables produced by modules.

Destroyed after rendering.

---

## manager.py

Module manager.

Responsibilities

- discover modules
- initialize modules
- update modules
- coordinate execution

Eventually may support

- plugins
- hot reload
- dependencies

---

## module.py

Defines the Module base class.

Every visualization inherits from this class.

This is the public API used by module developers.

---

## parameters.py

Foundation of the future parameter system.

Will expose editable values

- UI
- presets
- automation
- MIDI

---

## render_graph.py

High-level render graph.

Coordinates render passes.

Should not contain rendering logic itself.

---

## settings.py

Application configuration.

Examples

- fullscreen
- vsync
- target FPS

Distinct from module parameters.

---

## signal.py

Event bus.

Provides communication between otherwise independent systems.

---

# inputs/

Purpose

Hardware abstraction.

Current files

```
audio.py

gpio.py

keyboard.py

mouse.py

touch.py
```

The renderer never accesses hardware directly.

Everything flows through these abstractions.

---

## audio.py

Microphone acquisition.

Eventually

- RMS
- FFT
- beat detection
- spectrum

---

## keyboard.py

Keyboard polling.

Future

- actions
- shortcuts
- text input

---

## mouse.py

Mouse state.

Future

- cursor
- buttons
- wheel

---

## touch.py

Touchscreen abstraction.

Especially important for Raspberry Pi.

---

## gpio.py

GPIO abstraction.

Allows Retroscope to integrate with

- buttons
- encoders
- sensors
- custom hardware

without platform-specific module code.

---

# modules/

Purpose

Visualization library.

This is where nearly all creative work happens.

Every directory contains one visualization.

Example

```
wave/

grid/

overlay/

audio/

demo/
```

Future

```
particles/

jarvis/

snow/

sand/

radar/

dna/
```

---

## Module Philosophy

Modules never render.

Modules only generate geometry.

---

# plugins/

Purpose

Future third-party extensions.

Long-term goal

Drop a folder into

```
plugins/
```

and Retroscope discovers it automatically.

---

# presets/

Purpose

Persistent visualization configuration.

Stores

- parameter values
- themes
- enabled modules

Future

JSON serialization.

---

# render/

Purpose

Renderer-independent scene description.

Contains engine-side rendering abstractions.

Current files

```
builder_registry.py

primitives.py

renderable.py

transform.py
```

Nothing here depends on OpenGL.

---

## builder_registry.py

Maps primitive types to Geometry Builders.

Allows new primitive types without modifying the renderer.

---

## primitives.py

Defines logical geometry.

Examples

Polyline

Circle

Rectangle

Arc

Future additions belong here.

---

## renderable.py

The central rendering object.

Owns

- Geometry
- Material
- Transform
- Mesh
- Dirty state

Modules primarily interact with Renderables.

---

## transform.py

Stores spatial transforms.

Current

- translation

Future

- rotation
- scale
- matrices

---

# render_es2/

Purpose

Concrete renderer.

Implements the rendering backend.

Current backend

OpenGL ES 2.0

Desktop OpenGL compatibility.

---

Current files

```
renderer.py

shader.py

mesh.py

geometry_builder.py

geometry.py

vertex_buffer.py

material.py

texture.py

framebuffer.py

render_graph.py

render_packet.py

render_pass.py

passes/
```

This layer converts engine data into GPU commands.

---

## renderer.py

Top-level renderer.

Coordinates

- geometry build
- render graph
- profiler

Acts as the rendering entry point.

---

## geometry_builder.py

Converts Geometry into native vertex buffers.

One of the most performance-critical parts of the engine.

---

## geometry.py

Intermediate geometry container.

Holds generated vertices before upload.

---

## mesh.py

Python wrapper around the native Mesh object.

Owns almost no rendering logic.

Delegates to

```
_native.Mesh
```

---

## shader.py

Python wrapper around native Shader.

Compiles programs.

Sets uniforms.

Eventually becomes an extremely thin wrapper.

---

## material.py

Stores rendering appearance.

Examples

- color
- opacity
- blending

Renderer interprets these values.

---

## vertex_buffer.py

Python-side interface to the native VertexBuffer.

---

## texture.py

Reserved for future texture support.

---

## framebuffer.py

Reserved for offscreen rendering.

Future

- bloom
- CRT
- post-processing

---

## render_graph.py

Renderer-specific graph.

Executes render passes.

Distinct from the engine RenderGraph.

---

## render_packet.py

Collects renderables into an efficient rendering representation.

Acts as the bridge between engine and renderer.

---

## render_pass.py

Base class for rendering passes.

Future examples

- Geometry
- Bloom
- CRT
- UI
- Post Processing

---

## passes/

Individual rendering passes.

Current

```
geometry.py
```

Future

```
shadow.py

crt.py

bloom.py

ui.py
```

---

# render_es2/_native/

Purpose

Performance-critical native implementation.

This directory represents the lowest layer of the renderer.

Everything here is written in C.

Current objects

```
Mesh

Shader

VertexBuffer

Stroke Builder
```

---

## wrapper.c

Module entry point.

Registers Python types.

Exports native functions.

---

## mesh_object.c

Native Mesh.

Owns

- VAO
- VBO
- Draw calls

---

## shader_object.c

Native Shader.

Owns

- Program
- Uniform locations
- Compilation
- Linking

---

## vertex_buffer_object.c

Persistent native vertex storage.

Avoids Python allocations.

---

## stroke.c

Polyline tessellation.

Converts logical lines into triangles.

---

## geometry.c

Native geometry helpers.

Supports Geometry Builder.

---

## gl_platform.h

Platform abstraction.

Supports

- macOS
- Raspberry Pi
- Linux

without scattering platform checks throughout the renderer.

---

## setup.py

Builds the native extension.

Produces

```
_native.so
```

---

# services/

Purpose

Engine infrastructure.

Current

```
logger

profiler

recorder

settings

screenshot
```

Modules should access these through Context rather than importing them directly.

---

# themes/

Purpose

Visual appearance.

Contains semantic color palettes.

Examples

```
Amber

Cyberpunk

Oscilloscope

Blue
```

Themes define colors.

They never define geometry.

---

# ui/

Purpose

Future desktop interface.

Potential responsibilities

- parameter editor
- module browser
- profiler
- scene hierarchy

---

# web/

Purpose

Remote control interface.

Current structure

```
templates/

static/
```

Future

- dashboards
- mobile control
- parameter editing
- monitoring

---

# config.py

Global configuration.

Contains project-wide constants.

Should remain small.

---

# main.py

Application entry point.

Creates

```
App

↓

Run
```

Almost no engine logic belongs here.

---

# README.md

Project overview.

Installation.

Getting started.

Quick examples.

---

# setup.py

Python packaging.

Builds and installs Retroscope.

---

# Architectural Layers

The repository can be viewed as five stacked layers.

```
Applications

↓

Modules

↓

Engine

↓

Renderer

↓

Native Backend
```

Each layer depends only on the one below it.

---

# Dependency Rules

Allowed

```
Modules

↓

Renderables

↓

Renderer
```

Not allowed

```
Renderer

↓

Modules
```

Dependencies always point downward.

---

# Typical Code Path

When a frame is rendered

```
main.py

↓

App

↓

Module Manager

↓

Modules

↓

Frame

↓

Geometry Builder

↓

Render Packet

↓

Render Graph

↓

Native Mesh

↓

OpenGL

↓

Display
```

Every file in the repository participates in one stage of this pipeline.

---

# Where Should New Code Go?

Visualization?

```
modules/
```

Engine abstraction?

```
core/
```

Rendering?

```
render_es2/
```

GPU optimization?

```
_native/
```

Appearance?

```
themes/
```

Infrastructure?

```
services/
```

Hardware?

```
inputs/
```

Keeping code in the correct directory is one of the most important architectural practices in Retroscope.

---

# Summary

The Retroscope repository is intentionally organized into independent subsystems, each with a narrowly defined responsibility. High-level application logic resides in `core`, visualization algorithms live in `modules`, renderer-independent scene abstractions are defined in `render`, the OpenGL ES backend is implemented in `render_es2`, and performance-critical GPU interaction is isolated within the native C extension.

This layered organization allows the engine to grow organically while remaining understandable. Developers should always place new functionality into the subsystem that best matches its responsibility, preserving the clean separation between architecture, visualization, rendering, and platform-specific implementation that defines the Retroscope project.