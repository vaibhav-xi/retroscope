
from __future__ import annotations

import math
import platform

import numpy as np

import config

from core.module import Module
from core.frame import Layer

from render.primitives import Polyline
from render.renderable import Renderable
from render_es2.material import Material

from inputs.music_analysis import MusicAnalyzer

from . import theory
from . import lattice
from . import fractal
from .bassline import BasslineSpiral
from .constellation import MelodyConstellation
from .tension_field import TensionField

_IS_DESKTOP = platform.system() == "Darwin"

_SPECTRUM_RESOLUTION = 64 if _IS_DESKTOP else 32

_LATTICE_RADIUS = 150.0
_KEY_HALO_RADIUS = 196.0

_NODE_BASE_SIZE = 4.0
_NODE_GAIN = 16.0

_ACTIVE_EDGE_THRESHOLD = 0.045

_TENSION_CAPACITY = 1600 if _IS_DESKTOP else 420
_CONSTELLATION_CAPACITY = 220 if _IS_DESKTOP else 60
_BASSLINE_CAPACITY = 280 if _IS_DESKTOP else 130

_FRACTAL_DEPTH = 5 if _IS_DESKTOP else 3
_FRACTAL_JITTER = 4.0

_MELODY_BURST_SIZE = 6 if _IS_DESKTOP else 3


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


def _lerp_color(a, b, t):

    t = max(0.0, min(1.0, t))

    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class AudioReactiveMode5(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 5 (Tonal Instrument)")

        self.audio = MusicAnalyzer(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            spectrum_resolution=_SPECTRUM_RESOLUTION,
        )

        self.rotation = 0.0

        self.chord_flash = 0.0
        self.bar_pulse = 0.0

        self.bassline = None
        self.constellation = None
        self.tension_field = None

        self._fractal_segments = []

        self._dim_color = (0.0, 0.0, 0.0)
        self._bright_color = (1.0, 1.0, 1.0)
        self._dim_accent = (0.0, 0.0, 0.0)
        self._bright_accent = (1.0, 1.0, 1.0)

        self.lattice_faint_renderable = None
        self.lattice_active_renderable = None
        self.node_renderable = None
        self.chord_renderable = None
        self.fractal_renderable = None
        self.key_halo_renderable = None
        self.bassline_renderable = None
        self.constellation_renderable = None
        self.tension_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        self.bassline = BasslineSpiral(capacity=_BASSLINE_CAPACITY)

        self.constellation = MelodyConstellation(
            capacity=_CONSTELLATION_CAPACITY,
            random=context.random,
        )

        self.tension_field = TensionField(
            capacity=_TENSION_CAPACITY,
            random=context.random,
        )

        theme = context.theme

        self._dim_color = _normalize_color(theme.trace_glow)
        self._bright_color = _normalize_color(theme.trace_core)
        self._dim_accent = _normalize_color(theme.trace_main)
        self._bright_accent = _normalize_color(theme.accent)

        self.lattice_faint_renderable = Renderable(
            material=Material(
                color=self._dim_color,
                line_width=1.0,
            ),
            is_dynamic=True,
        )

        self.lattice_active_renderable = Renderable(
            material=Material(
                color=self._bright_color,
                line_width=1.5,
            ),
            is_dynamic=True,
        )

        self.node_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.trace_main),
                line_width=1.5,
            ),
            is_dynamic=True,
        )

        self.chord_renderable = Renderable(
            material=Material(
                color=self._bright_accent,
                line_width=2.5,
            ),
            is_dynamic=True,
        )

        self.fractal_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.text),
                line_width=1.0,
            ),
            is_dynamic=True,
        )

        self.key_halo_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.accent),
                line_width=2.0,
            ),
            is_dynamic=True,
        )

        self.bassline_renderable = Renderable(
            material=Material(
                color=self._bright_color,
                line_width=1.5,
            ),
            is_dynamic=True,
        )

        self.constellation_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.text),
                line_width=1.0,
            ),
            is_dynamic=True,
        )

        self.tension_renderable = Renderable(
            material=Material(
                color=_normalize_color(theme.trace_glow),
                line_width=1.0,
            ),
            is_dynamic=True,
        )

    # ---------------------------------------------------------

    def update(self, context):

        dt = context.delta_time

        audio = self.audio

        self.rotation += dt * (0.035 + audio.tension * 0.12)

        self.chord_flash *= math.exp(-dt * 4.0)

        if audio.chord_changed:
            self.chord_flash = 1.0

        self.bar_pulse *= math.exp(-dt * 5.0)

        if audio.on_downbeat:
            self.bar_pulse = 1.0

        bass_angle = theory.node_angle(audio.bass_note_class, self.rotation)

        self.bassline.push(bass_angle, audio.bass_note_confidence)

        melody_trigger = audio.harmonic_change > 0.35 or audio.high_hit

        if melody_trigger and audio.melody_note_confidence > 0.2:

            origin = theory.node_position(
                audio.melody_note_class,
                (0.0, 0.0),
                _LATTICE_RADIUS * 0.82,
                self.rotation,
            )

            self.constellation.spawn(
                origin=origin,
                count=_MELODY_BURST_SIZE,
                speed_scale=1.0 + audio.high,
            )

        self.constellation.update(dt)

        chroma_peak = float(audio.chroma.max()) + 1e-6

        chord_energy = float(
            np.mean(
                [audio.chroma[pc] / chroma_peak for pc in audio.chord_tones]
            )
        )

        self.tension_field.set_parameters(
            tension=audio.tension,
            chord_energy=chord_energy,
        )

        self.tension_field.update(
            reseed_fraction=0.012 + audio.tension * 0.02
        )

        if audio.attack_hit or audio.on_downbeat or not self._fractal_segments:

            positions = theory.node_positions(
                (0.0, 0.0),
                _LATTICE_RADIUS,
                self.rotation,
            )

            triangle = tuple(
                positions[pc] for pc in audio.chord_tones
            )

            self._fractal_segments = fractal.subdivide_triangle(
                triangle,
                depth=_FRACTAL_DEPTH,
                jitter=_FRACTAL_JITTER,
                random=context.random,
            )

    # ---------------------------------------------------------

    def emit(self, context, frame):

        cx, cy = context.center

        audio = self.audio

        chroma_norm = audio.chroma / (float(audio.chroma.max()) + 1e-6)

        positions = theory.node_positions(
            (cx, cy),
            _LATTICE_RADIUS,
            self.rotation,
        )

        self.lattice_faint_renderable.clear()
        self.lattice_active_renderable.clear()

        total_brightness = 0.0
        active_count = 0

        for points, brightness in lattice.lattice_edges(chroma_norm, positions):

            self.lattice_faint_renderable.add(Polyline(points=points))

            if brightness > _ACTIVE_EDGE_THRESHOLD:

                self.lattice_active_renderable.add(Polyline(points=points))

                total_brightness += brightness
                active_count += 1

        avg_brightness = (
            total_brightness / active_count if active_count else 0.0
        )

        self.lattice_active_renderable.material = Material(
            color=_lerp_color(
                self._dim_color,
                self._bright_color,
                min(1.0, avg_brightness * 2.2),
            ),
            line_width=1.0 + min(1.0, avg_brightness * 2.0) * 2.5,
        )

        self.node_renderable.clear()

        for pitch_class in range(12):

            energy = float(chroma_norm[pitch_class])

            points = lattice.node_pulse(
                pitch_class,
                positions,
                energy,
                _NODE_BASE_SIZE,
                _NODE_GAIN,
            )

            self.node_renderable.add(Polyline(points=points))

        self.chord_renderable.clear()

        chord_points = lattice.chord_polygon(audio.chord_tones, positions)

        self.chord_renderable.add(Polyline(points=chord_points))

        chord_brightness = min(1.0, audio.chord_confidence + self.chord_flash * 0.6)

        self.chord_renderable.material = Material(
            color=_lerp_color(
                self._dim_accent,
                self._bright_accent,
                chord_brightness,
            ),
            line_width=2.0 + self.chord_flash * 3.5,
        )

        self.fractal_renderable.clear()

        for a, b in self._fractal_segments:

            points = np.array(
                [
                    [a[0] + cx, a[1] + cy],
                    [b[0] + cx, b[1] + cy],
                ],
                dtype=np.float32,
            )

            self.fractal_renderable.add(Polyline(points=points))

        self.fractal_renderable.material = Material(
            color=_lerp_color(
                self._dim_accent,
                self._bright_color,
                audio.tension,
            ),
            line_width=1.0 + self.bar_pulse * 1.5,
        )

        self.key_halo_renderable.clear()

        halo_points = lattice.key_halo(
            audio.key_tonic,
            (cx, cy),
            _KEY_HALO_RADIUS,
            self.rotation,
            audio.key_confidence,
        )

        self.key_halo_renderable.add(Polyline(points=halo_points))

        self.key_halo_renderable.material = Material(
            color=_normalize_color(context.theme.accent),
            line_width=1.5 + audio.key_confidence * 2.5,
        )

        self.bassline_renderable.clear()

        spiral_points = self.bassline.points(
            (cx, cy),
            inner_radius=18.0,
            radius_step=0.55,
        )

        if len(spiral_points) >= 2:

            self.bassline_renderable.add(Polyline(points=spiral_points))

        self.bassline_renderable.material = Material(
            color=_lerp_color(
                self._bright_color,
                self._bright_accent,
                audio.tension,
            ),
            line_width=1.3 + audio.bass_note_confidence * 1.5,
        )

        self.constellation_renderable.clear()

        spark_positions, spark_life = self.constellation.points()

        for (x, y), life in zip(spark_positions, spark_life):

            size = 2.0 + life * 4.0

            self.constellation_renderable.add(
                Polyline(
                    points=np.array(
                        [
                            [cx + x - size, cy + y],
                            [cx + x + size, cy + y],
                        ],
                        dtype=np.float32,
                    )
                )
            )

        self.tension_renderable.clear()

        scale = 95.0 * (0.8 + audio.tension * 0.6 + audio.section_energy * 0.2)

        dust_positions = self.tension_field.points((0.0, 0.0), scale)

        dust_positions[:, 0] += cx
        dust_positions[:, 1] += cy

        for x, y in dust_positions:

            self.tension_renderable.add(
                Polyline(
                    points=np.array(
                        [[x, y], [x + 0.6, y + 0.6]],
                        dtype=np.float32,
                    )
                )
            )

        self.tension_renderable.material = Material(
            color=_lerp_color(
                self._dim_color,
                self._bright_accent,
                audio.tension,
            ),
            line_width=1.0,
        )

        #
        # Submit renderables, back to front.
        #

        frame.add_renderable(self.tension_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.lattice_faint_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.lattice_active_renderable, Layer.MAIN)
        frame.add_renderable(self.node_renderable, Layer.MAIN)
        frame.add_renderable(self.key_halo_renderable, Layer.MAIN)
        frame.add_renderable(self.bassline_renderable, Layer.MAIN)
        frame.add_renderable(self.fractal_renderable, Layer.MAIN)
        frame.add_renderable(self.chord_renderable, Layer.OVERLAY)
        frame.add_renderable(self.constellation_renderable, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()
