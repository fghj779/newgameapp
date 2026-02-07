import unittest

from orbital_colony.economy_engine import CommodityState, EconomyConfig, EconomyEngine, EconomyState


class TestEconomyEngine(unittest.TestCase):
    def test_price_rises_when_demand_exceeds_supply(self) -> None:
        engine = EconomyEngine(EconomyConfig(volatility=0.0))
        state = EconomyState(
            commodities={
                "OXYGEN": CommodityState(
                    name="OXYGEN",
                    price=10.0,
                    supply_rate=2.0,
                    demand_rate=6.0,
                    inventory=100.0,
                )
            }
        )

        next_state = engine.step(state, 1.0)
        self.assertGreater(next_state.commodities["OXYGEN"].price, 10.0)

    def test_price_falls_when_supply_exceeds_demand(self) -> None:
        engine = EconomyEngine(EconomyConfig(volatility=0.0))
        state = EconomyState(
            commodities={
                "FUEL": CommodityState(
                    name="FUEL",
                    price=20.0,
                    supply_rate=7.0,
                    demand_rate=2.0,
                    inventory=100.0,
                )
            }
        )

        next_state = engine.step(state, 1.0)
        self.assertLess(next_state.commodities["FUEL"].price, 20.0)

    def test_volatility_within_configured_envelope(self) -> None:
        config = EconomyConfig(volatility=0.2, max_volatility_abs=0.08, rng_seed=123)
        engine = EconomyEngine(config)
        state = engine.create_default_state()

        for _ in range(60):
            state = engine.step(state, 0.5)
            for commodity in state.commodities.values():
                self.assertGreaterEqual(commodity.last_volatility, -0.08)
                self.assertLessEqual(commodity.last_volatility, 0.08)

    def test_no_negative_inventory_or_price(self) -> None:
        engine = EconomyEngine(EconomyConfig(min_price=0.01, volatility=0.0))
        state = EconomyState(
            commodities={
                "METALS": CommodityState(
                    name="METALS",
                    price=1.0,
                    supply_rate=0.0,
                    demand_rate=10.0,
                    inventory=3.0,
                )
            }
        )

        for _ in range(20):
            state = engine.step(state, 1.0)
            metals = state.commodities["METALS"]
            self.assertGreaterEqual(metals.price, 0.01)
            self.assertGreaterEqual(metals.inventory, 0.0)

        state_after_buy, filled, _ = engine.place_buy_order(state, "METALS", 100.0)
        self.assertGreaterEqual(state_after_buy.commodities["METALS"].inventory, 0.0)
        self.assertGreaterEqual(filled, 0.0)


if __name__ == "__main__":
    unittest.main()
