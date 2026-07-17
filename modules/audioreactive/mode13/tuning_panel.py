import json
import pathlib

import pygame

_HERE = pathlib.Path(__file__).parent
_STATE_FILE = _HERE / "tuning.json"

DEFAULTS = {
    "persistence_seconds": 0.02,
    "point_stride": 1.0,
    "blank_max_factor": 6.0,
    "blank_min_threshold": 4.0,
    "gain_release": 0.98,
    "gain_target": 0.9,
    "gain_floor": 0.05,
    "smoothing": 0.0,
    "line_width": 1.0,
}

RANGES = {
    "persistence_seconds": (0.002, 10),
    "point_stride": (1.0, 8.0),
    "blank_max_factor": (1.0, 20.0),
    "blank_min_threshold": (0.5, 30.0),
    "gain_release": (0.90, 0.999),
    "gain_target": (0.3, 1.0),
    "gain_floor": (0.01, 0.2),
    "smoothing": (0.0, 8.0),
    "line_width": (0.3, 4.0),
}

_WIDTH = 460
_ROW_HEIGHT = 56
_TRACK_X = 20
_TRACK_WIDTH = 420
_HANDLE_RADIUS = 8

_BG = (18, 18, 18)
_TRACK_COLOR = (70, 70, 70)
_HANDLE_COLOR = (0, 255, 120)
_TEXT_COLOR = (220, 220, 220)


def _load_initial():

    if _STATE_FILE.exists():

        try:

            return {**DEFAULTS, **json.loads(_STATE_FILE.read_text())}

        except (ValueError, OSError):

            pass

    return dict(DEFAULTS)


def _write(values):

    try:

        _STATE_FILE.write_text(json.dumps(values))

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


def main():

    values = _load_initial()

    pygame.init()

    keys = list(RANGES.keys())

    height = _ROW_HEIGHT * len(keys) + 20

    screen = pygame.display.set_mode((_WIDTH, height))

    pygame.display.set_caption("Mode 13 Tuning")

    font = pygame.font.SysFont(None, 18)

    clock = pygame.time.Clock()

    dragging = None

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = event.pos

                row = my // _ROW_HEIGHT

                if 0 <= row < len(keys):

                    dragging = keys[row]

            elif event.type == pygame.MOUSEBUTTONUP:

                dragging = None

            elif event.type == pygame.MOUSEMOTION and dragging is not None:

                lo, hi = RANGES[dragging]

                values[dragging] = _x_to_value(event.pos[0], lo, hi)

                _write(values)

        screen.fill(_BG)

        for i, key in enumerate(keys):

            lo, hi = RANGES[key]

            row_y = i * _ROW_HEIGHT + 10

            label = font.render(
                f"{key}  {values[key]:.3f}",
                True,
                _TEXT_COLOR,
            )

            screen.blit(label, (_TRACK_X, row_y))

            track_y = row_y + 22

            pygame.draw.line(
                screen,
                _TRACK_COLOR,
                (_TRACK_X, track_y),
                (_TRACK_X + _TRACK_WIDTH, track_y),
                4,
            )

            handle_x = _value_to_x(values[key], lo, hi)

            pygame.draw.circle(
                screen,
                _HANDLE_COLOR,
                (handle_x, track_y),
                _HANDLE_RADIUS,
            )

        pygame.display.flip()

        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":

    main()
