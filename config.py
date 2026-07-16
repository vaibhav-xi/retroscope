"""
RetroScope

Global Configuration

This file contains immutable configuration values.

Nothing in this file should change while the engine is
running. Runtime state belongs in Context.
"""

import platform

_IS_LINUX = platform.system() == "Linux"

# ==========================================================
# Application
# ==========================================================

APP_NAME = "RetroScope"

VERSION = "1.0.0"

# ==========================================================
# Display
# ==========================================================

WIDTH = 1920

HEIGHT = 1080

FPS = 60

FULLSCREEN = False

WINDOW_TITLE = "RetroScope"

# ==========================================================
# Theme
# ==========================================================

DEFAULT_THEME = "oscilloscope"

# ==========================================================
# Debug
# ==========================================================

SHOW_FPS = True

SHOW_DEBUG = False

# ==========================================================
# Paths
# ==========================================================

ASSETS_DIR = "assets"

PLUGINS_DIR = "plugins"

# ==========================================================
# Audio Input
# ==========================================================

AUDIO_DEVICE = "retroscope_sink.monitor" if _IS_LINUX else None  # None = system default input device

AUDIO_SAMPLE_RATE = 48000 if _IS_LINUX else 44100

AUDIO_BLOCK_SIZE = 1024

# ==========================================================
# Networking
# ==========================================================

WEB_PORT = 5000