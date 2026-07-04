"""
RetroScope

Geometry Primitives

Pure geometric descriptions.

Rendering appearance is defined by Material.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List


# ==========================================================
# Common Types
# ==========================================================

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

    size: int = 1


# ==========================================================
# Polyline
# ==========================================================

@dataclass
class Polyline(Primitive):

    points: List[Point2D]

    width: int = 1


# ==========================================================
# Circle
# ==========================================================

@dataclass
class Circle(Primitive):

    center: Point2D

    radius: float

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

    filled: bool = False


# ==========================================================
# Text
# ==========================================================

@dataclass
class Text(Primitive):

    text: str

    position: Point2D

    size: int = 18