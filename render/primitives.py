"""
RetroScope

Render Primitives

Every drawable object derives from Primitive.

The renderer understands primitives.

Simulation modules create primitives.

Primitives contain only data.

They NEVER render themselves.
"""

from abc import ABC


class Primitive(ABC):
    """
    Base class for every render primitive.
    """

    pass