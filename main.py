"""
RetroScope

Application Entry Point

This file should remain as small as possible.
Its only responsibility is to start the engine.
"""

import gc

from core.app import App

import sys


def main() -> None:
    """
    Application entry point.
    """

    gc.disable()
    
    sys.setswitchinterval(0.001)

    app = App()

    app.run()


if __name__ == "__main__":
    main()
