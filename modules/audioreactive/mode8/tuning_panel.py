import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))

from inputs.tuning_ui import run

_STATE_FILE = pathlib.Path(__file__).parent / "tuning.json"

DEFAULTS = {
    "wave_hue": 0.0,
    "vocal_hue": 0.0,
}

RANGES = {
    "wave_hue": (0.0, 360.0),
    "vocal_hue": (0.0, 360.0),
}

if __name__ == "__main__":

    run("Mode 8 Tuning", _STATE_FILE, DEFAULTS, RANGES)
