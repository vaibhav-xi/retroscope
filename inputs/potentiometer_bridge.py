"""
    RetroScope - potentiometer bridge (Arduino Nano over USB serial).

    Reads up to 7 potentiometers streamed by an Arduino Nano (see
    inputs/arduino/potentiometer_bridge/potentiometer_bridge.ino) and
    writes their values into whichever tuning.json + key each channel is
    mapped to in pot_mapping.json. Works with any module that already
    polls a tuning.json

"""

import json
import pathlib
import time

try:

    import serial
    from serial.tools import list_ports

except ImportError:

    serial = None
    list_ports = None

_HERE = pathlib.Path(__file__).parent
_MAPPING_FILE = _HERE / "pot_mapping.json"

_BAUD_RATE = 115200
_SMOOTHING = 0.2    # EMA factor - higher = more responsive, jitterier.

# Common Arduino Nano USB-serial chip vendor IDs, used for
# auto-detecting the port instead of hardcoding /dev/ttyUSB0 or a
# COM port. Set PORT explicitly below if auto-detect picks wrong.
_KNOWN_VIDS = {0x1A86, 0x0403, 0x2341, 0x10C4}

PORT = None  # e.g. "/dev/ttyACM0" or "COM5" - None = auto-detect

# Regenerated on first run if pot_mapping.json doesn't exist yet -
# edit that file to reassign any channel to any control.
_DEFAULT_MAPPING = {
    "connected_channels": 7,
    "channels": {
        "0": {"file": "modules/audioreactive/mode7/tuning.json", "key": "wave_hue", "min": 0.0, "max": 360.0},
        "1": {"file": "modules/audioreactive/mode7/tuning.json", "key": "liss_hue", "min": 0.0, "max": 360.0},
        "2": {"file": "modules/audioreactive/mode7/tuning.json", "key": "band_glow", "min": 0.5, "max": 3.0},
        "3": {"file": "modules/audioreactive/mode8/tuning.json", "key": "wave_hue", "min": 0.0, "max": 360.0},
        "4": {"file": "modules/audioreactive/mode8/tuning.json", "key": "vocal_hue", "min": 0.0, "max": 360.0},
        "5": {"file": "modules/audioreactive/mode10/tuning.json", "key": "rose_hue", "min": 0.0, "max": 360.0},
        "6": {"file": "modules/audioreactive/mode10/tuning.json", "key": "spin_speed", "min": 0.0, "max": 3.0},
    },
}


def _load_mapping():

    if _MAPPING_FILE.exists():

        try:

            return json.loads(_MAPPING_FILE.read_text())

        except (ValueError, OSError):

            pass

    _MAPPING_FILE.write_text(json.dumps(_DEFAULT_MAPPING, indent=4))

    return dict(_DEFAULT_MAPPING)


def _find_port():

    if PORT is not None:

        return PORT

    for port in list_ports.comports():

        if port.vid in _KNOWN_VIDS:

            return port.device

    return None


def main():

    mapping = _load_mapping()

    connected = int(mapping.get("connected_channels", 0))

    channels = mapping.get("channels", {})

    port = _find_port()

    if port is None:

        raise RuntimeError(
            "no Arduino found on any serial port - plug it in, or "
            "set PORT explicitly at the top of this file"
        )

    print(f"[PotBridge] connecting to {port} @ {_BAUD_RATE}, {connected} pot(s) expected")

    link = serial.Serial(port, _BAUD_RATE, timeout=1)

    time.sleep(2.0)
    link.reset_input_buffer()

    smoothed = {}

    project_root = _HERE.parent

    try:

        while True:

            line = link.readline().decode("ascii", errors="ignore").strip()

            if not line:

                continue

            try:

                raw_values = [int(v) for v in line.split(",")]

            except ValueError:

                continue

            files_touched = {}

            for channel in range(min(connected, len(raw_values))):

                target = channels.get(str(channel))

                if target is None:

                    continue

                raw = max(0.0, min(1.0, raw_values[channel] / 1023.0))

                previous = smoothed.get(channel, raw)

                value = previous + (raw - previous) * _SMOOTHING

                smoothed[channel] = value

                mapped = target["min"] + value * (target["max"] - target["min"])

                path = project_root / target["file"]

                if path not in files_touched:

                    files_touched[path] = (
                        json.loads(path.read_text()) if path.exists() else {}
                    )

                files_touched[path][target["key"]] = mapped

            for path, values in files_touched.items():

                path.write_text(json.dumps(values))

    except KeyboardInterrupt:

        pass

    finally:

        link.close()


if __name__ == "__main__":

    main()
