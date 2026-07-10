# 17 - Parameters & Settings API

Version: 1.0

---

# Introduction

One of Retroscope's core goals is that **every visualization should be configurable without modifying code**.

A module should expose parameters that describe its behavior.

Examples include

- waveform amplitude
- particle count
- snow density
- hologram rotation speed
- grid spacing
- glow strength
- line thickness

These values should eventually be editable from

- UI
- Web UI
- OSC
- MIDI
- Presets
- Remote APIs

without changing the module itself.

---

# Philosophy

A module should separate

```
Behavior

↓

Parameters

Logic

↓

Update()

Rendering

↓

Build()
```

Instead of writing

```python
speed = 2.5
```

inside the algorithm,

the module should expose

```python
speed
```

as a configurable parameter.

---

# Why Parameters?

Imagine changing

- grid spacing
- waveform frequency
- particle count

If those values are hardcoded,

every change requires editing source code.

Instead

```
UI

↓

Parameter

↓

Module

↓

Visualization
```

Everything becomes interactive.

---

# Current State

Today,

Retroscope contains

```
core/

parameters.py
```

along with

```
core/settings.py
```

The architecture is already preparing for a unified parameter system.

---

# Parameters vs Settings

These two concepts are intentionally different.

## Parameters

Describe

**module behavior**

Examples

```
Amplitude

Speed

Density

Radius

Frequency
```

---

## Settings

Describe

**engine behavior**

Examples

```
Fullscreen

VSync

Target FPS

Theme

Audio Device
```

Parameters belong to modules.

Settings belong to the application.

---

# Module Parameters

Each module should own its own parameters.

Conceptually

```
Wave Module

↓

frequency

↓

amplitude

↓

thickness
```

---

# Example

Wave Module

```python
class WaveModule:

    amplitude

    frequency

    speed
```

These values determine the generated geometry.

---

# Example

Particle Module

```python
count

velocity

drag

gravity

size
```

---

# Example

Grid Module

```python
spacing

major_every

line_width

opacity
```

---

# Parameter Types

The parameter system should support

```
Integer

Float

Boolean

Color

String

Enum

Vector

File

Path
```

---

# Integer Parameter

Example

```python
particle_count = 5000
```

---

# Float Parameter

Example

```python
speed = 0.25
```

---

# Boolean

Example

```python
show_labels = True
```

---

# Enum

Example

```python
mode =

LINES

POINTS

MESH
```

---

# Color

Example

```python
color =

theme.primary
```

or

```
RGB
```

---

# Parameter Metadata

Eventually parameters should contain

```
Name

↓

Description

↓

Default

↓

Minimum

↓

Maximum

↓

Step
```

This allows automatic UI generation.

---

# Example

Conceptually

```python
FloatParameter(

    "Amplitude",

    default=1.0,

    minimum=0.0,

    maximum=5.0,

    step=0.1
)
```

---

# Automatic UI

Future UI

```
Parameter

↓

Slider

↓

Module
```

No additional UI code required.

---

# Web UI

The exact same parameter

may become

```
Web Slider

↓

WebSocket

↓

Module
```

Again,

no module changes required.

---

# MIDI

Future

```
Knob

↓

Parameter

↓

Module
```

Allows hardware control.

---

# OSC

Future

```
OSC Message

↓

Parameter

↓

Visualization
```

Useful for live performances.

---

# Presets

Presets become simple collections of parameter values.

Example

```
Preset

↓

Amplitude = 2

↓

Density = 10000

↓

Theme = Cyberpunk
```

Loading a preset updates every module.

---

# Animation

Parameters themselves may eventually become animated.

Example

```
LFO

↓

Speed

↓

Wave Module
```

No module modifications required.

---

# Read Access

Modules simply read

```python
self.parameters.speed
```

or

```python
context.parameters.speed
```

depending on the final API.

---

# Write Access

Normally performed by

```
UI

↓

Preset

↓

OSC

↓

Automation
```

Modules generally shouldn't modify their own parameters continuously.

---

# Dirty State

Changing a parameter may automatically mark

```
Renderable Dirty
```

or

```
Module Dirty
```

allowing the renderer to rebuild only when necessary.

---

# Categories

Parameters may be grouped.

Example

```
Geometry

Appearance

Animation

Audio

Physics
```

Useful for UI organization.

---

# Example

Jarvis Globe

```
Geometry

↓

Radius

↓

Latitude Count

↓

Longitude Count

Animation

↓

Rotation Speed

↓

Pulse Speed

Appearance

↓

Glow

↓

Line Width

↓

Color

Audio

↓

Bass Gain

↓

Treble Gain
```

---

# Hidden Parameters

Future

Some parameters may exist for

```
Debug

Advanced Users

Experimental
```

and remain hidden by default.

---

# Serialization

Parameters should serialize automatically.

Example

```
JSON

↓

Preset

↓

Reload
```

Modules should not implement serialization manually.

---

# Default Values

Every parameter should define a sensible default.

This ensures

```
Create Module

↓

Immediately Works
```

---

# Validation

The parameter system should prevent invalid values.

Example

```
Particle Count

↓

-100

↓

Rejected
```

---

# Notifications

Future

Changing a parameter may emit

```
Parameter Changed

↓

Signal

↓

Module
```

instead of constant polling.

---

# Performance

Parameter access should be inexpensive.

Changing thousands of parameters every frame should not require rebuilding unrelated systems.

---

# Best Practices

✔ Expose configurable values.

✔ Avoid hardcoded constants.

✔ Choose sensible defaults.

✔ Group related parameters.

✔ Use semantic names.

---

# Anti-Patterns

Avoid

```python
speed = 1.732
```

inside algorithms.

Avoid

duplicating configuration files.

Avoid

manual UI creation for every module.

---

# Mental Model

Think of parameters as the knobs on a synthesizer.

The synthesizer already knows how to generate sound.

The knobs simply control it.

Retroscope modules should work the same way.

The module contains the algorithm.

Parameters control the algorithm.

---

# Future Vision

The parameter system is expected to become one of the most powerful parts of Retroscope.

Eventually the exact same parameter could be controlled simultaneously from

- Desktop UI
- Web UI
- OSC
- MIDI
- Presets
- Automation
- AI assistants
- Remote APIs

without changing the visualization module.

That level of flexibility is only possible because parameters are treated as first-class engine objects rather than ordinary Python variables.

---

# Summary

The Parameters API separates module configuration from module implementation.

Rather than hardcoding values inside algorithms, modules expose configurable parameters that can be edited by users, presets, hardware controllers, or automation systems.

This architecture keeps modules reusable, enables automatic user interfaces, and allows Retroscope to evolve into a highly interactive procedural visualization platform where every aspect of a visualization can be adjusted without modifying code.