"""
RetroScope

Render Graph

Executes render passes in order.

Initially this contains only the GeometryPass.

Future passes:

- Glow
- Blur
- Feedback
- CRT
- Composite
"""

class RenderGraph:

    def __init__(self):

        self.passes = []

    # ---------------------------------------------------------

    def add(self, render_pass):

        self.passes.append(
            render_pass
        )

    # ---------------------------------------------------------

    def execute(self, packet):

        for render_pass in self.passes:

            render_pass.execute(
                packet
            )