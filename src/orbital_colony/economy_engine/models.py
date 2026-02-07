from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CommodityState:
    name: str
    price: float
    supply_rate: float
    demand_rate: float
    inventory: float
    last_volatility: float = 0.0


@dataclass
class EconomyConfig:
    elasticity: float = 0.35
    damping: float = 0.4
    volatility: float = 0.05
    min_price: float = 0.01
    max_price_step_ratio: float = 0.2
    min_inventory: float = 0.0
    rng_seed: int = 7
    max_volatility_abs: float = 0.25
    base_prices: dict[str, float] = field(
        default_factory=lambda: {
            "OXYGEN": 10.0,
            "FUEL": 14.0,
            "METALS": 8.0,
        }
    )


@dataclass
class EconomyState:
    commodities: dict[str, CommodityState] = field(default_factory=dict)
    time_seconds: float = 0.0
