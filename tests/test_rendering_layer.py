import unittest

from orbital_colony.core_physics import CelestialBody, ColonyNode, PhysicsState
from orbital_colony.economy_engine import CommodityState, EconomyState
from orbital_colony.npc_ai import Drone, DroneState
from orbital_colony.rendering_layer import RenderEngine, SceneAdapter


class TestRenderingLayer(unittest.TestCase):
    def test_scene_adapter_builds_entities_and_hud(self) -> None:
        adapter = SceneAdapter()
        physics_state = PhysicsState(
            bodies=[CelestialBody(name="A", mass=25.0, position=(1.0, 2.0))],
            colony=ColonyNode(name="C", mass=3.0, position=(0.0, 0.0)),
            stability_index=0.82,
        )
        economy_state = EconomyState(
            commodities={
                "OXYGEN": CommodityState("OXYGEN", 12.0, 1.0, 1.0, 100.0),
                "FUEL": CommodityState("FUEL", 15.0, 1.0, 1.0, 100.0),
            }
        )
        drones = [Drone(id="D1", state=DroneState.GATHER)]

        frame = adapter.build_frame(physics_state, economy_state, drones)
        self.assertEqual(len(frame.entities), 3)
        self.assertAlmostEqual(frame.hud.stability_index, 0.82, places=10)
        self.assertIn("OXYGEN", frame.hud.commodity_prices)
        self.assertEqual(frame.hud.drone_states["D1"], "GATHER")

    def test_headless_render_smoke(self) -> None:
        adapter = SceneAdapter()
        render = RenderEngine()
        frame = adapter.build_frame(PhysicsState(), EconomyState(), [])
        result = render.draw(frame)
        self.assertEqual(result["entities_drawn"], 0)
        self.assertIn("stability", result)


if __name__ == "__main__":
    unittest.main()
