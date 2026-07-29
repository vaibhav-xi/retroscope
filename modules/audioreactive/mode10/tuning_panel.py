import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from inputs.tuning_ui import run

_STATE_FILE = pathlib.Path(__file__).parent / "tuning.json"

DEFAULTS = {
    "rose_hue": 0.0,
    "spin_speed": 1.0,
}

RANGES = {
    "rose_hue": (0.0, 360.0),
    "spin_speed": (0.0, 3.0),
}

if __name__ == "__main__":

    run("Mode 10 Tuning", _STATE_FILE, DEFAULTS, RANGES)
