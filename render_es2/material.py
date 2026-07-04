from dataclasses import dataclass

@dataclass(frozen=True)
class Material:
    """
    Describes how geometry should be rendered.
    """

    color: tuple[float, float, float]

    line_width: float = 1.0