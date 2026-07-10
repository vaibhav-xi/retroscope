# 19 - Input System API

Version: 1.0

---

# Introduction

The Input System provides Retroscope modules with access to user interaction while keeping them completely independent from the underlying operating system.

Modules should never know whether input comes from

- GLFW
- SDL
- Raspberry Pi GPIO
- Linux evdev
- macOS Cocoa
- Windows
- USB HID devices
- Touchscreens

Instead, modules interact with a stable engine API.

```
Hardware

↓

Platform Backend

↓

Input System

↓

Context

↓

Modules
```

The module never communicates with hardware directly.

---

# Philosophy

The Input System answers

> "What is the current state of user input?"

It should never answer

> "How should the visualization behave?"

Input provides information.

Modules decide how to respond.

---

# Design Goals

The Input System is designed to

- hide platform differences
- provide deterministic state
- support multiple input devices
- remain independent from visualization logic
- be easily expandable

---

# Current Repository

Current input directory

```
inputs/

├── audio.py

├── gpio.py

├── keyboard.py

├── mouse.py

└── touch.py
```

Each file is responsible for one physical input source.

---

# Ownership

Input belongs to the application.

```
App

↓

Input Manager

↓

Context

↓

Modules
```

Modules never create input devices.

---

# Lifetime

Typical lifetime

```
Application Starts

↓

Devices Open

↓

Poll Every Frame

↓

Application Exit

↓

Devices Closed
```

---

# Polling Model

Retroscope uses a polling model.

Each frame

```
Read Hardware

↓

Update Context

↓

Modules Read State
```

Modules always observe a consistent snapshot.

---

# Context Access

Eventually

```python
context.mouse

context.keyboard

context.touch

context.gpio
```

become the primary interfaces.

---

# Mouse

Future API

```python
context.mouse.position
```

Example

```
(x, y)
```

---

# Mouse Buttons

Future

```python
context.mouse.left

context.mouse.right

context.mouse.middle
```

Boolean values.

---

# Mouse Wheel

Future

```python
context.mouse.scroll
```

Useful for

- zoom
- scaling
- parameter adjustment

---

# Keyboard

Future API

```python
context.keyboard
```

Typical usage

```python
if context.keyboard.space:

    ...
```

---

# Key Queries

Conceptually

```python
context.keyboard.is_pressed("A")
```

or

```python
context.keyboard.keys
```

depending on the final implementation.

---

# Modifier Keys

Future

```
Shift

Ctrl

Alt

Command
```

Example

```python
context.keyboard.shift
```

---

# Text Input

Future

```python
context.keyboard.text
```

Useful for

- UI
- search
- console
- scripting

---

# Touch

Touch is a first-class input source.

Future

```python
context.touch.points
```

Each touch point contains

```
Position

Pressure

ID
```

---

# Multi-touch

Supported conceptually

```
Finger 1

Finger 2

Finger 3
```

Modules may create gestures.

---

# Gestures

Future engine

```
Pinch

Rotate

Swipe

Tap

Long Press
```

Modules receive high-level gestures rather than raw touch events.

---

# GPIO

One of Retroscope's distinguishing features is Raspberry Pi support.

Future

```python
context.gpio
```

Example

```python
if context.gpio[17]:

    ...
```

Possible uses

- buttons
- rotary encoders
- sensors
- custom hardware
- arcade controls

---

# Analog Inputs

Future

```
Joystick

Potentiometer

ADC

Pressure Sensors
```

GPIO may eventually expose normalized analog values.

---

# Audio Input

Although audio lives in its own subsystem,

it is conceptually another input device.

```
Microphone

↓

Audio Service

↓

Context.audio
```

---

# Future Devices

Possible future input sources

```
Gamepad

Joystick

MIDI

OSC

Leap Motion

Camera

Depth Sensor

VR Controllers
```

The architecture already supports adding them.

---

# Device Independence

Modules should never ask

```
Is this macOS?

Is this Raspberry Pi?

Is this GLFW?
```

Instead,

they read Context.

---

# Events vs Polling

Current philosophy favors polling.

Example

```python
if context.mouse.left:

    ...
```

rather than callback-heavy APIs.

Signals remain available for higher-level events.

---

# Frame Consistency

Input is updated once per frame.

Every module observes identical state.

No module can observe

```
Old Mouse

↓

New Mouse
```

during the same frame.

---

# Coordinate System

Mouse and touch coordinates follow the engine's coordinate conventions.

Future camera systems may provide automatic coordinate conversion.

---

# Input Mapping

Future abstraction

```
Action

↓

Space

↓

Gamepad A

↓

GPIO Button
```

Modules respond to actions,

not physical buttons.

---

# Example

Instead of

```python
if key == GLFW_KEY_SPACE:
```

future modules might do

```python
if context.input.action("Pause"):
```

making controls configurable.

---

# Recording

Future Recorder Service may capture

```
Input

↓

Replay
```

allowing deterministic demonstrations.

---

# Network Input

Future

```
Remote Device

↓

Network

↓

Input System

↓

Modules
```

No module changes required.

---

# Threading

Hardware polling may occur on background threads.

Modules always receive synchronized snapshots through Context.

---

# Best Practices

✔ Read input through Context.

✔ Avoid platform-specific APIs.

✔ Treat input as read-only.

✔ Keep interaction logic inside modules.

---

# Anti-Patterns

Never

```python
import glfw
```

Never

```python
pygame.key.get_pressed()
```

Never

```python
GPIO.input(...)
```

inside visualization modules.

Platform code belongs to the Input System.

---

# Mental Model

Imagine an aircraft cockpit.

The pilot doesn't connect directly to every sensor.

Instead,

the cockpit instruments display the current state.

The pilot reacts.

Context.input is the cockpit.

The operating system, drivers, and hardware remain hidden.

---

# Future Vision

Retroscope is designed to become much more than an oscilloscope.

Future installations may include

- touch tables
- museum exhibits
- MIDI synthesizers
- Raspberry Pi hardware
- motion sensors
- custom controllers
- network-controlled installations

The Input System provides a stable abstraction layer that allows all of these devices to drive the exact same visualization modules without modification.

---

# Summary

The Input System abstracts all user and hardware interaction behind a unified engine interface.

Rather than exposing platform-specific APIs, it provides synchronized input state through Context, allowing modules to remain portable, deterministic, and independent of operating system details.

By treating keyboards, mice, touchscreens, GPIO, audio, and future devices as interchangeable input sources, Retroscope creates a flexible foundation for everything from desktop visualizers to embedded interactive installations.