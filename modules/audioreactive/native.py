"""
RetroScope

Native Acceleration Bridge - Audio Reactive Modules

Ported modules (currently Mode 1) import particle/geometry helpers
from here instead of importing their pure-Python implementation
directly. This module tries to load the compiled native extension
(modules/audioreactive/_native/) first; if it isn't built for the
current platform, it transparently falls back to the original
pure-Python implementation, so nothing breaks on a machine that
hasn't run the build step yet - same "native accelerates, Python
describes" split used by render_es2/_native.

To build the native extension:

    cd modules/audioreactive/_native
    python3 setup.py build_ext --inplace

This has to be run separately on each target platform (the same way
render_es2/_native's checked-in .so is Mac-specific and won't load on
a Raspberry Pi) - there is no cross-compiled binary checked in here.
"""

from __future__ import annotations

try:

    from modules.audioreactive._native import _native as _native_audio

    NATIVE_AVAILABLE = True

except ImportError:

    _native_audio = None

    NATIVE_AVAILABLE = False


if NATIVE_AVAILABLE:

    class EmberField:
        """
        Native-backed drop-in replacement for
        modules/audioreactive/mode1/particles.py's EmberField.

        The native side uses its own fast xorshift RNG rather than
        the passed-in `random.Random`, seeded once from it, so calls
        stay unpredictable-looking without paying the cost of calling
        back into the interpreter per particle.
        """

        def __init__(self, capacity: int, inner_radius: float, random):

            seed = random.getrandbits(32) if random is not None else 0

            self._native = _native_audio.EmberField(
                capacity,
                float(inner_radius),
                seed,
            )

            self.capacity = capacity
            self.inner_radius = inner_radius
            self.random = random

        def spawn(self, count: int):

            self._native.spawn(count)

        def update(self, dt: float):

            self._native.update(dt)

        def points(self):

            return self._native.points()

    def spectrum_ring(
        magnitudes,
        base_radius: float,
        amplitude: float,
        rotation: float = 0.0,
        mirror: bool = True,
    ):

        return _native_audio.spectrum_ring(
            magnitudes,
            float(base_radius),
            float(amplitude),
            float(rotation),
            bool(mirror),
        )

else:

    print(
        "[modules.audioreactive.native] native extension not built - "
        "falling back to pure-Python EmberField/spectrum_ring."
    )

    from modules.audioreactive.mode1.particles import EmberField
    from modules.audioreactive.mode1.spectrum import spectrum_ring


__all__ = ["EmberField", "spectrum_ring", "NATIVE_AVAILABLE"]
