"""
RetroScope

Black Hole Geometry Generator

Composition layer.

This module simply delegates geometry generation
to specialized generators.
"""

from .disk import generate_disk
from .grid import generate_lensing_grid
from .horizon import generate_event_horizon
from .photon import generate_photon_rings


build_event_horizon = generate_event_horizon

build_photon_rings = generate_photon_rings

build_accretion_disk = generate_disk

build_lensing_grid = generate_lensing_grid