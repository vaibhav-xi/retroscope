from __future__ import annotations

from dataclasses import dataclass

from typing import Tuple

import numpy as np


# ==========================================================
# Common Types
# ==========================================================

Point2D = Tuple[float, float]


# ==========================================================
# Base Primitive
# ==========================================================

@dataclass
class Primitive:
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

    points: np.ndarray

    def __post_init__(self):

        self.points = np.ascontiguousarray(
            self.points,
            dtype=np.float32,
        )

        if self.points.ndim != 2 or self.points.shape[1] != 2:
            raise ValueError(
                "Polyline.points must have shape (N, 2)"
            )


# ==========================================================
# Circle
# ==========================================================

@dataclass
class Circle(Primitive):

    center: Point2D

    radius: float


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