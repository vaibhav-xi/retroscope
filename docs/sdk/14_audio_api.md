# 14 - Audio API

Version: 1.0

---

# Introduction

Audio is one of the primary inputs to Retroscope.

Although Retroscope can render purely procedural animations, its long-term purpose is to create visualizations that react to sound in real time.

Unlike traditional music visualizers, the engine treats audio as just another data source.

A visualization module does not know

- where the audio comes from,
- which microphone is connected,
- whether the signal comes from a USB microphone,
- ALSA,
- PulseAudio,
- JACK,
- a WAV file,
- or network streaming.

Instead, modules consume a simple Audio interface.

---

# Philosophy

The audio subsystem follows the same philosophy as the renderer.

Modules should never contain

- PyAudio code
- sounddevice code
- ALSA calls
- platform-specific microphone handling
- buffering logic

Instead they receive processed audio values.

```
Microphone

↓

Audio Engine

↓

Analysis

↓

Context.audio

↓

Visualization Module
```

---

# Design Goals

The Audio API is designed to

- hide hardware differences
- expose useful signal information
- minimize latency
- remain deterministic
- be independent of visualization modules

---

# Audio Ownership

Audio belongs to the engine.

```
Application

↓

Audio Engine

↓

Context.audio

↓

Modules
```

Modules never own audio devices.

---

# Lifetime

Typical lifetime

```
Application Start

↓

Microphone Opens

↓

Continuous Capture

↓

Application Exit

↓

Microphone Closes
```

Modules should never start or stop microphones.

---

# Current State

Today,

Retroscope contains

```
inputs/audio.py
```

along with standalone microphone tests used during development.

The engine is transitioning toward a permanent Audio service.

---

# Audio Flow

Conceptually

```
USB Microphone

↓

PCM Samples

↓

Signal Processing

↓

Context.audio

↓

Modules
```

---

# Raw Samples

Future API

```python
context.audio.samples
```

Type

```python
numpy.ndarray
```

Contains the latest block of captured samples.

Example

```
1024 samples

or

2048 samples
```

depending on configuration.

---

# RMS Level

One of the most useful measurements.

Future

```python
context.audio.rms
```

Range

```
0.0

↓

1.0
```

Useful for

- glow
- brightness
- pulse
- camera shake

---

# Peak Level

Future

```python
context.audio.peak
```

Represents the loudest sample within the current block.

Useful for

- transient detection
- beat visualization
- clipping indicators

---

# Decibel Level

Future

```python
context.audio.db
```

Example

```
-60 dB

↓

Silence

-20 dB

↓

Conversation

0 dB

↓

Maximum
```

Useful for VU meters.

---

# FFT

Perhaps the most important future feature.

```python
context.audio.fft
```

Returns

```
Frequency Spectrum
```

Example

```
20 Hz

↓

20 kHz
```

Modules can generate

- equalizers
- holograms
- frequency rings
- particle systems

---

# Frequency Bands

Instead of computing FFT manually,

future convenience values

```python
context.audio.bass

context.audio.mid

context.audio.treble
```

Range

```
0.0

↓

1.0
```

---

# Beat Detection

Future

```python
context.audio.beat
```

Boolean

```
True

↓

Beat Detected
```

Modules no longer need custom beat algorithms.

---

# BPM

Future

```python
context.audio.bpm
```

Estimated tempo.

Useful for synchronized procedural animation.

---

# Envelope

Future

```python
context.audio.envelope
```

Represents the smoothed amplitude over time.

Ideal for fluid animations.

---

# Spectrogram

Future

```python
context.audio.spectrogram
```

Contains recent FFT history.

Useful for

- waterfalls
- scrolling frequency displays
- temporal analysis

---

# Latency

The engine aims to keep audio latency low enough for real-time interaction.

Target

```
<20 ms
```

Visualization should feel directly connected to sound.

---

# Sampling Rate

Future

```python
context.audio.sample_rate
```

Example

```
44100

48000

96000
```

Modules rarely need this value directly.

---

# Channels

Future

```python
context.audio.channels
```

Example

```
Mono

Stereo
```

Most visualizations operate on a mixed mono signal.

---

# Audio Source

The engine should eventually support multiple sources.

Examples

```
USB Microphone

↓

System Audio

↓

Audio File

↓

Network Stream
```

Modules remain unchanged.

---

# Device Enumeration

Device management belongs to the engine.

Modules should never enumerate microphones.

---

# Audio Analysis

Signal processing belongs to the Audio service.

Examples

```
FFT

↓

Filtering

↓

Normalization

↓

Beat Detection

↓

Envelope Following
```

Modules consume results rather than performing duplicate analysis.

---

# Example

Simple brightness pulse

```python
level = context.audio.rms

renderable.material.color = (

    level,

    1.0,

    level

)
```

---

# Example

Scale animation

```python
scale =

1.0 +

context.audio.bass
```

---

# Example

Particle emission

```python
if context.audio.beat:

    emit_particles()
```

---

# Example

Frequency ring

```python
energy =

context.audio.fft[120]
```

---

# Audio Independence

Modules should never know

- microphone type
- operating system
- audio backend
- buffer size

These details belong entirely to the engine.

---

# Future Audio Features

Planned analysis includes

- FFT
- Mel spectrum
- chromagram
- onset detection
- BPM estimation
- beat tracking
- envelope followers
- spectral centroid
- spectral rolloff
- zero-crossing rate

Most visualization modules will only need a small subset.

---

# Multiple Consumers

Many modules may simultaneously consume the same audio.

Example

```
Waveform

↓

Particle System

↓

Spectrum Analyzer

↓

Holographic Globe

↓

Snowfall
```

The engine computes analysis once.

Modules reuse it.

---

# Threading

Audio capture may occur on a background thread.

Modules should treat all Context audio values as read-only snapshots.

---

# Performance

Heavy DSP should occur only once per frame.

Modules should never compute identical FFTs independently.

---

# Best Practices

✔ Read audio through Context.

✔ Use RMS for simple amplitude.

✔ Use FFT for frequency-driven effects.

✔ Keep visualization separate from signal processing.

✔ Assume normalized values whenever possible.

---

# Anti-Patterns

Never

```python
import sounddevice
```

Never

```python
import pyaudio
```

Never

```python
stream.read(...)
```

Never

```python
compute_fft(...)
```

inside every module.

Signal processing belongs to the Audio subsystem.

---

# Mental Model

Imagine the Audio subsystem as a laboratory.

Raw sound enters the lab.

Scientists measure

- amplitude
- frequency
- beats
- transients
- energy

Modules don't receive the raw experiment.

They receive the finished measurements.

This keeps visualization code extremely simple.

---

# Future Vision

Audio is expected to become one of the defining features of Retroscope.

Future visualizations may include

- Jarvis holographic globes
- reactive particle storms
- volumetric frequency fields
- procedural snow
- flowing sand
- liquid simulations
- radar sweeps
- phosphor persistence
- oscilloscope traces

All of them will consume the same Audio API.

---

# Summary

The Audio API provides Retroscope modules with a stable, high-level interface to real-time sound analysis.

Rather than exposing microphones or platform-specific APIs, the engine supplies normalized signal measurements such as RMS, FFT, frequency bands, beats, and future DSP analyses through `context.audio`.

This separation allows visualization modules to remain portable, efficient, and focused entirely on creating compelling graphics rather than processing audio streams.