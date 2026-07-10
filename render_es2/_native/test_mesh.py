from render_es2._native import Mesh
import gc

print("creating")
m = Mesh()

print("calling create")
m.create()

print("calling test")
m.test()

print("deleting")
del m

# Force tp_dealloc to run.
gc.collect()

print("done")