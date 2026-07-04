"""
RetroScope

Render Primitives

Every drawable object inside RetroScope derives from Primitive.

Primitives are DATA ONLY.

They never render themselves.

The Renderer is responsible for converting primitives
into pixels.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List


# ==========================================================
# Common Types
# ==========================================================

Color = Tuple[int, int, int]

Point2D = Tuple[float, float]


# ==========================================================
# Base Primitive
# ==========================================================

@dataclass
class Primitive:
    """
    Base render primitive.
    """
    pass


# ==========================================================
# Point
# ==========================================================

@dataclass
class Point(Primitive):

    position: Point2D

    color: Color

    size: int = 1


# ==========================================================
# Polyline
# ==========================================================

@dataclass
class Polyline(Primitive):

    points: List[Point2D]

    color: Color

    width: int = 1


# ==========================================================
# Circle
# ==========================================================

@dataclass
class Circle(Primitive):

    center: Point2D

    radius: float

    color: Color

    width: int = 1


# ==========================================================
# Rectangle
# ==========================================================

@dataclass
class Rectangle(Primitive):

    x: float

    y: float

    width: float

    height: float

    color: Color

    filled: bool = False


# ==========================================================
# Text
# ==========================================================

@dataclass
class Text(Primitive):

    text: str

    position: Point2D

    color: Color

    size: int = 18