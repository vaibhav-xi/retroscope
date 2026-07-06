from setuptools import Extension, setup

module = Extension(
    "render_es2._stroke_builder",
    sources=[
        "render_es2/_stroke_builder.c",
    ],
)

setup(
    name="retroscope_native",
    version="0.1",
    ext_modules=[module],
)