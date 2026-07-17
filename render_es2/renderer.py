from pathlib import Path

import numpy as np

from OpenGL.GL import *

from render_es2.shader import Shader
from render_es2.geometry_builder import GeometryBuilder
from render_es2.render_graph import RenderGraph
from render_es2.passes.geometry import GeometryPass
from render_es2.profiler import Profiler
from render_es2.stroke_builder import StrokeBuilder
from render_es2.material import Material

from render.primitives import Polyline
from render.renderable import Renderable

from core.frame import Frame, Layer


class Renderer:

    def __init__(self):

        glClearColor(
            0.0,
            0.0,
            0.0,
            1.0,
        )

        # Start from a clean black frame - afterglow mode never
        # clears again after this, so the very first frame needs an
        # explicit clear instead of whatever garbage is in the
        # window's backbuffer at creation time.
        glClear(GL_COLOR_BUFFER_BIT)

        glEnable(GL_BLEND)

        shader_dir = (
            Path(__file__).parent
            / "shaders"
        )

        vertex = (
            shader_dir / "simple.vert"
        ).read_text()

        fragment = (
            shader_dir / "simple.frag"
        ).read_text()

        self.shader = Shader(
            vertex,
            fragment,
        )

        self.shader.use()

        self.profiler = Profiler()

        self.render_graph = RenderGraph()

        self.render_graph.add(

            GeometryPass(
                self.shader,
            )

        )

        # Reused every frame for the afterglow fade quad - see
        # _draw_fade_quad(). Left as None until first needed so
        # modes that never touch afterglow pay nothing extra.
        self._fade_renderable = None

    # ---------------------------------------------------------

    def render(self, frame, afterglow: float = 1.0):

        GeometryBuilder.profiler = self.profiler

        if afterglow >= 0.999:

            #
            # No persistence requested - identical to the old
            # behaviour, hard clear every frame.
            #

            glClear(GL_COLOR_BUFFER_BIT)

        else:

            #
            # Fade the existing framebuffer toward black instead of
            # clearing it - the software equivalent of CRT phosphor
            # decay. Old strokes dim out over several frames instead
            # of vanishing instantly or piling up at full brightness.
            #

            self._draw_fade_quad(afterglow)

        self.profiler.begin(
            "GeometryBuilder"
        )

        packet = GeometryBuilder.build(
            frame
        )

        self.profiler.end(
            "GeometryBuilder"
        )

        #
        # Execute render passes.
        #

        self.profiler.begin(
            "RenderGraph"
        )

        self.render_graph.execute(
            packet
        )

        self.profiler.end(
            "RenderGraph"
        )

    # ---------------------------------------------------------

    def _draw_fade_quad(self, afterglow: float):

        alpha = max(0.0, min(1.0, 1.0 - afterglow))

        if alpha <= 0.0:

            return

        width = StrokeBuilder.screen_width
        height = StrokeBuilder.screen_height

        if self._fade_renderable is None:

            self._fade_renderable = Renderable(is_dynamic=True)

        self._fade_renderable.clear()

        #
        # A single "line" as wide as the screen with half_width ==
        # half the screen height covers exactly one fullscreen
        # rectangle - reuses the existing stroke pipeline instead of
        # needing a new native fullscreen-quad primitive.
        #

        self._fade_renderable.material = Material(
            color=(0.0, 0.0, 0.0),
            alpha=alpha,
            line_width=height,
            additive=False,
        )

        self._fade_renderable.add(
            Polyline(
                points=np.array(
                    [[0.0, height * 0.5], [width, height * 0.5]],
                    dtype=np.float32,
                )
            )
        )

        fade_frame = Frame()

        fade_frame.add_renderable(self._fade_renderable, Layer.BACKGROUND)

        fade_packet = GeometryBuilder.build(fade_frame)

        self.render_graph.execute(fade_packet)
