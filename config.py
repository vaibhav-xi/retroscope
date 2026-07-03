"""
RetroScope

Global Configuration

This file contains immutable configuration values.

Nothing in this file should change while the engine is
running. Runtime state belongs in Context.
"""

# ==========================================================
# Application
# ==========================================================

APP_NAME = "RetroScope"

VERSION = "1.0.0"

# ==========================================================
# Display
# ==========================================================

WIDTH = 800

HEIGHT = 480

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
# Networking
# ==========================================================

WEB_PORT = 5000