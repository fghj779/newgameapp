from __future__ import annotations

import random
from dataclasses import replace
from math import sqrt

from .models import CommodityState, EconomyConfig, EconomyState


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(value, upper))


class EconomyEngine:
    def __init__(self, config: EconomyConfig | None = None) -> None:
        self.config = config or EconomyConfig()
        self._rng = random.Random(self.config.rng_seed)

    def create_default_state(self) -> EconomyState:
        return EconomyState(
            commodities={
                name: CommodityState(
                    name=name,
                    price=price,
                    supply_rate=1.0,
                    demand_rate=1.0,
                    inventory=100.0,
                )
                for name, price in self.config.base_prices.items()
            }
        )

    def step(self, state: EconomyState, dt_seconds: float) -> EconomyState:
        if dt_seconds <= 0:
            raise ValueError("dt_seconds must be positive")

        next_state = EconomyState(commodities={}, time_seconds=state.time_seconds + dt_seconds)

        for key, commodity in state.commodities.items():
            c = replace(commodity)
            imbalance = (c.demand_rate - c.supply_rate) / max(c.supply_rate, 1e-6)
            target_price = c.price * (1.0 + self.config.elasticity * imbalance)
            damped_price = c.price + self.config.damping * (target_price - c.price)

            volatility_sigma = self.config.volatility * sqrt(dt_seconds)
            raw_shock = self._rng.gauss(0.0, volatility_sigma)
            shock = _clamp(raw_shock, -self.config.max_volatility_abs, self.config.max_volatility_abs)

            candidate_price = damped_price * (1.0 + shock)
            ratio_step = (candidate_price - c.price) / max(c.price, 1e-6)
            ratio_step = _clamp(
                ratio_step,
                -self.config.max_price_step_ratio,
                self.config.max_price_step_ratio,
            )
            c.price = max(self.config.min_price, c.price * (1.0 + ratio_step))
            c.last_volatility = shock

            c.inventory += (c.supply_rate - c.demand_rate) * dt_seconds
            c.inventory = max(self.config.min_inventory, c.inventory)

            next_state.commodities[key] = c

        return next_state

    def place_buy_order(
        self,
        state: EconomyState,
        commodity_name: str,
        quantity: float,
    ) -> tuple[EconomyState, float, float]:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if commodity_name not in state.commodities:
            raise KeyError(f"Unknown commodity: {commodity_name}")

        next_state = EconomyState(
            commodities={k: replace(v) for k, v in state.commodities.items()},
            time_seconds=state.time_seconds,
        )
        commodity = next_state.commodities[commodity_name]
        filled = min(quantity, commodity.inventory)
        cost = filled * commodity.price
        commodity.inventory -= filled
        commodity.demand_rate += quantity
        commodity.inventory = max(self.config.min_inventory, commodity.inventory)
        return next_state, filled, cost

    def place_sell_order(
        self,
        state: EconomyState,
        commodity_name: str,
        quantity: float,
    ) -> tuple[EconomyState, float]:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if commodity_name not in state.commodities:
            raise KeyError(f"Unknown commodity: {commodity_name}")

        next_state = EconomyState(
            commodities={k: replace(v) for k, v in state.commodities.items()},
            time_seconds=state.time_seconds,
        )
        commodity = next_state.commodities[commodity_name]
        revenue = quantity * commodity.price
        commodity.inventory += quantity
        commodity.supply_rate += quantity
        commodity.inventory = max(self.config.min_inventory, commodity.inventory)
        return next_state, revenue
