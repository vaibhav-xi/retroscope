from render_es2._native import VertexBuffer

vb = VertexBuffer()

vb.reserve(16)

print(vb.vertices)
print(vb.vertices.shape)

vb.count = 5

print(vb.vertices)
print(vb.vertices.shape)

vb.clear()

print(vb.count)