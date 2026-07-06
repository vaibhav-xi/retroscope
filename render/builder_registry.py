"""
RetroScope

Builder Registry

Maps render primitives to their geometry builders.

The renderer never needs to know about individual primitive
types. New primitives simply register a new builder.
"""

from render.primitives import Polyline

from render_es2.stroke_builder import StrokeBuilder


class BuilderRegistry:
    """
    Global primitive -> builder registry.
    """

    _builders = {}

    # ---------------------------------------------------------

    @classmethod
    def register(
        cls,
        primitive_type,
        builder,
    ):

        cls._builders[
            primitive_type
        ] = builder

    # ---------------------------------------------------------

    @classmethod
    def builder_for(
        cls,
        primitive,
    ):

        return cls._builders.get(
            type(primitive)
        )


#
# Default builders.
#

BuilderRegistry.register(

    Polyline,

    StrokeBuilder,

)