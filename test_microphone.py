import time

import numpy as np
import sounddevice as sd

#
# Pick a device.
#

print("Input devices:\n")

devices = sd.query_devices()

for i, device in enumerate(devices):

    if device["max_input_channels"] > 0:

        print(
            f"{i:2d}: {device['name']}"
        )

print()

device = int(
    input("Input device: ")
)

print()

#
# Audio callback.
#

level = 0.0


def callback(indata, frames, time_info, status):

    global level

    # Ignore occasional status messages so the
    # terminal stays on one line.

    samples = indata[:, 0]

    rms = np.sqrt(
        np.mean(samples * samples)
    )

    # Smooth the meter slightly.
    level = (
        level * 0.8
        + rms * 0.2
    )


#
# Capture.
#

WIDTH = 60

peak = 0.0

with sd.InputStream(

    device=device,

    samplerate=44100,

    channels=1,

    callback=callback,

):

    while True:

        meter = min(
            level * 200,
            1.0
        )

        peak = max(
            peak * 0.97,
            meter
        )

        bar = [" "] * WIDTH

        for i in range(
            int(meter * WIDTH)
        ):
            bar[i] = "█"

        peak_pos = min(
            int(peak * WIDTH),
            WIDTH - 1
        )

        bar[peak_pos] = "│"

        print(
            "\r["
            + "".join(bar)
            + "] "
            + f"{level:.4f}",
            end="",
            flush=True,
        )

        time.sleep(0.03)

print()