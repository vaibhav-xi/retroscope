# docs/reference/parameter_reference.md

# Parameter Reference

Version: 1.0

---

# Introduction

Parameters are the primary mechanism through which a Retroscope module exposes configurable behavior.

Unlike ordinary Python variables, Parameters are intended to become part of the engine's public interface.

A parameter may eventually be controlled from

- Desktop UI
- Web UI
- Presets
- OSC
- MIDI
- Automation
- Scripting
- Plugins

without requiring any changes to the visualization itself.

This makes parameters one of the most important abstractions in the engine.

---

# Philosophy

A module should never hide important constants inside its implementation.

Instead of

```python
speed = 2.5
```

the module should expose

```python
speed
```

as a configurable parameter.

The algorithm remains identical.

Only the source of the value changes.

---

# Parameters vs Variables

A variable exists only inside the module.

Example

```python
phase += dt
```

The user never edits this value.

A parameter, however, represents a user-adjustable property.

Example

```
Particle Count

↓

Editable

↓

Changes Visualization
```

---

# Current State

Today,

Retroscope already contains

```
core/

parameters.py
```

The current implementation is intentionally lightweight.

The architecture, however, is designed for a much richer parameter system.

---

# Design Goals

Parameters should eventually support

✔ automatic UI generation

✔ serialization

✔ validation

✔ animation

✔ presets

✔ networking

✔ scripting

✔ documentation

without module-specific code.

---

# Ownership

Parameters belong to Modules.

```
Module

↓

Parameters
```

The engine reads and writes them.

Modules consume them.

---

# Lifetime

Parameters live for the lifetime of the module.

```
Create Module

↓

Create Parameters

↓

Runtime

↓

Destroy Module
```

---

# Categories

Parameters should be grouped logically.

Example

```
Appearance

↓

Animation

↓

Audio

↓

Simulation

↓

Physics
```

This organization naturally maps to future user interfaces.

---

# Parameter Types

The engine is designed to support multiple parameter types.

Examples

```
Integer

Float

Boolean

Color

Enum

String

Path

Vector

List
```

---

# Integer

Example

```python
particle_count =

5000
```

---

# Float

Example

```python
speed =

1.25
```

---

# Boolean

Example

```python
show_grid =

True
```

---

# Enum

Example

```python
mode =

LINES
```

Possible values

```
Lines

Points

Filled
```

---

# Color

Example

```python
accent_color
```

Eventually integrates with the Theme system.

---

# Vector

Future

```python
gravity =

(0,-9.81)
```

Useful for physics modules.

---

# Parameter Metadata

Every parameter should eventually expose metadata.

```
Name

Description

Default

Minimum

Maximum

Step

Units

Category
```

This allows automatic documentation and editor generation.

---

# Example

Conceptually

```python
FloatParameter(

    name="Amplitude",

    default=1.0,

    minimum=0.0,

    maximum=5.0,

    step=0.1
)
```

---

# Units

Future parameters should specify units where appropriate.

Examples

```
Pixels

Seconds

Degrees

Radians

Hz

dB
```

This makes interfaces much clearer.

---

# Default Values

Every parameter should define a sensible default.

A module should always be usable immediately after creation.

---

# Validation

Invalid values should be rejected.

Example

```
Opacity

↓

-3

↓

Rejected
```

Validation belongs to the parameter system,

not the module.

---

# Animation

Future parameter animation

```
LFO

↓

Amplitude

↓

Wave Module
```

The module simply reads the current value.

---

# Automation

Parameters should eventually support automation curves.

Example

```
Time

↓

Interpolation

↓

Parameter

↓

Visualization
```

---

# UI Integration

Future desktop UI

```
Parameter

↓

Slider

↓

Value

↓

Module
```

No custom UI code required.

---

# Web Integration

Exactly the same parameter should appear inside

```
Browser

↓

WebSocket

↓

Engine
```

without modifying the module.

---

# MIDI Integration

Example

```
Knob

↓

Brightness

↓

Glow
```

Hardware controllers simply modify parameters.

---

# OSC Integration

Example

```
OSC

↓

Radius

↓

Visualization
```

Again,

no module modifications.

---

# Presets

Presets become collections of parameter values.

```
Preset

↓

Parameters

↓

Visualization
```

Loading a preset updates the entire module.

---

# Serialization

Future

```json
{
    "radius": 0.5,
    "speed": 1.2,
    "glow": true
}
```

No module-specific serialization should be required.

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

allowing efficient updates.

---

# Read Access

Modules should simply read

```python
self.parameters.radius
```

or

```python
context.parameters.radius
```

depending on the final API.

---

# Write Access

Typically performed by

- UI
- Automation
- Presets
- Network
- MIDI
- Scripts

Modules themselves rarely modify parameter values.

---

# Documentation

Parameter descriptions should explain

- purpose
- units
- expected range
- visual effect

Future documentation can be generated automatically.

---

# Best Practices

✔ Expose meaningful controls.

✔ Use descriptive names.

✔ Provide sensible defaults.

✔ Group related parameters.

✔ Validate input.

✔ Document behavior.

---

# Anti-Patterns

Avoid

```python
speed = 3.14159265
```

inside algorithms.

Avoid

duplicating configuration systems.

Avoid

manually building parameter editors.

---

# Future Parameter API

Long-term vision

```python
FloatParameter(

    name="Rotation Speed",

    description="Angular velocity of the globe.",

    default=0.5,

    minimum=0,

    maximum=5,

    units="rad/s",

    category="Animation"
)
```

A single declaration becomes

- documentation
- UI
- preset support
- automation
- networking
- scripting

automatically.

---

# Mental Model

Think of a modular synthesizer.

Each module contains oscillators, filters, and envelopes.

The knobs are the parameters.

Changing a knob changes behavior,

not the underlying circuitry.

Retroscope modules should work exactly the same way.

---

# Summary

The Parameter system is the primary interface between a Retroscope module and the outside world.

Rather than hiding configuration inside source code, modules expose meaningful, documented parameters that can be controlled by users, presets, automation systems, MIDI devices, web interfaces, or future scripting APIs.

By treating parameters as first-class engine objects rather than ordinary variables, Retroscope enables highly interactive visualizations while keeping module implementations clean, reusable, and independent of user interface concerns.