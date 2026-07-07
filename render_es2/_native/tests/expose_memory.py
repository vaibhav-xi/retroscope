from render_es2._native import VertexBuffer

vb = VertexBuffer()

vb.reserve(8)

vb.count = 8

a = vb.data()

print(type(a))
print(a.dtype)
print(a.shape)