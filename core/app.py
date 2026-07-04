from render_es2.window import Window
from render_es2.renderer import Renderer

import config


class App:

    def __init__(self):

        self.window = Window(
            config.WIDTH,
            config.HEIGHT,
            config.WINDOW_TITLE,
        )

        self.renderer = Renderer()

    def run(self):

        while not self.window.should_close():

            self.window.poll()

            frame = self.manager.render()

            self.renderer.render(frame)

            self.window.swap()

        self.window.shutdown()