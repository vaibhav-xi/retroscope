"""
RetroScope Input Manager
"""

import pygame
import config


class InputManager:

    def __init__(self):

        pass

    # ----------------------------------------------------

    def handle_key(self, event):

        #
        # Freeze waveform
        #

        if event.key == pygame.K_SPACE:

            config.runtime["freeze"] = not config.runtime["freeze"]

        #
        # Waveforms
        #

        elif event.key == pygame.K_1:

            config.runtime["waveform"] = "sine"

        elif event.key == pygame.K_2:

            config.runtime["waveform"] = "square"

        elif event.key == pygame.K_3:

            config.runtime["waveform"] = "triangle"

        elif event.key == pygame.K_4:

            config.runtime["waveform"] = "saw"

        elif event.key == pygame.K_5:

            config.runtime["waveform"] = "noise"

        #
        # Increase frequency
        #

        elif event.key == pygame.K_UP:

            config.runtime["frequency"] += 0.25

        #
        # Decrease frequency
        #

        elif event.key == pygame.K_DOWN:

            config.runtime["frequency"] = max(
                0.25,
                config.runtime["frequency"] - 0.25,
            )

        #
        # Increase amplitude
        #

        elif event.key == pygame.K_RIGHT:

            config.runtime["amplitude"] = min(
                0.95,
                config.runtime["amplitude"] + 0.05,
            )

        #
        # Decrease amplitude
        #

        elif event.key == pygame.K_LEFT:

            config.runtime["amplitude"] = max(
                0.05,
                config.runtime["amplitude"] - 0.05,
            )

        #
        # Toggle effects
        #

        elif event.key == pygame.K_g:

            config.runtime["glow"] = not config.runtime["glow"]

        elif event.key == pygame.K_s:

            config.runtime["scanlines"] = not config.runtime["scanlines"]

        elif event.key == pygame.K_p:

            config.runtime["persistence"] = not config.runtime["persistence"]

        elif event.key == pygame.K_n:

            config.runtime["noise"] = not config.runtime["noise"]

        elif event.key == pygame.K_v:

            config.runtime["vignette"] = not config.runtime["vignette"]

        #
        # Future GPIO toggle switch
        #

        elif event.key == pygame.K_w:

            print("WiFi/AP switch placeholder")

        #
        # Debug
        #

        elif event.key == pygame.K_d:

            print("----------------------------------")

            for key, value in config.runtime.items():

                print(f"{key:15}: {value}")

            print("----------------------------------")
