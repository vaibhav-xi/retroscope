from _native import build

verts = build(
    [(0.0, 0.0), (100.0, 0.0)],
    2.0,
)

print(len(verts))
print(verts)