"""
RetroScope
Main Entry
"""

from renderer import Renderer
from network import start as start_web


def main():

    #
    # Start Flask server
    #

    start_web()

    #
    # Start renderer
    #

    renderer = Renderer()

    renderer.run()


if __name__ == "__main__":
    main()
