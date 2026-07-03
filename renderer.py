"""
RetroScope Rendering Engine
"""

import random
import pygame

import config
import grid
from waveform import Waveform
import crt
from input import InputManager

class Renderer:

    def __init__(self):

        pygame.init()

        flags = 0

        if config.FULLSCREEN:
            flags = pygame.FULLSCREEN

        self.screen = pygame.display.set_mode(
            (config.WIDTH, config.HEIGHT),
            flags
        )

        pygame.display.set_caption("RetroScope")

        self.clock = pygame.time.Clock()

        self.running = True

        #
        # Rendering layers
        #

        self.grid_surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT)
        ).convert()

        self.trace_surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA
        ).convert_alpha()

        self.glow_surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA
        ).convert_alpha()

        self.effect_surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA
        ).convert_alpha()

        #
        # Draw static grid once
        #

        self.grid_surface.fill(config.BACKGROUND)

        grid.draw(
            self.grid_surface,
            config.WIDTH,
            config.HEIGHT,
        )

        #
        # Wave generator
        #

        self.wave = Waveform()

        self.input = InputManager()

        #
        # Fonts
        #

        self.font = pygame.font.SysFont(
            "Courier New",
            18,
            bold=True,
        )

    # -----------------------------------------------------

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self.input.handle_key(event)

    # -----------------------------------------------------

    def update(self):

        if not config.runtime["freeze"]:
            self.wave.update()

    # -----------------------------------------------------

    def draw(self):

        #
        # Persistence
        #

        if config.runtime["persistence"]:

            fade = pygame.Surface(
                (config.WIDTH, config.HEIGHT)
            )

            fade.fill((0, 0, 0))

            fade.set_alpha(config.PERSISTENCE_ALPHA)

            self.trace_surface.blit(
                fade,
                (0, 0),
            )

        else:

            self.trace_surface.fill((0, 0, 0, 0))

        #
        # Draw waveform
        #

        self.wave.draw(
            self.trace_surface,
            config.WIDTH,
            config.HEIGHT,
        )

        #
        # Glow layer
        #

        self.glow_surface.fill((0, 0, 0, 0))

        if config.runtime["glow"]:

            crt.draw_glow(
                self.trace_surface,
                self.glow_surface,
            )

        #
        # Compose final frame
        #

        self.screen.blit(
            self.grid_surface,
            (0, 0),
        )

        self.screen.blit(
            self.glow_surface,
            (0, 0),
            special_flags=pygame.BLEND_ADD,
        )

        self.screen.blit(
            self.trace_surface,
            (0, 0),
        )

        #
        # Effects
        #

        self.effect_surface.fill((0, 0, 0, 0))

        if config.runtime["scanlines"]:
            crt.draw_scanlines(
                self.effect_surface
            )

        if config.runtime["noise"]:
            crt.draw_noise(
                self.effect_surface
            )

        if config.runtime["vignette"]:
            crt.draw_vignette(
                self.effect_surface
            )

        self.screen.blit(
            self.effect_surface,
            (0, 0),
        )

        #
        # Status text
        #

        self.draw_overlay()

        pygame.display.flip()

        self.clock.tick(config.FPS)

    # -----------------------------------------------------

    def draw_overlay(self):

        left = f"{config.CHANNEL}   {config.MODE}   {config.TRIGGER}"

        right = f"{config.TIME_DIV}   {config.VOLT_DIV}"

        text1 = self.font.render(
            left,
            True,
            config.TEXT,
        )

        text2 = self.font.render(
            right,
            True,
            config.TEXT,
        )

        self.screen.blit(
            text1,
            (15, 12),
        )

        self.screen.blit(
            text2,
            (430, 12),
        )

    # -----------------------------------------------------

    def run(self):

        while self.running:

            self.handle_events()

            self.update()

            self.draw()

        pygame.quit()
