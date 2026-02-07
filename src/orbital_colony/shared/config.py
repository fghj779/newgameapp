from __future__ import annotations

from dataclasses import dataclass, field

from orbital_colony.core_physics import PhysicsConfig
from orbital_colony.economy_engine import EconomyConfig
from orbital_colony.npc_ai import NpcConfig
from orbital_colony.rendering_layer import RenderConfig


@dataclass(frozen=True)
class GameConfig:
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    economy: EconomyConfig = field(default_factory=EconomyConfig)
    npc: NpcConfig = field(default_factory=NpcConfig)
    render: RenderConfig = field(default_factory=RenderConfig)
    fixed_dt: float = 0.1
