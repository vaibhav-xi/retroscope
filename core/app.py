"""
RetroScope

Application

Owns the engine lifecycle.

Pipeline

Context
    ↓
Manager
    ↓
Frame
    ↓
Renderer
"""

import config

from core.context import Context
from core.frame import Frame
from core.manager import Manager

from render.renderer import Renderer

from modules.demo.demo import DemoModule

class App:

    def __init__(self):

        #
        # Shared engine state
        #

        self.context = Context()

        #
        # Module manager
        #

        self.manager = Manager()

        #
        # Render frame
        #

        self.frame = Frame()

        #
        # Renderer
        #

        self.renderer = Renderer()

    # ---------------------------------------------------------

    def initialize(self):

        self.manager.register(
            DemoModule()
        )

        self.manager.initialize(
            self.context
        )

    # ---------------------------------------------------------

    def update(self):

        #
        # Timing
        #

        self.context.update()

        #
        # Simulations
        #

        self.manager.update(
            self.context
        )

        #
        # Build render frame
        #

        self.frame.clear()

        self.manager.emit(
            self.frame
        )

    # ---------------------------------------------------------

    def draw(self):

        #
        # Begin frame
        #

        self.renderer.begin_frame()

        #
        # Render
        #

        self.renderer.render(
            self.frame
        )

        #
        # Present
        #

        fps = self.renderer.end_frame()

        self.context.set_fps(fps)

    # ---------------------------------------------------------

    def shutdown(self):

        self.manager.shutdown()

        self.renderer.shutdown()

    # ---------------------------------------------------------

    def run(self):

        self.initialize()

        running = True

        while running:

            #
            # Handle window events
            #

            import pygame

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    running = False

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:

                        running = False

            #
            # Engine
            #

            self.update()

            #
            # Renderer
            #

            self.draw()

        self.shutdown()