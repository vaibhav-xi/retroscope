from . import build
from render_es2.vertex_buffer import VertexBuffer

vb = VertexBuffer()

build(
    [(0.0, 0.0), (100.0, 0.0)],
    2.0,
    vb,
)

print(vb.count)
print(vb.vertices[:vb.count])