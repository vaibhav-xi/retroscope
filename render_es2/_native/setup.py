from setuptools import Extension
from setuptools import setup

import numpy

import platform

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
        "gl_upload.c",
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