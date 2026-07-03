import pygame

GRID = (0, 35, 10)
CENTER = (0, 120, 45)


def draw(screen, width, height):

    div_x = 10
    div_y = 8

    spacing_x = width / div_x
    spacing_y = height / div_y

    for i in range(div_x + 1):

        x = int(i * spacing_x)

        color = CENTER if i == div_x // 2 else GRID

        pygame.draw.line(
            screen,
            color,
            (x, 0),
            (x, height),
            1,
        )

    for i in range(div_y + 1):

        y = int(i * spacing_y)

        color = CENTER if i == div_y // 2 else GRID

        pygame.draw.line(
            screen,
            color,
            (0, y),
            (width, y),
            1,
        )
