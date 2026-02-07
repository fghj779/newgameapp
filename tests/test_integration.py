import unittest

from orbital_colony.main import create_default_runtime, simulate
from orbital_colony.shared import GameConfig


class TestIntegration(unittest.TestCase):
    def test_five_minute_simulation_smoke(self) -> None:
        runtime = create_default_runtime()
        frame = simulate(runtime, 300.0)

        self.assertGreater(runtime.physics_state.time_seconds, 299.9)
        self.assertGreaterEqual(frame.hud.stability_index, 0.0)
        self.assertLessEqual(frame.hud.stability_index, 1.0)
        self.assertGreaterEqual(len(runtime.drones), 1)

    def test_seeded_run_is_deterministic(self) -> None:
        cfg = GameConfig()
        runtime_a = create_default_runtime(cfg)
        runtime_b = create_default_runtime(cfg)
        frame_a = simulate(runtime_a, 30.0)
        frame_b = simulate(runtime_b, 30.0)

        self.assertAlmostEqual(frame_a.hud.stability_index, frame_b.hud.stability_index, places=10)
        self.assertEqual(frame_a.hud.drone_states, frame_b.hud.drone_states)
        for key in frame_a.hud.commodity_prices:
            self.assertAlmostEqual(
                frame_a.hud.commodity_prices[key],
                frame_b.hud.commodity_prices[key],
                places=10,
            )


if __name__ == "__main__":
    unittest.main()
