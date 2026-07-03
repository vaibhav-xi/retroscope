import pygame

import grid
from waveform import Waveform

WIDTH = 800
HEIGHT = 480

BACKGROUND = (2, 5, 2)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RetroScope")

clock = pygame.time.Clock()

wave = Waveform()

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

    wave.update()

    screen.fill(BACKGROUND)

    grid.draw(screen, WIDTH, HEIGHT)

    wave.draw(screen, WIDTH, HEIGHT)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
