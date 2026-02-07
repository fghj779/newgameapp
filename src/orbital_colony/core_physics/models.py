from __future__ import annotations

from dataclasses import dataclass, field

Vector2 = tuple[float, float]


@dataclass
class CelestialBody:
    name: str
    mass: float
    position: Vector2
    velocity: Vector2 = (0.0, 0.0)


@dataclass
class ColonyNode:
    name: str
    mass: float
    position: Vector2
    velocity: Vector2 = (0.0, 0.0)
    anchor_position: Vector2 | None = None

    def __post_init__(self) -> None:
        if self.anchor_position is None:
            self.anchor_position = self.position


@dataclass
class PhysicsConfig:
    gravitational_constant: float = 1.0
    softening: float = 1e-3
    tidal_scale: float = 0.02
    drift_scale: float = 0.04
    max_penalty: float = 1.0


@dataclass
class PhysicsState:
    bodies: list[CelestialBody] = field(default_factory=list)
    colony: ColonyNode | None = None
    time_seconds: float = 0.0
    stability_index: float = 1.0
