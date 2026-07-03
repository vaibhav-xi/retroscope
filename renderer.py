"""
RetroScope v0.2
Renderer
"""

import pygame

import config
import grid

from waveform import Waveform
from beam import BeamRenderer
from crt import CRT
from input import InputManager


class Renderer:

    def __init__(self):

        pygame.init()

        flags = pygame.FULLSCREEN if config.FULLSCREEN else 0

        self.screen = pygame.display.set_mode(
            (config.WIDTH, config.HEIGHT),
            flags,
        )

        pygame.display.set_caption("RetroScope")

        self.clock = pygame.time.Clock()

        self.running = True

        #
        # Static grid
        #

        self.grid = pygame.Surface(
            (config.WIDTH, config.HEIGHT)
        ).convert()

        self.grid.fill(config.BACKGROUND)

        grid.draw(
            self.grid,
            config.WIDTH,
            config.HEIGHT,
        )

        #
        # Engine
        #

        self.wave = Waveform()

        self.beam = BeamRenderer()

        self.crt = CRT()

        self.input = InputManager()

        self.font = pygame.font.SysFont(
            "Courier New",
            18,
            bold=True,
        )

    # ----------------------------------------------------

    def events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.running = False

                else:

                    self.input.handle_key(event)

    # ----------------------------------------------------

    def overlay(self):

        left = (
            f"{config.CHANNEL}   "
            f"{config.MODE}   "
            f"{config.TRIGGER}"
        )

        right = (
            f"{config.TIME_DIV}   "
            f"{config.VOLT_DIV}"
        )

        t1 = self.font.render(
            left,
            True,
            config.TEXT,
        )

        t2 = self.font.render(
            right,
            True,
            config.TEXT,
        )

        self.screen.blit(
            t1,
            (15, 10),
        )

        self.screen.blit(
            t2,
            (430, 10),
        )

    # ----------------------------------------------------

    def draw(self):

        #
        # Update waveform
        #

        if not config.runtime["freeze"]:

            self.wave.update()

        #
        # Fresh beam
        #

        beam_surface = self.beam.draw(
            self.wave.samples
        )

        #
        # CRT
        #

        self.crt.update(
            beam_surface
        )

        #
        # Begin frame
        #

        self.screen.blit(
            self.grid,
            (0, 0),
        )

        #
        # CRT rendering
        #

        self.crt.render(
            self.screen
        )

        #
        # Overlay
        #

        self.overlay()

        pygame.display.flip()

    # ----------------------------------------------------

    def run(self):

        while self.running:

            self.events()

            self.draw()

            self.clock.tick(
                config.FPS
            )

        pygame.quit()
