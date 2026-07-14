
from __future__ import annotations

import numpy as np


def subdivide_triangle(triangle, depth: int, jitter: float = 0.0, random=None):

    p0, p1, p2 = (np.asarray(p, dtype=np.float32) for p in triangle)

    segments = []

    def _mid(a, b):

        m = (a + b) * 0.5

        if jitter and random is not None:

            m = m + np.array(
                [
                    random.uniform(-jitter, jitter),
                    random.uniform(-jitter, jitter),
                ],
                dtype=np.float32,
            )

        return m

    def _recurse(a, b, c, level):

        if level <= 0:
            return

        ab = _mid(a, b)
        bc = _mid(b, c)
        ca = _mid(c, a)

        segments.append((ab, bc))
        segments.append((bc, ca))
        segments.append((ca, ab))

        _recurse(a, ab, ca, level - 1)
        _recurse(ab, b, bc, level - 1)
        _recurse(ca, bc, c, level - 1)

    _recurse(p0, p1, p2, depth)

    return segments
