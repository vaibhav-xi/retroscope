
from __future__ import annotations

try:

    from modules.audioreactive._native import _native as _native_audio

    NATIVE_AVAILABLE = True

except ImportError:

    _native_audio = None

    NATIVE_AVAILABLE = False


if NATIVE_AVAILABLE:

    class EmberField:

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
