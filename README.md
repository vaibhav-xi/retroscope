# RetroScope

**A real-time audio-reactive oscilloscope renderer — built as a custom GPU engine, not a script.**

RetroScope turns live audio into the kind of glowing, phosphor-green waveform you'd expect to see on a CRT test bench, rendered at 60 FPS on hardware as modest as a Raspberry Pi. It's built the way you'd build an actual game engine: a modular simulation layer, a custom OpenGL rendering pipeline, a hand-written render graph, and a native C extension sitting under the hot path — not a Python script drawing a sine wave on a canvas.

If you came here expecting a weekend FFT-bars project, this isn't that. It's over-engineered on purpose.

---

## Why this isn't "just a visualizer"

A few things RetroScope does that most audio visualizers don't bother with:

- **A real module architecture, not a monolith.** Every visual effect is a self-contained `Module` (`initialize` → `update` → `emit` → `shutdown`), owned by a central `Manager`. Simulation never touches rendering directly — modules emit render primitives into layered frames (`BACKGROUND`, `MAIN`, `OVERLAY`, `UI`), and the renderer decides what to do with them. Add a new visual mode without touching the engine.
- **A custom OpenGL ES 2.0 pipeline.** Its own `RenderGraph`, its own `GeometryPass`, hand-written GLSL shaders — not a wrapper around someone else's renderer.
- **A native C extension in the hot path.** Stroke geometry (the actual line/vertex construction for every trace on screen) is built by a compiled CPython extension for real-time performance, with an automatic pure-Python fallback if the native build isn't available. Prototype in Python, ship in C, without losing the ability to run anywhere.
- **Real DSP, not a bar graph.** The audio analyzer does spectrum resolution, per-band waveform separation, pitch tracking, and harmony analysis — not just an FFT magnitude plot.
- **CRT phosphor decay, simulated correctly.** Instead of clearing the framebuffer every frame, RetroScope can fade it toward black instead — the actual optical behavior of a real oscilloscope's phosphor coating, not a flat digital "trail" effect.
- **Thirteen visualization modes, one engine.** The default oscilloscope/Lissajous mode is the headline, but it's one of thirteen interchangeable render modes built on the same module system — the others are built and simply switched off by default.
- **Tunable live, from a browser.** A built-in web interface lets you adjust hue, glow, and other visual parameters while it's running, with settings persisted to disk — no restart required.
- **Audio capture built from source, not assumed.** PortAudio is compiled locally against ALSA and PulseAudio for reliable low-latency capture on Linux/Raspberry Pi, rather than relying on whatever the OS happens to expose.

---

## Features

- Real-time audio-reactive oscilloscope (X-Y / Lissajous) rendering
- Custom OpenGL ES 2.0 renderer with a dedicated render graph
- Native C acceleration for geometry/stroke building, with Python fallback
- Beat, kick, and snare-reactive visual triggers
- Spectrum, per-band waveform, pitch, and harmony analysis
- Thirteen built-in visualization modes (oscilloscope active by default)
- CRT-accurate phosphor afterglow / decay simulation
- Authentic green-phosphor CRT color theme, fully swappable via a theme system
- Live browser-based control panel for real-time parameter tuning
- Cross-platform audio input (Linux/Raspberry Pi via PulseAudio monitor sink, Windows via WASAPI loopback, macOS/other via default input device)
- Config-driven — all runtime-immutable settings live in a single `config.py`

---

## Architecture

```
main.py            → application entry point (kept intentionally tiny)
core/               → engine core: App, Manager, Module, Context, Frame
render/             → renderer-agnostic primitives (Polyline, Renderable, color utils)
render_es2/         → OpenGL ES 2.0 renderer: shaders, render graph, geometry/stroke builders,
                      native C extension (_stroke_builder.c) with Python fallback
modules/            → visual modules (grid, overlay, wave, blackhole, 13 audio-reactive modes)
inputs/             → audio capture + music analysis (spectrum, bands, pitch, harmony)
themes/             → visual theming (color-only, no logic — e.g. the default CRT green theme)
presets/            → saved parameter presets
web/                → Flask-based live control interface
services/           → supporting background services
config.py           → global, immutable configuration
```

The engine loop is straightforward and deliberately boring where it should be: **Poll → Update → Emit → Draw → Swap**, profiled every frame, reported once a second.

---

## Requirements

- Python 3.10+
- A GPU/driver stack that supports OpenGL ES 2.0 (this includes Raspberry Pi's GPU)
- System audio input (microphone, line-in, or a loopback/monitor source)

Python dependencies:

```
Flask>=3.1,<4
moderngl>=5.12,<6
glfw>=2.10,<3
numpy>=2.0,<3
pygame>=2.6,<3
PyOpenGL>=3.1,<4
PyOpenGL-accelerate>=3.1,<4
sounddevice>=0.5,<1
PyAudioWPatch>=0.2.12,<1  # Windows only
```

Install with:

```bash
pip install -r requirements.txt
```

---

## Building the native performance layer

RetroScope will run without it (falling back to a pure-Python stroke builder), but for real-time performance on constrained hardware like a Raspberry Pi, build the native extension:

```bash
python setup.py build_ext --inplace
```

On Linux, you'll also want PortAudio built against ALSA and PulseAudio for reliable low-latency capture:

```bash
./build_portaudio.sh
```

---

## Running it

```bash
python main.py
```

`ESC` closes the window. FPS and frame-timing stats print to the console once per second.

### Live tuning

With the app running, open the web control interface at:

```
http://localhost:5000
```

(port configurable via `WEB_PORT` in `config.py`)

Parameter changes made here are saved to disk and picked back up automatically.

---

## Configuration

All runtime-immutable settings live in `config.py` — resolution, target FPS, fullscreen toggle, default theme, audio device/sample rate/block size, and the web control port. Anything that changes *while the engine is running* lives in `Context`, not here.

---

## Visualization modes

The engine currently ships with thirteen `AudioReactiveMode` modules plus a handful of utility modules (grid, overlay, wave, blackhole). Only the default oscilloscope mode (`AudioReactiveMode7`) is registered and active out of the box — the rest are fully built and can be enabled in `core/app.py`.

---

## Author

Built and maintained by [vaibhav-xi](https://github.com/vaibhav-xi).