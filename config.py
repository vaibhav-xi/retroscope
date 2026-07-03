"""
RetroScope v0.2 Configuration
"""

# ==========================================================
# Display
# ==========================================================

WIDTH = 800
HEIGHT = 480

FPS = 60

FULLSCREEN = False

# ==========================================================
# Colors
# ==========================================================

BACKGROUND = (2, 5, 2)

GRID = (0, 35, 8)
GRID_CENTER = (0, 70, 18)

TRACE_CORE = (245, 255, 245)
TRACE_MAIN = (80, 255, 120)
TRACE_GLOW = (20, 180, 60)

TEXT = (0, 230, 90)

# ==========================================================
# Grid
# ==========================================================

GRID_COLUMNS = 10
GRID_ROWS = 8

DRAW_MINOR_TICKS = True
MINOR_TICKS = 5

# ==========================================================
# Beam
# ==========================================================

BEAM_CORE_WIDTH = 1

BEAM_WIDTH = 3

BEAM_GLOW_WIDTH = 7

BEAM_HALO_WIDTH = 11

# ==========================================================
# Waveform
# ==========================================================

DEFAULT_WAVEFORM = "sine"

AMPLITUDE = 0.30

FREQUENCY = 2.0

#
# Sampling speed
#

SPEED = 1.0

# ==========================================================
# CRT
# ==========================================================

ENABLE_GLOW = True

ENABLE_PERSISTENCE = True

ENABLE_SCANLINES = True

ENABLE_VIGNETTE = True

ENABLE_NOISE = True

#
# Lower value = longer trail
#

PERSISTENCE_ALPHA = 12

#
# Bloom strength
#

BLOOM_ALPHA = 90

#
# Scanlines
#

SCANLINE_ALPHA = 22

#
# Random phosphor speckles
#

NOISE_PIXELS = 60

# ==========================================================
# Oscilloscope UI
# ==========================================================

CHANNEL = "CH1"

MODE = "AUTO"

TRIGGER = "EDGE"

TIME_DIV = "1 ms/div"

VOLT_DIV = "500 mV/div"

# ==========================================================
# Network
# ==========================================================

WEB_PORT = 5000

AP_SSID = "RetroScope"

AP_PASSWORD = "oscilloscope"

# ==========================================================
# Runtime
# ==========================================================

runtime = {

    "waveform": DEFAULT_WAVEFORM,

    "frequency": FREQUENCY,

    "amplitude": AMPLITUDE,

    "speed": SPEED,

    "freeze": False,

    "grid": True,

    "glow": ENABLE_GLOW,

    "persistence": ENABLE_PERSISTENCE,

    "scanlines": ENABLE_SCANLINES,

    "noise": ENABLE_NOISE,

    "vignette": ENABLE_VIGNETTE,

}
