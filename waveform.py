"""
RetroScope v0.2
Wave Engine
"""

import math
import random
from collections import deque

import pygame

import config


class Waveform:

    def __init__(self):

        #
        # Rolling sample buffer
        #

        self.samples = deque(
            [0.0] * config.WIDTH,
            maxlen=config.WIDTH,
        )

        self.time = 0.0

    # ----------------------------------------------------

    def signal(self, t):

        wave = config.runtime["waveform"]

        freq = config.runtime["frequency"]

        if wave == "sine":

            return math.sin(
                t * math.pi * 2 * freq
            )

        elif wave == "square":

            return (
                1
                if math.sin(
                    t * math.pi * 2 * freq
                ) >= 0
                else -1
            )

        elif wave == "triangle":

            x = (t * freq) % 1.0

            return 4 * abs(x - 0.5) - 1

        elif wave == "saw":

            x = (t * freq) % 1.0

            return (x * 2) - 1

        elif wave == "noise":

            return random.uniform(-1, 1)

        return 0

    # ----------------------------------------------------

    def update(self):

        #
        # Time advances continuously
        #

        self.time += config.runtime["speed"] * 0.01

        value = self.signal(self.time)

        self.samples.append(value)

    # ----------------------------------------------------

    def draw(self, surface, width, height):

        centre = height // 2

        amplitude = (
            config.runtime["amplitude"]
            * height
            * 0.40
        )

        points = []

        for x, sample in enumerate(self.samples):

            y = int(
                centre
                - sample * amplitude
            )

            points.append((x, y))

        #
        # Outer glow
        #

        pygame.draw.lines(
            surface,
            config.TRACE_GLOW,
            False,
            points,
            config.GLOW_WIDTH + 4,
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
        # Bright phosphor
        #

        pygame.draw.aalines(
            surface,
            config.TRACE_CORE,
            False,
            points,
        )
