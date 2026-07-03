"""
Oscilloscope Graticule
"""

import pygame
import config


def draw(screen, width, height):

    cols = config.GRID_COLUMNS
    rows = config.GRID_ROWS

    sx = width / cols
    sy = height / rows

    #
    # Border
    #

    pygame.draw.rect(
        screen,
        config.GRID_CENTER,
        pygame.Rect(0, 0, width - 1, height - 1),
        2,
    )

    #
    # Vertical divisions
    #

    for c in range(cols + 1):

        x = int(c * sx)

        color = (
            config.GRID_CENTER
            if c == cols // 2
            else config.GRID
        )

        pygame.draw.line(
            screen,
            color,
            (x, 0),
            (x, height),
            1,
        )

        #
        # Minor ticks
        #

        if config.DRAW_MINOR_TICKS:

            for r in range(rows):

                y0 = int(r * sy)

                tick = sy / config.MINOR_TICKS

                for i in range(1, config.MINOR_TICKS):

                    yy = int(y0 + i * tick)

                    pygame.draw.line(
                        screen,
                        color,
                        (x - 4, yy),
                        (x + 4, yy),
                        1,
                    )

    #
    # Horizontal divisions
    #

    for r in range(rows + 1):

        y = int(r * sy)

        color = (
            config.GRID_CENTER
            if r == rows // 2
            else config.GRID
        )

        pygame.draw.line(
            screen,
            color,
            (0, y),
            (width, y),
            1,
        )

        #
        # Minor ticks
        #

        if config.DRAW_MINOR_TICKS:

            for c in range(cols):

                x0 = int(c * sx)

                tick = sx / config.MINOR_TICKS

                for i in range(1, config.MINOR_TICKS):

                    xx = int(x0 + i * tick)

                    pygame.draw.line(
                        screen,
                        color,
                        (xx, y - 4),
                        (xx, y + 4),
                        1,
                    )

    #
    # Center reference cross
    #

    cx = width // 2
    cy = height // 2

    pygame.draw.line(
        screen,
        config.GRID_CENTER,
        (cx - 12, cy),
        (cx + 12, cy),
        2,
    )

    pygame.draw.line(
        screen,
        config.GRID_CENTER,
        (cx, cy - 12),
        (cx, cy + 12),
        2,
    )
