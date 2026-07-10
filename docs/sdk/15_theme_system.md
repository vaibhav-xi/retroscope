# 15 - Theme System

Version: 1.0

---

# Introduction

The Theme System defines the visual identity of Retroscope.

Modules should describe **what** they want to render, not **how** it should be colored.

The purpose of the Theme system is to completely separate visualization logic from appearance.

Instead of this

```python
color = (0.0, 1.0, 0.4)
```

modules should eventually do

```python
color = context.theme.primary
```

Changing the active theme immediately changes the appearance of the entire application without modifying a single visualization module.

---

# Philosophy

Themes should answer questions like

- What color should grid lines be?
- What color should the waveform be?
- What should the background look like?
- Should glow be enabled?
- How bright should highlights be?

They should **never** contain

- rendering code
- geometry
- simulation
- modules
- OpenGL objects

A Theme is purely a collection of visual parameters.

---

# Ownership

The Theme belongs to the application.

```
App

↓

Theme

↓

Context

↓

Modules
```

Modules read from the theme.

They never own it.

---

# Current Themes

Current repository

```
themes/

├── amber.py

├── blue.py

├── cyberpunk.py

└── oscilloscope.py
```

Each file represents one complete visual style.

---

# Theme Lifetime

```
Application Starts

↓

Theme Loaded

↓

Used Every Frame

↓

Theme Changed (optional)

↓

Application Exit
```

Themes are long-lived.

---

# Current Usage

Today,

many modules still assign colors directly.

Example

```python
Material(

    color=(0.0, 1.0, 0.4)

)
```

The long-term goal is to replace these literals with theme values.

---

# Theme Responsibilities

A Theme defines

- colors
- brightness
- accents
- UI palette
- optional rendering hints

Nothing more.

---

# Typical Structure

Conceptually

```python
class Theme:

    primary

    secondary

    accent

    background

    grid

    waveform

    warning

    success
```

Future themes may expose many more properties.

---

# Primary Color

The most commonly used color.

Example

```python
theme.primary
```

Typical usage

```
Waveform

↓

Primary Color
```

---

# Secondary Color

Used for supporting geometry.

Example

```
Minor Grid

↓

Secondary
```

---

# Accent Color

Used for emphasis.

Examples

```
Selection

Cursor

Highlight

Marker
```

---

# Background

Defines

```
Clear Color
```

Future renderer

```python
glClearColor(

    *theme.background

)
```

Modules should never set clear colors directly.

---

# Grid Color

Future

```python
theme.grid
```

Allows grid modules to remain completely style-independent.

---

# Waveform Color

Future

```python
theme.waveform
```

Different themes can completely change oscilloscope appearance.

---

# Warning Color

Useful for

```
Clipping

Errors

Alerts
```

---

# Success Color

Useful for

```
Confirmation

Healthy Signal

Status
```

---

# Example Theme

Oscilloscope

Conceptually

```python
primary

↓

Green

background

↓

Black

grid

↓

Dark Green
```

Produces the classic CRT oscilloscope appearance.

---

# Cyberpunk Theme

Conceptually

```python
primary

↓

Magenta

accent

↓

Cyan

background

↓

Dark Purple
```

The same modules now produce an entirely different aesthetic.

---

# Amber Theme

Inspired by vintage monochrome CRT terminals.

```
Amber

↓

Dark Brown Background

↓

Warm Glow
```

---

# Blue Theme

Inspired by laboratory oscilloscopes.

```
Blue

↓

Black Background

↓

Blue Grid
```

---

# Theme Switching

Future application

```
User

↓

Select Theme

↓

Context.theme

↓

Entire Scene Updates
```

Modules require no modification.

---

# Why Themes?

Without themes,

every module eventually contains

```python
(0,1,0)

(0,0.7,0)

(0.2,1,0.3)
```

Changing appearance becomes impossible.

Themes eliminate duplicated color definitions.

---

# Theme Independence

A module should never ask

```
Am I using Cyberpunk?

Am I using Amber?
```

Instead,

it simply requests

```
theme.primary
```

The Theme decides the actual color.

---

# Future Theme Parameters

Beyond colors,

themes may eventually define

```
Glow Strength

↓

Bloom Amount

↓

Grid Opacity

↓

Persistence

↓

Noise Strength

↓

Scanline Strength
```

This allows themes to affect rendering characteristics.

---

# CRT Appearance

Future CRT pipeline

```
Theme

↓

Persistence

↓

Bloom

↓

Glow

↓

Noise
```

Different themes produce different CRT personalities.

---

# Font Styling

Future

```python
theme.font
```

Allows UI modules to remain independent from typography.

---

# Particle Colors

Future

```python
theme.particles
```

or

```python
theme.palette
```

Allowing procedural modules to select harmonious colors.

---

# Gradients

Future themes may expose

```python
theme.gradient
```

instead of single colors.

Useful for

- holograms
- spectrums
- particles
- frequency displays

---

# Random Palette

Future

```python
theme.random_color()
```

Allows procedural modules to remain stylistically consistent.

---

# Accessibility

Future themes could support

- high contrast
- color blindness
- monochrome
- low-light modes

without modifying visualization modules.

---

# Theme Reloading

Future development mode

```
Edit Theme File

↓

Reload

↓

Immediate Visual Update
```

No application restart required.

---

# Best Practices

✔ Obtain colors from the Theme.

✔ Avoid hardcoded RGB values.

✔ Keep modules theme-independent.

✔ Use semantic names rather than literal colors.

Good

```python
theme.primary
```

Bad

```python
(0.0,1.0,0.4)
```

---

# Anti-Patterns

Avoid

```python
if cyberpunk:
```

Avoid

```python
if amber:
```

Avoid

```python
color=(0,1,0)
```

Visualization logic should never depend on a specific theme.

---

# Mental Model

Imagine writing a book.

The content is the visualization module.

The font, paper, and cover design are the Theme.

Changing the book cover doesn't change the story.

Likewise,

changing the Theme should never change visualization logic.

---

# Future Vision

The Theme System is expected to become one of Retroscope's defining features.

Imagine switching between

```
Vintage Oscilloscope

↓

Military Radar

↓

Jarvis Hologram

↓

Cyberpunk

↓

Medical Monitor

↓

Retro Terminal

↓

Synthwave
```

using exactly the same visualization modules.

Only the Theme changes.

---

# Summary

The Theme System separates visual identity from visualization logic.

Modules describe geometry and behavior while Themes define colors, palettes, glow characteristics, and eventually rendering style. This separation allows the entire appearance of Retroscope to change instantly without modifying modules, making themes a first-class part of the engine's architecture.

For module authors, the rule is simple:

> Never hardcode appearance when a semantic theme value exists.

This keeps visualizations reusable, consistent, and future-proof as Retroscope evolves into a complete procedural visualization platform.