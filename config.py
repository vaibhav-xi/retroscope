"""
RetroScope Configuration
Every visual parameter lives here.
"""

# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

WIDTH = 800
HEIGHT = 480
FPS = 60

FULLSCREEN = False

# ---------------------------------------------------------
# Colors
# ---------------------------------------------------------

BACKGROUND = (2, 5, 2)

GRID = (0, 28, 8)
GRID_CENTER = (0, 55, 18)

TRACE_CORE = (220, 255, 220)
TRACE_MAIN = (60, 255, 120)
TRACE_GLOW = (0, 160, 60)

TEXT = (0, 210, 70)

# ---------------------------------------------------------
# Grid
# ---------------------------------------------------------

GRID_COLUMNS = 10
GRID_ROWS = 8

DRAW_MINOR_TICKS = True
MINOR_TICKS = 5

# ---------------------------------------------------------
# Waveform
# ---------------------------------------------------------

DEFAULT_WAVEFORM = "sine"

AMPLITUDE = 0.30
FREQUENCY = 2.0
SPEED = 0.05

TRACE_WIDTH = 3
GLOW_WIDTH = 7

# ---------------------------------------------------------
# CRT Effects
# ---------------------------------------------------------

ENABLE_GLOW = True
ENABLE_SCANLINES = True
ENABLE_PERSISTENCE = True
ENABLE_VIGNETTE = True
ENABLE_NOISE = True

PERSISTENCE_ALPHA = 18
SCANLINE_ALPHA = 24

NOISE_PIXELS = 120

# ---------------------------------------------------------
# Boot
# ---------------------------------------------------------

BOOT_DURATION = 2.0

# ---------------------------------------------------------
# Networking
# ---------------------------------------------------------

WEB_PORT = 5000

AP_SSID = "RetroScope"

AP_PASSWORD = "oscilloscope"

# ---------------------------------------------------------
# Oscilloscope UI
# ---------------------------------------------------------

TIME_DIV = "1 ms/div"

VOLT_DIV = "500 mV/div"

CHANNEL = "CH1"

MODE = "AUTO"

TRIGGER = "EDGE"

# ---------------------------------------------------------
# Runtime state
# (Modified by the web server)
# ---------------------------------------------------------

runtime = {

    "waveform": DEFAULT_WAVEFORM,

    "frequency": FREQUENCY,

    "amplitude": AMPLITUDE,

    "speed": SPEED,

    "freeze": False,

    "grid": True,

    "glow": ENABLE_GLOW,

    "scanlines": ENABLE_SCANLINES,

    "persistence": ENABLE_PERSISTENCE,

    "noise": ENABLE_NOISE,

    "vignette": ENABLE_VIGNETTE,

}
