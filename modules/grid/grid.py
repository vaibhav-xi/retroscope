"""
RetroScope

Grid Module

Produces the oscilloscope grid.
"""

import config

from core.frame import Layer
from core.module import Module

from render.primitives import Polyline
from render.renderable import Renderable
from render_es2.material import Material


class GridModule(Module):

    def __init__(self):

        super().__init__("Grid")

        self.columns = 10
        self.rows = 8
        self.minor_divisions = 5

    # ---------------------------------------------------------

    def initialize(self, context):

        pass

    # ---------------------------------------------------------

    def update(self, context):

        pass

    # ---------------------------------------------------------

    def emit(self, context, frame):

        width = config.WIDTH
        height = config.HEIGHT

        dx = width / self.columns
        dy = height / self.rows

        #
        # Entire grid becomes ONE renderable.
        #

        grid = Renderable(
            is_dynamic=False,
            material=Material(
                color=(
                    1.0,
                    0.0,
                    0.0,
                ),
            ),
        )

        #
        # Major Vertical Lines
        #

        for i in range(self.columns + 1):

            x = i * dx

            grid.add(

                Polyline(

                    points=[
                        (x, 0),
                        (x, height),
                    ],

                    width=1,

                )

            )

        #
        # Major Horizontal Lines
        #

        for i in range(self.rows + 1):

            y = i * dy

            grid.add(

                Polyline(

                    points=[
                        (0, y),
                        (width, y),
                    ],

                    width=1,

                )

            )

        #
        # Minor Vertical Lines
        #

        # step = dx / self.minor_divisions

        # for major in range(self.columns):

        #     for minor in range(1, self.minor_divisions):

        #         x = major * dx + minor * step

        #         grid.add(

        #             Polyline(

        #                 points=[
        #                     (x, 0),
        #                     (x, height),
        #                 ],

        #                 width=1,

        #             )

        #         )

        #
        # Minor Horizontal Lines
        #

        # step = dy / self.minor_divisions

        # for major in range(self.rows):

        #     for minor in range(1, self.minor_divisions):

        #         y = major * dy + minor * step

        #         grid.add(

        #             Polyline(

        #                 points=[
        #                     (0, y),
        #                     (width, y),
        #                 ],

        #                 width=1,

        #             )

        #         )

        #
        # Submit a single renderable.
        #

        frame.add_renderable(
            grid,
            Layer.BACKGROUND,
        )

    # ---------------------------------------------------------

    def shutdown(self):

        pass