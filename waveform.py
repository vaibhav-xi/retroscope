import math
import pygame


TRACE = (80, 255, 120)


class Waveform:

    def __init__(self):
        self.phase = 0.0

    def update(self):
        self.phase += 0.05

    def draw(self, screen, width, height):

        points = []

        amplitude = height * 0.30

        center_y = height // 2

        for x in range(width):

            angle = (x / width) * math.pi * 4 + self.phase

            y = center_y + math.sin(angle) * amplitude

            points.append((x, int(y)))

        pygame.draw.aalines(
            screen,
            TRACE,
            False,
            points,
        )
