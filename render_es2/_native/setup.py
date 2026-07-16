from setuptools import Extension, setup

import numpy
import platform

sources = [
    "geometry.c",
    "stroke.c",
    "vertex_buffer_object.c",
    "wrapper.c",
    "mesh_object.c",
    "shader_object.c",
    "gl_platform.c",
]

libraries = []

system = platform.system()

if system == "Linux":

    libraries = [
        "GLESv2",
        "EGL",
    ]

elif system == "Windows":

    libraries = [
        "opengl32",
    ]

module = Extension(
    "_native",
    sources=sources,
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
