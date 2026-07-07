from setuptools import Extension
from setuptools import setup

import numpy

module = Extension(

    "_native",

    sources=[
        "wrapper.c",
        "stroke.c",
        "geometry.c",
        "vertex_buffer.c",
    ],

    include_dirs=[
        numpy.get_include(),
    ],

)

setup(

    name="_native",

    version="1.0",

    ext_modules=[module],

)