

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
from .impact import ImpactSystem
from .shockwave import BlastField
from .debris import Debris
from .chain import ChainFlashes, lightning_bolt
from .tension_field import InfernoField
from .bassline import BasslineSpiral
from .constellation import MelodyConstellation

_IS_DESKTOP = platform.system() == "Darwin"

_SPECTRUM_RESOLUTION = 64 if _IS_DESKTOP else 32

_LATTICE_RADIUS = 132.0
_KEY_HALO_RADIUS = 186.0

_NODE_BASE_SIZE = 4.0
_NODE_GAIN = 18.0

_ACTIVE_EDGE_THRESHOLD = 0.04

_INFERNO_CAPACITY = 2200 if _IS_DESKTOP else 600
_DEBRIS_CAPACITY = 900 if _IS_DESKTOP else 220
_EMBER_CAPACITY = 500 if _IS_DESKTOP else 140
_CONSTELLATION_CAPACITY = 320 if _IS_DESKTOP else 90
_BASSLINE_CAPACITY = 300 if _IS_DESKTOP else 140

_BLAST_CAPACITY = 22 if _IS_DESKTOP else 10
_BOOM_CAPACITY = 24 if _IS_DESKTOP else 10

_FRACTAL_DEPTH = 5 if _IS_DESKTOP else 3
_FRACTAL_JITTER = 5.0

_HIT_BURST = 30 if _IS_DESKTOP else 10
_DOWNBEAT_BURST = 150 if _IS_DESKTOP else 45
_DROP_BURST = 320 if _IS_DESKTOP else 90


def _normalize_color(color_255):

    return tuple(c / 255.0 for c in color_255)


def _lerp_color(a, b, t):

    t = max(0.0, min(1.0, t))

    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class AudioReactiveMode6(Module):

    def __init__(self):

        super().__init__("Audio Reactive - Mode 6 (Detonation Instrument)")

        self.audio = MusicAnalyzer(
            device=config.AUDIO_DEVICE,
            samplerate=config.AUDIO_SAMPLE_RATE,
            block_size=config.AUDIO_BLOCK_SIZE,
            spectrum_resolution=_SPECTRUM_RESOLUTION,
        )

        self.rotation = 0.0

        self.chord_flash = 0.0

        self.impact = ImpactSystem()

        self.bassline = None
        self.constellation = None
        self.inferno = None
        self.blasts = None
        self.booms = None
        self.debris = None
        self.embers = None
        self.chains = None

        self._fractal_segments = []

        self._dim_color = (0.0, 0.0, 0.0)
        self._bright_color = (1.0, 1.0, 1.0)
        self._dim_accent = (0.0, 0.0, 0.0)
        self._bright_accent = (1.0, 1.0, 1.0)

        self.inferno_renderable = None
        self.lattice_faint_renderable = None
        self.lattice_active_renderable = None
        self.node_renderable = None
        self.chord_renderable = None
        self.fractal_renderable = None
        self.key_halo_renderable = None
        self.bassline_renderable = None
        self.constellation_renderable = None
        self.blast_renderable = None
        self.boom_renderable = None
        self.debris_renderable = None
        self.ember_renderable = None
        self.chain_renderable = None

    # ---------------------------------------------------------

    def initialize(self, context):

        self.audio.start()

        self.bassline = BasslineSpiral(capacity=_BASSLINE_CAPACITY)

        self.constellation = MelodyConstellation(
            capacity=_CONSTELLATION_CAPACITY,
            random=context.random,
        )

        self.inferno = InfernoField(
            capacity=_INFERNO_CAPACITY,
            random=context.random,
        )

        self.blasts = BlastField(capacity=_BLAST_CAPACITY, segments=40)
        self.booms = BlastField(capacity=_BOOM_CAPACITY, segments=56)

        self.debris = Debris(capacity=_DEBRIS_CAPACITY, random=context.random, drag=2.4)
        self.embers = Debris(capacity=_EMBER_CAPACITY, random=context.random, drag=3.2)

        self.chains = ChainFlashes(capacity=20)

        theme = context.theme

        self._dim_color = _normalize_color(theme.trace_glow)
        self._bright_color = _normalize_color(theme.trace_core)
        self._dim_accent = _normalize_color(theme.trace_main)
        self._bright_accent = _normalize_color(theme.accent)
        self._text_color = _normalize_color(theme.text)

        self.inferno_renderable = Renderable(
            material=Material(color=self._dim_color, line_width=1.0),
            is_dynamic=True,
        )

        self.lattice_faint_renderable = Renderable(
            material=Material(color=self._dim_color, line_width=1.0),
            is_dynamic=True,
        )

        self.lattice_active_renderable = Renderable(
            material=Material(color=self._bright_color, line_width=1.5),
            is_dynamic=True,
        )

        self.node_renderable = Renderable(
            material=Material(color=self._dim_accent, line_width=1.5),
            is_dynamic=True,
        )

        self.chord_renderable = Renderable(
            material=Material(color=self._bright_accent, line_width=2.5),
            is_dynamic=True,
        )

        self.fractal_renderable = Renderable(
            material=Material(color=self._text_color, line_width=1.0),
            is_dynamic=True,
        )

        self.key_halo_renderable = Renderable(
            material=Material(color=self._bright_accent, line_width=2.0),
            is_dynamic=True,
        )

        self.bassline_renderable = Renderable(
            material=Material(color=self._bright_color, line_width=1.5),
            is_dynamic=True,
        )

        self.constellation_renderable = Renderable(
            material=Material(color=self._text_color, line_width=1.0),
            is_dynamic=True,
        )

        self.blast_renderable = Renderable(
            material=Material(color=self._dim_accent, line_width=1.5),
            is_dynamic=True,
        )

        self.boom_renderable = Renderable(
            material=Material(color=self._bright_color, line_width=2.5),
            is_dynamic=True,
        )

        self.debris_renderable = Renderable(
            material=Material(color=self._bright_accent, line_width=1.5),
            is_dynamic=True,
        )

        self.ember_renderable = Renderable(
            material=Material(color=self._text_color, line_width=1.0),
            is_dynamic=True,
        )

        self.chain_renderable = Renderable(
            material=Material(color=self._bright_color, line_width=1.5),
            is_dynamic=True,
        )

    # ---------------------------------------------------------

    def update(self, context):

        dt = context.delta_time

        audio = self.audio

        random = context.random

        beat_trigger = (
            audio.on_beat if audio.beat_confidence > 0.3 else audio.attack_hit
        )

        downbeat_trigger = (
            audio.on_downbeat and audio.beat_confidence > 0.3
        )

        chord_tones = audio.chord_tones

        self.rotation += dt * (
            0.10 + audio.tension * 0.5 + self.impact.spin_velocity
        )

        self.chord_flash *= math.exp(-dt * 4.0)

        if audio.chord_changed:
            self.chord_flash = 1.0

        bass_angle = theory.node_angle(audio.bass_note_class, self.rotation)

        self.bassline.push(bass_angle, audio.bass_note_confidence)

        melody_trigger = audio.harmonic_change > 0.3 or audio.high_hit

        if melody_trigger and audio.melody_note_confidence > 0.2:

            origin = theory.node_position(
                audio.melody_note_class,
                (0.0, 0.0),
                _LATTICE_RADIUS * 0.82,
                self.rotation,
            )

            self.constellation.spawn(
                origin=origin,
                count=(10 if _IS_DESKTOP else 4),
                speed_scale=1.2 + audio.high,
            )

            bass_pos = theory.node_position(
                audio.bass_note_class, (0.0, 0.0), _LATTICE_RADIUS, self.rotation
            )

            melody_pos = theory.node_position(
                audio.melody_note_class, (0.0, 0.0), _LATTICE_RADIUS, self.rotation
            )

            self.chains.spawn(
                lightning_bolt(
                    bass_pos,
                    melody_pos,
                    depth=3,
                    jitter=4.0 + (1.0 - audio.interval_consonance) * 20.0,
                    random=random,
                ),
                lifetime=0.3,
            )

        self.constellation.update(dt)

        chroma_peak = float(audio.chroma.max()) + 1e-6

        chord_energy = float(
            np.mean([audio.chroma[pc] / chroma_peak for pc in chord_tones])
        )

        self.inferno.set_parameters(tension=audio.tension, chord_energy=chord_energy)

        self.inferno.update(dt, reseed_fraction=0.02 + audio.tension * 0.03)

        if audio.attack_hit:

            hit_pc = chord_tones[random.randrange(3)]

            hit_origin = theory.node_position(
                hit_pc, (0.0, 0.0), _LATTICE_RADIUS, self.rotation
            )

            self.debris.burst(
                origin=hit_origin,
                count=_HIT_BURST,
                speed_range=(140.0, 380.0 + audio.attack * 260.0),
                lifetime_range=(0.25, 0.6),
            )

            self.blasts.spawn(
                strength=10.0 + audio.attack * 22.0,
                speed=180.0 + audio.attack * 220.0,
                wobble=0.3,
            )

            self.impact.shake(4.0 + audio.attack * 10.0, random)
            self.impact.kick_node(hit_pc, 8.0 + audio.attack * 18.0)

            self._fractal_segments = self._rebuild_fractal(chord_tones, random)

        if audio.high_hit:

            self.embers.burst(
                origin=(0.0, 0.0),
                count=(24 if _IS_DESKTOP else 8),
                speed_range=(200.0, 500.0),
                lifetime_range=(0.15, 0.4),
            )

        if audio.mid_hit or audio.bass_hit:

            self.impact.shake(2.0, random)

        if beat_trigger:

            self.impact.kick_scale(0.22)

            self.blasts.spawn(
                strength=16.0 + audio.bass * 20.0,
                speed=220.0 + audio.bass * 200.0,
                wobble=0.2,
            )

            root_pos = theory.node_position(
                chord_tones[0], (0.0, 0.0), _LATTICE_RADIUS, self.rotation
            )

            third_pos = theory.node_position(
                chord_tones[1], (0.0, 0.0), _LATTICE_RADIUS, self.rotation
            )

            self.chains.spawn(
                lightning_bolt(root_pos, third_pos, depth=3, jitter=6.0, random=random),
                lifetime=0.25,
            )

        if downbeat_trigger:

            self._detonate(context, chord_tones, strength=1.0)

        if audio.drop:

            self._detonate(context, chord_tones, strength=1.8)

            self.debris.burst(
                origin=(0.0, 0.0),
                count=_DROP_BURST,
                speed_range=(200.0, 620.0),
                lifetime_range=(0.4, 1.1),
            )

        self.blasts.update(dt)
        self.booms.update(dt)
        self.debris.update(dt)
        self.embers.update(dt)
        self.chains.update(dt)

        self.impact.update(dt)

    # ---------------------------------------------------------

    def _rebuild_fractal(self, chord_tones, random):

        positions = theory.node_positions((0.0, 0.0), _LATTICE_RADIUS, self.rotation)

        triangle = tuple(positions[pc] for pc in chord_tones)

        return fractal.subdivide_triangle(
            triangle,
            depth=_FRACTAL_DEPTH,
            jitter=_FRACTAL_JITTER,
            random=random,
        )

    # ---------------------------------------------------------

    def _detonate(self, context, chord_tones, strength: float):

        random = context.random

        audio = self.audio

        positions = theory.node_positions((0.0, 0.0), _LATTICE_RADIUS, self.rotation)

        for i in range(3):

            self.booms.spawn(
                strength=(26.0 + i * 10.0) * strength,
                speed=(260.0 + i * 60.0) * strength,
                wobble=0.08,
                start_radius=6.0 + i * 14.0,
            )

        for pc in chord_tones:

            origin = positions[pc]

            self.debris.burst(
                origin=origin,
                count=int(_DOWNBEAT_BURST * strength),
                speed_range=(160.0, 460.0 * strength),
                lifetime_range=(0.35, 0.9),
            )

        bolt_pairs = (
            (chord_tones[0], chord_tones[1]),
            (chord_tones[1], chord_tones[2]),
            (chord_tones[2], chord_tones[0]),
        )

        for a, b in bolt_pairs:

            self.chains.spawn(
                lightning_bolt(
                    positions[a], positions[b], depth=4, jitter=8.0, random=random
                ),
                lifetime=0.45,
            )

        chroma_peak = float(audio.chroma.max()) + 1e-6

        node_kicks = np.array(
            [
                (float(audio.chroma[pc]) / chroma_peak) * 16.0 * strength
                for pc in range(12)
            ],
            dtype=np.float32,
        )

        self.impact.kick_all_nodes(node_kicks)
        self.impact.kick_scale(0.6 * strength)
        self.impact.kick_spin(1.1 * strength)
        self.impact.shake(14.0 * strength, random)
        self.impact.ignite_flash(min(1.0, strength))

        self.inferno.detonate(min(1.5, strength))

        self._fractal_segments = self._rebuild_fractal(chord_tones, random)

    # ---------------------------------------------------------

    def emit(self, context, frame):

        base_cx, base_cy = context.center

        audio = self.audio

        cx = base_cx + float(self.impact.shake_offset[0])
        cy = base_cy + float(self.impact.shake_offset[1])

        scale = self.impact.scale_pulse

        lattice_radius = _LATTICE_RADIUS * scale
        key_halo_radius = _KEY_HALO_RADIUS * scale

        chroma_norm = audio.chroma / (float(audio.chroma.max()) + 1e-6)

        positions = theory.node_positions_with_impulse(
            (cx, cy),
            lattice_radius,
            self.rotation,
            self.impact.node_impulse,
        )

        flash = self.impact.flash

        #
        # Lattice.
        #

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

        avg_brightness = total_brightness / active_count if active_count else 0.0

        self.lattice_active_renderable.material = Material(
            color=_lerp_color(
                _lerp_color(self._dim_color, self._bright_color, min(1.0, avg_brightness * 2.2)),
                self._bright_color,
                flash,
            ),
            line_width=1.2 + min(1.0, avg_brightness * 2.0) * 3.0 + flash * 2.0,
        )

        #
        # Node pulses.
        #

        self.node_renderable.clear()

        for pitch_class in range(12):

            energy = float(chroma_norm[pitch_class]) + abs(
                float(self.impact.node_impulse[pitch_class])
            ) / _NODE_GAIN

            points = lattice.node_pulse(
                pitch_class, positions, energy, _NODE_BASE_SIZE, _NODE_GAIN
            )

            self.node_renderable.add(Polyline(points=points))

        #
        # Chord triangle.
        #

        self.chord_renderable.clear()

        chord_points = lattice.chord_polygon(audio.chord_tones, positions)

        self.chord_renderable.add(Polyline(points=chord_points))

        chord_brightness = min(1.0, audio.chord_confidence + self.chord_flash * 0.7 + flash * 0.5)

        self.chord_renderable.material = Material(
            color=_lerp_color(self._dim_accent, self._bright_accent, chord_brightness),
            line_width=2.2 + self.chord_flash * 4.0 + flash * 3.0,
        )

        #
        # Fractal fill.
        #

        self.fractal_renderable.clear()

        for a, b in self._fractal_segments:

            points = np.array(
                [
                    [a[0] * scale + cx, a[1] * scale + cy],
                    [b[0] * scale + cx, b[1] * scale + cy],
                ],
                dtype=np.float32,
            )

            self.fractal_renderable.add(Polyline(points=points))

        self.fractal_renderable.material = Material(
            color=_lerp_color(self._dim_accent, self._bright_color, min(1.0, audio.tension + flash * 0.5)),
            line_width=1.0 + flash * 2.0,
        )

        #
        # Key halo.
        #

        self.key_halo_renderable.clear()

        halo_points = lattice.key_halo(
            audio.key_tonic, (cx, cy), key_halo_radius, self.rotation, audio.key_confidence
        )

        self.key_halo_renderable.add(Polyline(points=halo_points))

        self.key_halo_renderable.material = Material(
            color=_lerp_color(self._dim_accent, self._bright_accent, audio.key_confidence),
            line_width=1.8 + audio.key_confidence * 3.0,
        )

        #
        # Bassline spiral.
        #

        self.bassline_renderable.clear()

        spiral_points = self.bassline.points(
            (cx, cy), inner_radius=16.0, radius_step=0.85
        )

        if len(spiral_points) >= 2:

            self.bassline_renderable.add(Polyline(points=spiral_points))

        self.bassline_renderable.material = Material(
            color=_lerp_color(self._bright_color, self._bright_accent, audio.tension),
            line_width=1.4 + audio.bass_note_confidence * 2.0,
        )

        #
        # Melody constellation.
        #

        self.constellation_renderable.clear()

        spark_positions, spark_life = self.constellation.points()

        for (x, y), life in zip(spark_positions, spark_life):

            size = 2.0 + life * 5.0

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

        self.constellation_renderable.material = Material(
            color=_lerp_color(self._text_color, self._bright_color, flash),
            line_width=1.0 + flash * 1.5,
        )

        #
        # Blast rings (per-beat).
        #

        self.blast_renderable.clear()

        for points, life in self.blasts.rings((cx, cy)):

            self.blast_renderable.add(Polyline(points=points))

        self.blast_renderable.material = Material(
            color=_lerp_color(self._dim_accent, self._bright_color, 0.4 + flash * 0.4),
            line_width=1.5 + flash * 1.5,
        )

        #
        # Boom rings (downbeat / drop detonations).
        #

        self.boom_renderable.clear()

        for points, life in self.booms.rings((cx, cy)):

            self.boom_renderable.add(Polyline(points=points))

        self.boom_renderable.material = Material(
            color=_lerp_color(self._bright_accent, self._bright_color, flash),
            line_width=2.0 + flash * 4.0,
        )

        #
        # Shrapnel (debris + embers).
        #

        self.debris_renderable.clear()

        heads, tails, life = self.debris.segments()

        for (hx, hy), (tx, ty) in zip(heads, tails):

            self.debris_renderable.add(
                Polyline(
                    points=np.array(
                        [[hx + cx, hy + cy], [tx + cx, ty + cy]],
                        dtype=np.float32,
                    )
                )
            )

        self.debris_renderable.material = Material(
            color=_lerp_color(self._dim_accent, self._bright_accent, 0.5 + flash * 0.5),
            line_width=1.4 + flash * 2.0,
        )

        self.ember_renderable.clear()

        ember_heads, ember_tails, ember_life = self.embers.segments()

        for (hx, hy), (tx, ty) in zip(ember_heads, ember_tails):

            self.ember_renderable.add(
                Polyline(
                    points=np.array(
                        [[hx + cx, hy + cy], [tx + cx, ty + cy]],
                        dtype=np.float32,
                    )
                )
            )

        self.ember_renderable.material = Material(
            color=_lerp_color(self._text_color, self._bright_color, flash),
            line_width=1.0 + flash * 1.5,
        )

        #
        # Chain lightning.
        #

        self.chain_renderable.clear()

        for points, life in self.chains.segments():

            translated = points.copy()

            translated[:, 0] += cx
            translated[:, 1] += cy

            self.chain_renderable.add(Polyline(points=translated))

        self.chain_renderable.material = Material(
            color=_lerp_color(self._dim_accent, self._bright_color, 0.6 + flash * 0.4),
            line_width=1.2 + flash * 2.0,
        )

        #
        # Inferno field - the dense chaotic backdrop.
        #

        self.inferno_renderable.clear()

        inferno_scale = 100.0 * scale * (
            0.85 + audio.tension * 0.7 + audio.section_energy * 0.25
        )

        inferno_positions = self.inferno.points((0.0, 0.0), inferno_scale)

        inferno_positions[:, 0] += cx
        inferno_positions[:, 1] += cy

        for x, y in inferno_positions:

            self.inferno_renderable.add(
                Polyline(
                    points=np.array(
                        [[x, y], [x + 0.7, y + 0.7]],
                        dtype=np.float32,
                    )
                )
            )

        self.inferno_renderable.material = Material(
            color=_lerp_color(self._dim_color, self._bright_accent, audio.tension),
            line_width=1.0,
        )

        #
        # Submit renderables, back to front.
        #

        frame.add_renderable(self.inferno_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.lattice_faint_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.blast_renderable, Layer.BACKGROUND)
        frame.add_renderable(self.lattice_active_renderable, Layer.MAIN)
        frame.add_renderable(self.node_renderable, Layer.MAIN)
        frame.add_renderable(self.key_halo_renderable, Layer.MAIN)
        frame.add_renderable(self.bassline_renderable, Layer.MAIN)
        frame.add_renderable(self.fractal_renderable, Layer.MAIN)
        frame.add_renderable(self.debris_renderable, Layer.MAIN)
        frame.add_renderable(self.chain_renderable, Layer.MAIN)
        frame.add_renderable(self.boom_renderable, Layer.OVERLAY)
        frame.add_renderable(self.chord_renderable, Layer.OVERLAY)
        frame.add_renderable(self.constellation_renderable, Layer.OVERLAY)
        frame.add_renderable(self.ember_renderable, Layer.OVERLAY)

    # ---------------------------------------------------------

    def shutdown(self):

        self.audio.stop()

