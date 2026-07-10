from setuptools import Extension, setup

import numpy
import platform

libraries = []

if platform.system() == "Linux":
    libraries = [
        "GLESv2",
        "EGL",
    ]

module = Extension(
    "_native",
    sources=[
        "geometry.c",
        "stroke.c",
        "vertex_buffer_object.c",
        "wrapper.c",
        "mesh_object.c",
        "shader_object.c",
    ],
    include_dirs=[
        numpy.get_include(),
    ],
    libraries=libraries,
)

setup(
    name="_native",
    version="1.0",
    ext_modules=[module],
)