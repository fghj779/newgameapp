import unittest

from orbital_colony.npc_ai import Drone, DroneState, NpcAiEngine, NpcConfig, NpcWorldState


class TestNpcAi(unittest.TestCase):
    def test_deterministic_transitions(self) -> None:
        config = NpcConfig(
            gather_rate=4.0,
            delivery_rate=6.0,
            repair_rate=8.0,
            recharge_rate=20.0,
            active_energy_burn=1.0,
            low_energy_threshold=10.0,
            resume_energy_threshold=60.0,
        )
        engine = NpcAiEngine(config)

        drones_a = [Drone(id="D1", energy=100.0)]
        world_a = NpcWorldState(
            resource_nodes={"METALS": 20.0},
            colony_inventory={},
            colony_damage=0.0,
            resource_priority=["METALS"],
        )
        drones_b = [Drone(id="D1", energy=100.0)]
        world_b = NpcWorldState(
            resource_nodes={"METALS": 20.0},
            colony_inventory={},
            colony_damage=0.0,
            resource_priority=["METALS"],
        )

        for _ in range(25):
            drones_a, world_a = engine.step(drones_a, world_a, 0.5)
            drones_b, world_b = engine.step(drones_b, world_b, 0.5)

        self.assertEqual(drones_a[0].state, drones_b[0].state)
        self.assertAlmostEqual(drones_a[0].delivered_total, drones_b[0].delivered_total, places=10)
        self.assertAlmostEqual(world_a.colony_inventory["METALS"], world_b.colony_inventory["METALS"], places=10)

    def test_eventually_returns_to_idle_after_delivery_cycle(self) -> None:
        engine = NpcAiEngine(NpcConfig(gather_rate=20.0, delivery_rate=20.0, active_energy_burn=0.1))
        drones = [Drone(id="D2")]
        world = NpcWorldState(
            resource_nodes={"OXYGEN": 8.0},
            colony_inventory={},
            colony_damage=0.0,
            resource_priority=["OXYGEN"],
        )

        seen_idle_after_work = False
        worked = False
        for _ in range(40):
            drones, world = engine.step(drones, world, 0.25)
            if drones[0].delivered_total > 0.0:
                worked = True
            if worked and drones[0].state == DroneState.IDLE:
                seen_idle_after_work = True
                break

        self.assertTrue(worked)
        self.assertTrue(seen_idle_after_work)

    def test_fallback_when_resource_missing_or_low_power(self) -> None:
        engine = NpcAiEngine(
            NpcConfig(
                gather_rate=2.0,
                delivery_rate=2.0,
                recharge_rate=50.0,
                active_energy_burn=5.0,
                low_energy_threshold=15.0,
                resume_energy_threshold=40.0,
            )
        )
        drones = [Drone(id="D3", energy=14.0, state=DroneState.GATHER, target_resource="FUEL")]
        world = NpcWorldState(
            resource_nodes={"FUEL": 0.0},
            colony_inventory={},
            colony_damage=0.0,
            resource_priority=["FUEL"],
        )

        drones, world = engine.step(drones, world, 1.0)
        self.assertIn(drones[0].state, {DroneState.RECHARGE, DroneState.IDLE})

        drones, world = engine.step(drones, world, 1.0)
        self.assertEqual(drones[0].state, DroneState.IDLE)


if __name__ == "__main__":
    unittest.main()
