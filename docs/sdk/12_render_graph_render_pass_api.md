# 12 - Render Graph & Render Pass API

Version: 1.0

---

# Introduction

One of the biggest architectural decisions in Retroscope is that the renderer **does not render directly**.

Instead, rendering is delegated to a **Render Graph**.

The Render Graph owns a collection of Render Passes.

Each pass performs one specific task.

Instead of this:

```
Renderer

↓

Draw Everything
```

Retroscope does this:

```
Renderer

↓

Render Graph

↓

Geometry Pass

↓

Future Passes

↓

Final Image
```

This may seem like unnecessary abstraction for today's renderer, but it is one of the most important design decisions in the engine because it allows the renderer to scale from a simple oscilloscope into a modern graphics pipeline without changing module code.

---

# Philosophy

A Render Pass should do **one thing only**.

Examples

```
Geometry

Bloom

CRT

Glow

Persistence

Overlay

UI
```

Each pass has exactly one responsibility.

---

# Why Not Render Everything Directly?

Imagine the renderer contained

```python
draw_geometry()

draw_glow()

draw_crt()

draw_ui()

draw_scanlines()

draw_noise()
```

Eventually this becomes

```
1000+
lines

↓

Massive Renderer
```

Every new visual effect modifies the renderer.

Instead,

Retroscope isolates every stage into its own object.

---

# Current Pipeline

Today's renderer is intentionally minimal.

```
Renderer

↓

GeometryPass
```

Only one pass exists.

That is enough to validate the architecture.

---

# Future Pipeline

The intended pipeline eventually looks like

```
Geometry Pass

↓

Glow Pass

↓

Persistence Pass

↓

Bloom Pass

↓

CRT Pass

↓

Overlay Pass

↓

UI Pass
```

Notice

Modules never change.

Only passes are added.

---

# Render Graph

Conceptually

```python
RenderGraph

↓

list[RenderPass]
```

The graph owns an ordered collection of passes.

---

# Construction

Today

```python
graph = RenderGraph()

graph.add(

    GeometryPass(...)
)
```

The renderer builds the graph once during initialization.

---

# Execution

Every frame

```python
graph.execute(packet)
```

The Render Graph simply executes each pass in order.

Conceptually

```python
for pass in passes:

    pass.execute(packet)
```

Nothing more.

---

# Render Packet

Every pass receives the same object.

```
RenderPacket
```

This packet contains everything needed for rendering.

Conceptually

```
Renderables

↓

Materials

↓

Meshes

↓

Transforms

↓

Future State
```

Every pass operates on this packet.

---

# Why A Packet?

Instead of

```python
pass.execute(

    frame,

    shader,

    renderer,

    camera,

    ...
)
```

everything is packaged into one object.

Benefits

- cleaner API
- future expansion
- simpler passes

---

# Render Pass

Every pass follows the same interface.

Conceptually

```python
class RenderPass:

    execute(packet)
```

Nothing else is required.

---

# Geometry Pass

Today's only pass.

Responsibilities

```
Iterate Renderables

↓

Upload Dirty Geometry

↓

Bind Shader

↓

Set Material

↓

Draw Mesh
```

Notice

It performs drawing only.

It does not generate geometry.

---

# Responsibilities

GeometryPass owns

```
Shader

Drawing

Material Upload
```

It does not own

```
Frame

Modules

Geometry Generation

Scene Logic
```

---

# Render Pass Independence

Every pass is completely independent.

Example

```
Bloom Pass
```

does not know

```
Grid

Wave

Radar

Particles
```

It only receives textures or framebuffers.

---

# Ordering

Pass order matters.

Example

Correct

```
Geometry

↓

Bloom

↓

CRT

↓

UI
```

Incorrect

```
UI

↓

Geometry
```

The Render Graph explicitly defines ordering.

---

# Adding A Pass

Adding a new rendering feature requires

1.

Create pass

```
BloomPass
```

2.

Add it

```python
graph.add(

    BloomPass()
)
```

No renderer changes.

No module changes.

---

# Example

Future Persistence Pass

```
Current Frame

↓

Blend

↓

Previous Frame

↓

Output
```

No visualization module needs to know this exists.

---

# Framebuffers

Future passes may render into

```
Framebuffer

↓

Texture

↓

Next Pass
```

Instead of directly drawing to the screen.

---

# Example Pipeline

```
Geometry

↓

Framebuffer A

↓

Glow

↓

Framebuffer B

↓

CRT

↓

Framebuffer C

↓

Screen
```

This architecture is already compatible with Retroscope.

---

# Post Processing

Everything after geometry becomes

another Render Pass.

Examples

```
Bloom

Noise

Scanlines

Vignette

Chromatic Aberration

Persistence

Tone Mapping
```

---

# Shader Ownership

Each pass owns the shaders it requires.

GeometryPass

↓

Geometry Shader

BloomPass

↓

Blur Shader

CRTPass

↓

CRT Shader

This keeps responsibilities isolated.

---

# Reusability

Because every pass shares the same interface,

they can easily be reused.

Example

```
Desktop

↓

GeometryPass

↓

BloomPass

↓

CRTPass

Raspberry Pi

↓

GeometryPass
```

Simply omit unsupported passes.

---

# Conditional Rendering

Future versions may enable or disable passes dynamically.

Example

```
Settings

↓

Enable Bloom

↓

Add BloomPass
```

or

```
Disable Bloom

↓

Skip BloomPass
```

No renderer modifications required.

---

# Profiling

Each pass can be profiled independently.

Future profiler output

```
Geometry

3.2 ms

Bloom

0.8 ms

CRT

1.5 ms

UI

0.3 ms
```

This makes optimization much easier.

---

# Data Ownership

Passes never own scene data.

Ownership remains

```
Modules

↓

Renderables

↓

Renderer
```

Passes simply consume the Render Packet.

---

# Communication

Render Passes should communicate only through

```
RenderPacket

Framebuffer

Textures
```

Never through global variables.

---

# Future Graph Features

The current graph is linear.

Future versions could support

```
Branching

Dependencies

Parallel Passes

Resource Lifetime

Automatic Scheduling
```

The public API would remain unchanged.

---

# What Modules Should Know

Modules do **not** interact with Render Graphs.

Modules should not

- add passes
- remove passes
- execute passes
- bind framebuffers

They simply create Renderables.

---

# Best Practices

✔ One responsibility per pass.

✔ Keep passes independent.

✔ Use RenderPacket as the input.

✔ Avoid module-specific logic.

✔ Think of passes as image processing stages.

---

# Anti-Patterns

Never

```python
if renderable is Wave:
```

inside a pass.

Never

```python
module.draw()
```

Never

```python
audio.update()
```

A Render Pass should only render.

---

# Mental Model

Imagine a modern video editing application.

Raw footage passes through a sequence of filters.

```
Raw Video

↓

Color Correction

↓

Bloom

↓

Sharpen

↓

Film Grain

↓

Output
```

Each filter is independent.

Retroscope's Render Graph works exactly the same way.

The Geometry Pass produces the initial image.

Every subsequent pass transforms that image until the final frame is presented to the display.

---

# Future Vision

As Retroscope evolves into a full procedural visualization engine, the Render Graph will become one of its defining features.

It will allow advanced visual effects—including CRT emulation, phosphor persistence, temporal feedback, glow, particle accumulation, volumetric effects, and post-processing—to be implemented as isolated Render Passes rather than as modifications to the renderer itself.

This keeps the renderer simple, keeps modules independent, and makes the graphics pipeline highly extensible.

---

# Summary

The Render Graph is the orchestration layer of Retroscope's rendering system.

Rather than rendering directly, the Renderer delegates work to an ordered collection of Render Passes. Each pass performs one well-defined task and consumes a shared Render Packet, allowing the graphics pipeline to remain modular, extensible, and platform-independent.

Today the Render Graph contains only a single Geometry Pass, but its architecture is already prepared for a complete modern rendering pipeline without requiring changes to visualization modules or the renderer itself.