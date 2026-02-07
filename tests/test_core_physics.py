import unittest

from orbital_colony.core_physics import (
    CelestialBody,
    ColonyNode,
    PhysicsConfig,
    PhysicsEngine,
    PhysicsState,
    compute_body_accelerations,
    compute_gravity_at_point,
)


class TestCorePhysics(unittest.TestCase):
    def test_two_body_force_symmetry(self) -> None:
        config = PhysicsConfig(gravitational_constant=1.0, softening=1e-6)
        bodies = [
            CelestialBody(name="left", mass=10.0, position=(-1.0, 0.0)),
            CelestialBody(name="right", mass=10.0, position=(1.0, 0.0)),
        ]
        accelerations = compute_body_accelerations(bodies, config)

        self.assertAlmostEqual(accelerations[0][0], -accelerations[1][0], places=8)
        self.assertAlmostEqual(accelerations[0][1], -accelerations[1][1], places=8)
        self.assertGreater(accelerations[0][0], 0.0)
        self.assertLess(accelerations[1][0], 0.0)

    def test_inverse_square_gravity_trend(self) -> None:
        config = PhysicsConfig(gravitational_constant=1.0, softening=1e-6)
        source = [CelestialBody(name="star", mass=25.0, position=(0.0, 0.0))]

        near = compute_gravity_at_point((2.0, 0.0), source, config)
        far = compute_gravity_at_point((4.0, 0.0), source, config)
        near_mag = abs(near[0])
        far_mag = abs(far[0])

        ratio = near_mag / far_mag
        self.assertAlmostEqual(ratio, 4.0, places=3)

    def test_stability_bounded_and_deterministic(self) -> None:
        config = PhysicsConfig(
            gravitational_constant=1.0,
            softening=1e-3,
            tidal_scale=0.05,
            drift_scale=0.05,
            max_penalty=1.0,
        )
        engine = PhysicsEngine(config)

        def make_state() -> PhysicsState:
            return PhysicsState(
                bodies=[
                    CelestialBody(name="planet", mass=40.0, position=(8.0, 0.0), velocity=(0.0, 1.2)),
                    CelestialBody(name="moon", mass=8.0, position=(-6.0, 0.0), velocity=(0.0, -1.0)),
                ],
                colony=ColonyNode(name="colony", mass=2.0, position=(0.0, 0.0)),
            )

        state_a = make_state()
        state_b = make_state()
        for _ in range(120):
            state_a = engine.step(state_a, 0.1)
            state_b = engine.step(state_b, 0.1)
            self.assertGreaterEqual(state_a.stability_index, 0.0)
            self.assertLessEqual(state_a.stability_index, 1.0)

        self.assertAlmostEqual(state_a.time_seconds, state_b.time_seconds, places=10)
        self.assertAlmostEqual(state_a.stability_index, state_b.stability_index, places=10)
        self.assertAlmostEqual(state_a.colony.position[0], state_b.colony.position[0], places=10)
        self.assertAlmostEqual(state_a.colony.position[1], state_b.colony.position[1], places=10)


if __name__ == "__main__":
    unittest.main()
