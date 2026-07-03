"""
Waveform Generator
"""

import math
import random
import pygame

import config


class Waveform:

    def __init__(self):

        self.phase = 0.0

    # -----------------------------------------------------

    def update(self):

        self.phase += config.runtime["speed"]

    # -----------------------------------------------------

    def sample(self, t):

        wave = config.runtime["waveform"]

        #
        # Sine
        #

        if wave == "sine":

            return math.sin(
                t * math.pi * 2 * config.runtime["frequency"]
                + self.phase
            )

        #
        # Square
        #

        elif wave == "square":

            s = math.sin(
                t * math.pi * 2 * config.runtime["frequency"]
                + self.phase
            )

            return 1 if s >= 0 else -1

        #
        # Triangle
        #

        elif wave == "triangle":

            x = (
                t * config.runtime["frequency"]
                + self.phase
            )

            x = x % 1.0

            return 4 * abs(x - 0.5) - 1

        #
        # Sawtooth
        #

        elif wave == "saw":

            x = (
                t * config.runtime["frequency"]
                + self.phase
            )

            x = x % 1.0

            return (x * 2) - 1

        #
        # Noise
        #

        elif wave == "noise":

            return random.uniform(-1, 1)

        #
        # Flat line
        #

        return 0

    # -----------------------------------------------------

    def draw(
        self,
        surface,
        width,
        height,
    ):

        points = []

        center = height // 2

        amplitude = (
            height
            * config.runtime["amplitude"]
        )

        for x in range(width):

            t = x / width

            y = self.sample(t)

            py = center + y * amplitude

            points.append(
                (x, int(py))
            )

        #
        # Thick glow beam
        #

        pygame.draw.lines(
            surface,
            config.TRACE_GLOW,
            False,
            points,
            config.GLOW_WIDTH,
        )

        #
        # Main beam
        #

        pygame.draw.lines(
            surface,
            config.TRACE_MAIN,
            False,
            points,
            config.TRACE_WIDTH,
        )

        #
        # Bright phosphor core
        #

        pygame.draw.aalines(
            surface,
            config.TRACE_CORE,
            False,
            points,
        )
