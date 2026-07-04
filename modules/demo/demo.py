"""
RetroScope

Demo Module

This module exists only to validate the engine.

It emits one instance of every render primitive.
"""

from core.module import Module

from render_backup.primitives import (
    Point,
    Polyline,
    Circle,
    Rectangle,
    Text,
)


class DemoModule(Module):

    def __init__(self):

        super().__init__("Demo")

    # ---------------------------------------------------------

    def initialize(self, context):

        pass

    # ---------------------------------------------------------

    def update(self, context):

        pass

    # ---------------------------------------------------------

    def emit(self, frame):

        #
        # Point
        #

        frame.add(

            Point(

                position=(100, 100),

                color=(255, 255, 255),

                size=4,

            )

        )

        #
        # Polyline
        #

        frame.add(

            Polyline(

                points=[

                    (150, 150),

                    (250, 120),

                    (350, 170),

                ],

                color=(0, 255, 0),

                width=2,

            )

        )

        #
        # Circle
        #

        frame.add(

            Circle(

                center=(500, 150),

                radius=50,

                color=(255, 255, 0),

                width=2,

            )

        )

        #
        # Rectangle
        #

        frame.add(

            Rectangle(

                x=80,

                y=260,

                width=180,

                height=100,

                color=(0, 200, 255),

                filled=False,

            )

        )

        #
        # Text
        #

        frame.add(

            Text(

                text="RetroScope",

                position=(320, 320),

                color=(0, 255, 0),

                size=28,

            )

        )

    # ---------------------------------------------------------

    def shutdown(self):

        pass