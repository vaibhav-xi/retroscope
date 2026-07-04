"""
RetroScope

CRT Pipeline

Coordinates every CRT post-processing stage.

Pipeline Order

Beam
 ↓
Bloom
 ↓
Persistence
 ↓
Scanlines
 ↓
Noise
 ↓
Vignette
 ↓
Display
"""

from __future__ import annotations

from render_backup.crt.persistence import PersistenceStage
from render_backup.crt.bloom import BloomStage
from render_backup.crt.scanlines import ScanlineStage
from render_backup.crt.noise import NoiseStage
from render_backup.crt.vignette import VignetteStage


class CRTPipeline:

    def __init__(self):

        #
        # Order matters.
        #

        self.bloom = BloomStage()

        self.persistence = PersistenceStage()

        self.scanlines = ScanlineStage()

        self.noise = NoiseStage()

        self.vignette = VignetteStage()

    # ---------------------------------------------------------

    def process(self, surface):
        """
        Apply CRT effects.

        IMPORTANT:

        Bloom is applied only to the freshly rendered beam.

        The persistence stage stores the already-bloomed beam,
        preventing the bloom from recursively amplifying itself
        every frame.
        """

        #
        # Fresh beam
        #

        self.bloom.process(surface)

        #
        # Phosphor memory
        #

        self.persistence.process(surface)

        #
        # Display effects
        #

        self.scanlines.process(surface)

        self.noise.process(surface)

        self.vignette.process(surface)