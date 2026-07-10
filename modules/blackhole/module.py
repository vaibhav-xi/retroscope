from __future__ import annotations

import numpy as np

from core.module import Module

from render.primitives import Polyline
from render.renderable import Renderable
from render_es2.material import Material

from core.frame import Layer

from .generator import (
    build_event_horizon,
    build_photon_rings,
    build_accretion_disk,
    build_lensing_grid,
)

from .plasma import PlasmaSystem

class BlackHole(Module):

    def __init__(self):

        super().__init__("Black Hole")

        self.rotation = 0.0

        self.disk_speed = 0.35

        self.event_horizon_radius = 80.0

        self.disk_inner = 90.0
        self.disk_outer = 220.0

        self.grid_extent = 350.0
        self.grid_spacing = 25.0

        self.warp_strength = 850.0
        
        self.plasma = None
        
        self.grid = None
        self.disk = None
        self.photon = None
        self.horizon = None
        
    def _translate(self, points, context):

        points = np.asarray(points, dtype=np.float32)

        cx, cy = context.center

        points[:, 0] += cx
        points[:, 1] += cy

        return points

    # ---------------------------------------------------------

    def initialize(self, context):

        self.plasma = PlasmaSystem(

            inner_radius=self.disk_inner,

            outer_radius=self.disk_outer,

            count=1200,

            seed=1,

        )

        #
        # Persistent renderables
        #

        self.grid = Renderable(

            material=Material(

                color=(0.10, 0.35, 0.10),

                line_width=1.0,

            ),

        )

        self.grid.is_dynamic = False

        self.photon = Renderable(

            material=Material(

                color=(0.7, 1.0, 0.8),

                line_width=2.5,

            ),

        )

        self.photon.is_dynamic = False

        self.horizon = Renderable(

            material=Material(

                color=(0.0, 0.0, 0.0),

                line_width=3.0,

            ),

        )

        self.horizon.is_dynamic = False

        self.disk = Renderable(

            material=Material(

                color=(0.0, 1.0, 0.4),

                line_width=2.0,

            ),

        )

        self.disk.is_dynamic = True
        
        
        #
        # Grid (static)
        #

        for line in build_lensing_grid(

            extent=self.grid_extent,

            spacing=self.grid_spacing,

            strength=self.warp_strength,

        ):

            self.grid.add(

                Polyline(

                    points=self._translate(
                        line,
                        context,
                    )

                )

            )

        self.grid.is_dirty = True
        
        
        #
        # Photon Rings (static)
        #

        for ring in build_photon_rings(

            radius=self.event_horizon_radius + 8,

            count=3,

            spacing=8,

        ):

            self.photon.add(

                Polyline(

                    points=self._translate(
                        ring,
                        context,
                    )

                )

            )

        self.photon.is_dirty = True
        
        #
        # Event Horizon (static)
        #

        self.horizon.add(

            Polyline(

                points=self._translate(

                    build_event_horizon(

                        self.event_horizon_radius,

                    ),

                    context,

                )

            )

        )

        self.horizon.is_dirty = True

    # ---------------------------------------------------------

    def update(self, context):

        self.rotation += self.disk_speed * context.delta_time
        
        self.plasma.update(
            context.delta_time
        )

    # ---------------------------------------------------------

    def emit(self, context, frame):

        #
        # Update dynamic disk
        #

        self.disk.clear()

        for spiral in build_accretion_disk(

            inner_radius=self.disk_inner,
            outer_radius=self.disk_outer,
            arms=6,
            turns=2.5,
            rotation=self.rotation,

        ):

            self.disk.add(

                Polyline(

                    points=self._translate(
                        spiral,
                        context,
                    )

                )

            )

        #
        # Plasma
        #

        plasma = Renderable(

            material=Material(

                color=(0.9, 1.0, 0.9),
                line_width=1.0,

            )

        )

        for streak in self.plasma.streamlines():

            plasma.add(

                Polyline(

                    points=self._translate(
                        streak,
                        context,
                    )

                )

            )

        #
        # Submit renderables
        #

        frame.add_renderable(
            self.grid,
            Layer.BACKGROUND,
        )

        frame.add_renderable(
            self.disk,
            Layer.MAIN,
        )

        frame.add_renderable(
            plasma,
            Layer.MAIN,
        )

        frame.add_renderable(
            self.photon,
            Layer.OVERLAY,
        )

        frame.add_renderable(
            self.horizon,
            Layer.OVERLAY,
        )

    # ---------------------------------------------------------

    def shutdown(self):

        pass