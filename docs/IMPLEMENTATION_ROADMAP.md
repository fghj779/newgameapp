# Implementation Roadmap

## Technology Choice
- Language: Python 3.11+
- Runtime/Framework: Pygame
- Testing: `unittest` (standard library)

## Milestone 0 - Scaffold (this stage)
1. Create module directories and package layout.
2. Define implementation order and interfaces.
3. Add scaffold verification tests.

Validation:
- `python3 -m unittest -v`

Steer gate:
- Wait for user `Steer` before implementing Module 1.

## Milestone 1 - `core_physics`
Deliverables:
1. Data models: `CelestialBody`, `ColonyNode`, `PhysicsState`.
2. N-body gravity solver (pairwise Newtonian force, softening term).
3. Time-step integrator (semi-implicit Euler start; extensible to RK4).
4. Colony stability index derived from net tidal stress and orbital drift.

Tests:
1. Symmetry check for equal-mass two-body force.
2. Inverse-square trend validation by distance ratio.
3. Stability index boundedness and deterministic updates.

Steer gate:
- Pause for `Steer` after this module.

## Milestone 2 - `economy_engine`
Deliverables:
1. Commodity registry: Oxygen, Fuel, Metals.
2. Supply-demand pricing model with elasticity and damping.
3. Real-time volatility injection with deterministic seeded RNG.
4. Colony-facing API for buy/sell orders and stock depletion.

Tests:
1. Price rises when demand > supply.
2. Price falls when supply > demand.
3. Volatility remains within configured risk envelope.
4. No negative inventory or negative prices.

Steer gate:
- Pause for `Steer` after this module.

## Milestone 3 - `npc_ai`
Deliverables:
1. FSM states: `IDLE`, `SEEK_RESOURCE`, `GATHER`, `DELIVER`, `REPAIR`, `RECHARGE`.
2. Transition guards based on inventory, energy, nearby damage, and priorities.
3. Task scheduler and blackboard for shared world signals.
4. Failure recovery transitions (resource missing, path blocked, low power).

Tests:
1. Deterministic state transitions for known world snapshots.
2. Drone eventually returns to `IDLE` after delivery/repair cycle.
3. Deadlock prevention and fallback transitions.

Steer gate:
- Pause for `Steer` after this module.

## Milestone 4 - `rendering_layer`
Deliverables:
1. Pygame scene graph for colony, bodies, drones.
2. HUD for stability index, commodity prices, and drone states.
3. Debug overlays for force vectors and FSM state labels.
4. Input controls for pause/speed scaling and camera panning.

Tests:
1. Headless-safe logic tests for render adapters.
2. Smoke test for scene updates without runtime exceptions.

Steer gate:
- Pause for `Steer` after this module.

## Milestone 5 - Integration
Deliverables:
1. `main.py` orchestrates physics/economy/AI/render loops.
2. Fixed-step simulation update + interpolated rendering.
3. Config-driven balancing constants in `shared/config.py`.

Tests:
1. Multi-system integration smoke test for 5 simulated minutes.
2. Performance sanity test: stable frame/update cadence.
3. Regression baseline for deterministic seeded run.

Steer gate:
- Pause for final `Steer` for tuning/features.
