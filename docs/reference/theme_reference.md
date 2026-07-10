# docs/reference/theme_reference.md

# Theme Reference

Version: 1.0

---

# Introduction

Themes define the visual identity of Retroscope.

A Theme is responsible only for appearance.

It does **not** define

- geometry
- animation
- rendering
- simulation
- audio processing

Instead, it provides a consistent visual language that every visualization module can share.

```
Theme

↓

Material

↓

Renderer

↓

Display
```

Modules should request semantic colors rather than hardcoded RGB values.

This allows the entire engine to change appearance instantly.

---

# Philosophy

A visualization should never assume

```
Green
```

Instead it should ask

```
Primary Color
```

The theme decides what "Primary" means.

This keeps modules reusable across completely different visual styles.

---

# Current Themes

The repository currently contains

```
themes/

amber.py

blue.py

cyberpunk.py

oscilloscope.py
```

Each file defines a complete visual identity.

---

# Theme Responsibilities

A Theme should define

- colors
- visual identity
- stylistic intent

A Theme should **not** define

- geometry
- rendering algorithms
- simulation parameters
- module behavior

---

# Semantic Colors

Rather than exposing arbitrary RGB values,

Themes expose semantic colors.

Example

```
Primary

Secondary

Accent

Grid

Background

Highlight

Warning

Selection

Disabled
```

These names describe intent rather than appearance.

---

# Primary

The primary color is the default drawing color used by most visualizations.

Example

```
Oscilloscope

↓

Green

Amber

↓

Orange

Cyberpunk

↓

Cyan
```

The module remains unchanged.

---

# Secondary

Used for

- supporting geometry
- less important objects
- helper visuals

---

# Accent

Used sparingly to attract attention.

Examples

- peaks
- selections
- active targets
- beat indicators

---

# Grid

Dedicated color for

- graph paper
- oscilloscope grid
- reference lines

Allows grid intensity to be controlled independently.

---

# Background

Defines the clear color.

Example

```
Black

Dark Blue

Dark Purple
```

The renderer reads this value when clearing the framebuffer.

---

# Highlight

Used for

- hover
- focus
- active objects

---

# Warning

Reserved for

- clipping
- overload
- errors
- alerts

Usually

```
Orange

Yellow

Red
```

depending on theme.

---

# Success (Future)

Useful for

```
Connected

Locked

Recording
```

---

# Error (Future)

Useful for

```
Disconnected

Failed

Missing
```

---

# Disabled (Future)

Used for

```
Inactive

Unavailable

Muted
```

---

# Typography Colors

Future UI themes may include

```
Text

Secondary Text

Caption

Placeholder
```

---

# Transparency

Themes may eventually define

```
Overlay Alpha

Grid Alpha

Glow Alpha
```

allowing subtle visual tuning.

---

# Glow

Future themes may specify

```
Glow Color

Glow Strength
```

particularly useful for

- holograms
- CRT
- neon interfaces

---

# CRT Themes

Future CRT pipeline may use

```
Phosphor

Persistence

Bloom

Noise

Scanlines
```

derived from the active theme.

---

# Holographic Themes

Future

```
Blue Hologram

Green Hologram

Red Alert

Medical

Military
```

Modules remain identical.

---

# Scientific Themes

Potential themes

```
Hospital Monitor

Laboratory

Radar

Engineering
```

Again,

only colors change.

---

# Theme Switching

Changing themes should be instantaneous.

```
Theme Changed

↓

Materials Updated

↓

Next Frame
```

No geometry rebuild required.

---

# Module Usage

Preferred

```python
renderable.material.color =

context.theme.primary
```

Avoid

```python
(0,1,0)
```

Hardcoded colors reduce portability.

---

# Audio Visualizations

Audio modules should also use semantic colors.

Example

```
Wave

↓

Primary

Peaks

↓

Accent

Grid

↓

Grid Color
```

The visualization adapts automatically.

---

# Parameter Interaction

Users may override theme colors using parameters.

The theme still provides defaults.

---

# Presets

Presets may include

```
Theme

↓

Cyberpunk
```

Loading the preset immediately changes the appearance of every visualization.

---

# Future Theme Structure

Conceptually

```python
Theme(

    background,

    primary,

    secondary,

    accent,

    grid,

    warning,

    highlight,

    disabled
)
```

This structure should remain stable.

---

# Theme Inheritance (Future)

Possible hierarchy

```
Base Theme

↓

Oscilloscope Theme

↓

Amber Theme
```

Reducing duplicated definitions.

---

# Custom Themes

Users should eventually be able to define

```
themes/

my_theme.py
```

or

```
JSON
```

without modifying engine code.

---

# Dynamic Themes

Future

Themes may animate.

Example

```
Beat

↓

Accent Pulses

↓

Glow Changes
```

The engine remains unaware.

---

# Accessibility

Future themes may support

- high contrast
- color blindness
- low brightness
- presentation mode

without changing visualization modules.

---

# Relationship With Materials

Themes provide

```
Default Colors
```

Materials consume those colors.

A Material may override them if necessary.

---

# Relationship With Renderer

The renderer should never hardcode colors.

It reads Material values,

which usually originate from the active Theme.

---

# Best Practices

✔ Use semantic colors.

✔ Avoid RGB literals.

✔ Keep themes cohesive.

✔ Separate appearance from behavior.

✔ Allow themes to evolve independently.

---

# Anti-Patterns

Avoid

```python
(0,1,0)
```

inside modules.

Avoid

duplicating colors across modules.

Avoid

putting geometry inside theme definitions.

---

# Mental Model

Imagine changing the skin of an operating system.

Applications continue working exactly the same way.

Only their appearance changes.

Retroscope themes provide the same capability for procedural visualizations.

---

# Future Vision

As Retroscope grows,

themes may eventually control

- color palettes
- glow
- bloom
- CRT effects
- fonts
- UI styling
- transition animations

without changing visualization code.

This makes themes a powerful mechanism for transforming the visual identity of the engine while preserving the underlying algorithms.

---

# Summary

The Theme system defines the visual language of Retroscope.

By exposing semantic colors instead of hardcoded RGB values, themes allow visualization modules to remain completely independent of appearance. A single module can therefore be rendered as a classic green oscilloscope, an amber CRT display, a cyberpunk hologram, or a scientific instrument simply by selecting a different theme.

This separation between appearance and behavior is a key architectural principle that enables consistency, customization, and long-term maintainability throughout the engine.