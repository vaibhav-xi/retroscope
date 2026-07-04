"""
RetroScope

Grid Module

Produces the oscilloscope grid.

The module defines the grid geometry only.

Colors and visual appearance come from the active Theme.
"""

import config

from core.module import Module
from render.primitives import Polyline


class GridModule(Module):

    def __init__(self):

        super().__init__("Grid")

        #
        # Grid layout
        #

        self.columns = 10
        self.rows = 8
        self.minor_divisions = 5

    # ---------------------------------------------------------

    def initialize(self, context):

        self.cached = []

    # ---------------------------------------------------------

    def update(self, context):

        pass

    # ---------------------------------------------------------

    def emit(self, context, frame):
        
        if self.cached:

            for primitive in self.cached:
                frame.add(primitive)

            return

        theme = context.theme

        width = config.WIDTH
        height = config.HEIGHT

        dx = width / self.columns
        dy = height / self.rows

        #
        # Major Vertical Lines
        #

        for i in range(self.columns + 1):

            x = i * dx

            color = theme.grid_center if i == self.columns // 2 else theme.grid_major

            # frame.add(
            #     Polyline(
            #         points=[
            #             (x, 0),
            #             (x, height),
            #         ],
            #         color=color,
            #         width=1,
            #     )
            # )
            
            polyline = Polyline(
                points=[
                    (x, 0),
                    (x, height),
                ],
                color=color,
                width=1,
            )
            
            frame.add(polyline)
            self.cached.append(polyline)

        #
        # Major Horizontal Lines
        #

        for i in range(self.rows + 1):

            y = i * dy

            color = theme.grid_center if i == self.rows // 2 else theme.grid_major

            # frame.add(
            #     Polyline(
            #         points=[
            #             (0, y),
            #             (width, y),
            #         ],
            #         color=color,
            #         width=1,
            #     )
            # )
            
            polyline = Polyline(
                points=[
                    (0, y),
                    (width, y),
                ],
                color=color,
                width=1,
            )

            frame.add(polyline)
            self.cached.append(polyline)

        # #
        # # Minor Vertical Lines
        # #

        # step = dx / self.minor_divisions

        # for major in range(self.columns):

        #     for minor in range(1, self.minor_divisions):

        #         x = major * dx + minor * step

        #         frame.add(
        #             Polyline(
        #                 points=[
        #                     (x, 0),
        #                     (x, height),
        #                 ],
        #                 color=theme.grid_minor,
        #                 width=1,
        #             )
        #         )

        # #
        # # Minor Horizontal Lines
        # #

        # step = dy / self.minor_divisions

        # for major in range(self.rows):

        #     for minor in range(1, self.minor_divisions):

        #         y = major * dy + minor * step

        #         frame.add(
        #             Polyline(
        #                 points=[
        #                     (0, y),
        #                     (width, y),
        #                 ],
        #                 color=theme.grid_minor,
        #                 width=1,
        #             )
        #         )

    # ---------------------------------------------------------

    def shutdown(self):

        pass