from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

Vector2 = tuple[float, float]


class DroneState(str, Enum):
    IDLE = "IDLE"
    SEEK_RESOURCE = "SEEK_RESOURCE"
    GATHER = "GATHER"
    DELIVER = "DELIVER"
    REPAIR = "REPAIR"
    RECHARGE = "RECHARGE"


@dataclass
class Drone:
    id: str
    position: Vector2 = (0.0, 0.0)
    state: DroneState = DroneState.IDLE
    energy: float = 100.0
    max_energy: float = 100.0
    cargo_type: str | None = None
    cargo_amount: float = 0.0
    cargo_capacity: float = 10.0
    target_resource: str | None = None
    delivered_total: float = 0.0


@dataclass
class NpcConfig:
    gather_rate: float = 2.0
    delivery_rate: float = 8.0
    repair_rate: float = 5.0
    recharge_rate: float = 20.0
    low_energy_threshold: float = 20.0
    resume_energy_threshold: float = 80.0
    active_energy_burn: float = 2.0


@dataclass
class NpcWorldState:
    resource_nodes: dict[str, float] = field(default_factory=dict)
    colony_inventory: dict[str, float] = field(default_factory=dict)
    colony_damage: float = 0.0
    resource_priority: list[str] = field(default_factory=lambda: ["METALS", "FUEL", "OXYGEN"])
    time_seconds: float = 0.0
