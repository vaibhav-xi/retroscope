from setuptools import Extension, setup

import numpy

module = Extension(
    "_native",
    sources=[
        "ember_field.c",
        "spectrum_ring.c",
        "wrapper.c",
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
