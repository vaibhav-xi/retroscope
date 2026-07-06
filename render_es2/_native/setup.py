from setuptools import Extension
from setuptools import setup

module = Extension(

    "_native",

    sources=[

        "wrapper.c",

        "stroke.c",

        "geometry.c",

    ],

)

setup(

    name="_native",

    version="1.0",

    ext_modules=[module],

)