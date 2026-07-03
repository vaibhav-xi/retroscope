"""
RetroScope

Application Entry Point

This file should remain as small as possible.
Its only responsibility is to start the engine.
"""

from core.app import App


def main() -> None:
    """
    Application entry point.
    """

    app = App()

    app.run()


if __name__ == "__main__":
    main()