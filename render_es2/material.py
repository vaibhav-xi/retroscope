from dataclasses import dataclass

@dataclass(frozen=True)
class Material:
    """
    Describes how geometry should be rendered.
    """

    color: tuple[float, float, float]

    line_width: float = 1.0

    alpha: float = 1.0

    additive: bool = False

    glow: float = 300.0
