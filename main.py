import pygame

import grid

WIDTH = 800
HEIGHT = 480

BACKGROUND = (3, 8, 3)

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill(BACKGROUND)

    grid.draw(screen, WIDTH, HEIGHT)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
