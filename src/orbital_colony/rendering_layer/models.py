from __future__ import annotations

from dataclasses import dataclass, field

Vector2 = tuple[float, float]


@dataclass
class RenderConfig:
    width: int = 1280
    height: int = 720
    world_scale: float = 12.0
    camera: Vector2 = (0.0, 0.0)
    show_debug_vectors: bool = True


@dataclass
class RenderEntity:
    id: str
    kind: str
    position: Vector2
    radius: float
    color: tuple[int, int, int]
    label: str = ""
    vector: Vector2 | None = None


@dataclass
class HudData:
    stability_index: float
    commodity_prices: dict[str, float] = field(default_factory=dict)
    drone_states: dict[str, str] = field(default_factory=dict)


@dataclass
class FrameData:
    entities: list[RenderEntity] = field(default_factory=list)
    hud: HudData = field(default_factory=lambda: HudData(stability_index=1.0))
