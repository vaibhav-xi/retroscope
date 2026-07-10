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

    if status:
        print(status)

    samples = indata[:, 0]

    rms = np.sqrt(
        np.mean(samples * samples)
    )

    level = rms


#
# Capture.
#

with sd.InputStream(

    device=device,

    samplerate=44100,

    channels=1,

    callback=callback,

):

    while True:

        bars = int(level * 120)

        print(
            "\r"
            + "█" * bars
            + " " * (120 - bars)
            + f" {level:.4f}",
            end="",
            flush=True,
        )

        time.sleep(0.03)