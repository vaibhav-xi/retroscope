"""
RetroScope Rendering Engine
"""

import pygame

import config
import grid
import crt

from waveform import Waveform
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
        # Layers
        #

        self.grid_surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT)
        ).convert()

        self.trace_surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        ).convert_alpha()

        self.glow_surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        ).convert_alpha()

        self.effect_surface = pygame.Surface(
            (config.WIDTH, config.HEIGHT),
            pygame.SRCALPHA,
        ).convert_alpha()

        #
        # Static grid
        #

        self.grid_surface.fill(config.BACKGROUND)

        grid.draw(
            self.grid_surface,
            config.WIDTH,
            config.HEIGHT,
        )

        #
        # Waveform
        #

        self.wave = Waveform()

        #
        # Input
        #

        self.input = InputManager()

        #
        # Font
        #

        self.font = pygame.font.SysFont(
            "Courier New",
            18,
            bold=True,
        )

    # ----------------------------------------------------

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.running = False

                else:

                    self.input.handle_key(event)

    # ----------------------------------------------------

    def update(self):

        if not config.runtime["freeze"]:

            self.wave.update()

    # ----------------------------------------------------

    def draw(self):

        #
        # ALWAYS CLEAR TRACE
        #
        # Persistence will be implemented later using
        # a proper phosphor buffer.
        #

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
        # Glow
        #

        self.glow_surface.fill((0, 0, 0, 0))

        if config.runtime["glow"]:

            crt.draw_glow(
                self.trace_surface,
                self.glow_surface,
            )

        #
        # Begin frame
        #

        self.screen.blit(
            self.grid_surface,
            (0, 0),
        )

        #
        # Glow first
        #

        self.screen.blit(
            self.glow_surface,
            (0, 0),
            special_flags=pygame.BLEND_ADD,
        )

        #
        # Main trace
        #

        self.screen.blit(
            self.trace_surface,
            (0, 0),
        )

        #
        # Overlay effects
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
        # UI
        #

        self.draw_overlay()

        pygame.display.flip()

        self.clock.tick(config.FPS)

    # ----------------------------------------------------

    def draw_overlay(self):

        left = (
            f"{config.CHANNEL}   "
            f"{config.MODE}   "
            f"{config.TRIGGER}"
        )

        right = (
            f"{config.TIME_DIV}   "
            f"{config.VOLT_DIV}"
        )

        text_left = self.font.render(
            left,
            True,
            config.TEXT,
        )

        text_right = self.font.render(
            right,
            True,
            config.TEXT,
        )

        self.screen.blit(
            text_left,
            (15, 12),
        )

        self.screen.blit(
            text_right,
            (430, 12),
        )

    # ----------------------------------------------------

    def run(self):

        while self.running:

            self.handle_events()

            self.update()

            self.draw()

        pygame.quit()
