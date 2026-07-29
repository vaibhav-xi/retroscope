"""
    RetroScope - reusable pygame slider panel.

    Shared by every mode's tuning_panel.py: draws one horizontal slider
    per tunable and writes the full set of values to a JSON state file
    on every change.
"""

import json
import pathlib

import pygame

_WIDTH = 460
_ROW_HEIGHT = 56
_TRACK_X = 20
_TRACK_WIDTH = 420
_HANDLE_RADIUS = 8

_BG = (18, 18, 18)
_TRACK_COLOR = (70, 70, 70)
_HANDLE_COLOR = (0, 255, 120)
_TEXT_COLOR = (220, 220, 220)


def _load_initial(state_file: pathlib.Path, defaults: dict):

    if state_file.exists():

        try:

            return {**defaults, **json.loads(state_file.read_text())}

        except (ValueError, OSError):

            pass

    return dict(defaults)


def _write(state_file: pathlib.Path, values: dict):

    try:

        state_file.write_text(json.dumps(values))

    except OSError:

        pass


def _value_to_x(value, lo, hi):

    t = (value - lo) / (hi - lo) if hi > lo else 0.0

    t = max(0.0, min(1.0, t))

    return _TRACK_X + int(t * _TRACK_WIDTH)


def _x_to_value(x, lo, hi):

    t = (x - _TRACK_X) / _TRACK_WIDTH

    t = max(0.0, min(1.0, t))

    return lo + t * (hi - lo)


def run(title: str, state_file: pathlib.Path, defaults: dict, ranges: dict):
    """
    Opens a window with one horizontal slider per key in `ranges`,
    writes the full `values` dict to `state_file` on every change.
    Blocks until the window is closed.
    """

    values = _load_initial(state_file, defaults)

    pygame.init()

    keys = list(ranges.keys())

    height = _ROW_HEIGHT * len(keys) + 20

    screen = pygame.display.set_mode((_WIDTH, height))

    pygame.display.set_caption(title)

    font = pygame.font.SysFont(None, 18)

    clock = pygame.time.Clock()

    dragging = None

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                row = event.pos[1] // _ROW_HEIGHT

                if 0 <= row < len(keys):

                    dragging = keys[row]

            elif event.type == pygame.MOUSEBUTTONUP:

                dragging = None

            elif event.type == pygame.MOUSEMOTION and dragging is not None:

                lo, hi = ranges[dragging]

                values[dragging] = _x_to_value(event.pos[0], lo, hi)

                _write(state_file, values)

        screen.fill(_BG)

        for i, key in enumerate(keys):

            lo, hi = ranges[key]

            row_y = i * _ROW_HEIGHT + 10

            label = font.render(f"{key}  {values[key]:.3f}", True, _TEXT_COLOR)

            screen.blit(label, (_TRACK_X, row_y))

            track_y = row_y + 22

            pygame.draw.line(
                screen, _TRACK_COLOR,
                (_TRACK_X, track_y), (_TRACK_X + _TRACK_WIDTH, track_y), 4,
            )

            handle_x = _value_to_x(values[key], lo, hi)

            pygame.draw.circle(screen, _HANDLE_COLOR, (handle_x, track_y), _HANDLE_RADIUS)

        pygame.display.flip()

        clock.tick(30)

    pygame.quit()
