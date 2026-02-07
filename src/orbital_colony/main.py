from __future__ import annotations

from dataclasses import dataclass

from orbital_colony.core_physics import CelestialBody, ColonyNode, PhysicsEngine, PhysicsState
from orbital_colony.economy_engine import EconomyEngine, EconomyState
from orbital_colony.npc_ai import Drone, NpcAiEngine, NpcWorldState
from orbital_colony.rendering_layer import FrameData, RenderEngine, SceneAdapter
from orbital_colony.shared import GameConfig


@dataclass
class GameRuntime:
    config: GameConfig
    physics_engine: PhysicsEngine
    economy_engine: EconomyEngine
    npc_engine: NpcAiEngine
    scene_adapter: SceneAdapter
    render_engine: RenderEngine
    physics_state: PhysicsState
    economy_state: EconomyState
    drones: list[Drone]
    npc_world: NpcWorldState


def create_default_runtime(config: GameConfig | None = None) -> GameRuntime:
    cfg = config or GameConfig()
    physics_engine = PhysicsEngine(cfg.physics)
    economy_engine = EconomyEngine(cfg.economy)
    npc_engine = NpcAiEngine(cfg.npc)
    scene_adapter = SceneAdapter()
    render_engine = RenderEngine(cfg.render)

    physics_state = PhysicsState(
        bodies=[
            CelestialBody(name="Primary", mass=200.0, position=(20.0, 0.0), velocity=(0.0, 0.6)),
            CelestialBody(name="Secondary", mass=120.0, position=(-16.0, 0.0), velocity=(0.0, -0.8)),
        ],
        colony=ColonyNode(name="Orbital-1", mass=4.0, position=(0.0, 0.0), velocity=(0.0, 0.0)),
    )
    economy_state = economy_engine.create_default_state()
    drones = [
        Drone(id="D-01"),
        Drone(id="D-02", energy=75.0),
        Drone(id="D-03", energy=40.0),
    ]
    npc_world = NpcWorldState(
        resource_nodes={"METALS": 140.0, "FUEL": 90.0, "OXYGEN": 110.0},
        colony_inventory={"METALS": 30.0, "FUEL": 25.0, "OXYGEN": 50.0},
        colony_damage=25.0,
        resource_priority=["METALS", "OXYGEN", "FUEL"],
    )

    return GameRuntime(
        config=cfg,
        physics_engine=physics_engine,
        economy_engine=economy_engine,
        npc_engine=npc_engine,
        scene_adapter=scene_adapter,
        render_engine=render_engine,
        physics_state=physics_state,
        economy_state=economy_state,
        drones=drones,
        npc_world=npc_world,
    )


def step_runtime(runtime: GameRuntime, dt_seconds: float) -> FrameData:
    runtime.physics_state = runtime.physics_engine.step(runtime.physics_state, dt_seconds)
    runtime.economy_state = runtime.economy_engine.step(runtime.economy_state, dt_seconds)

    runtime.drones, runtime.npc_world = runtime.npc_engine.step(
        runtime.drones,
        runtime.npc_world,
        dt_seconds,
    )

    for commodity in ("OXYGEN", "FUEL", "METALS"):
        delivered = runtime.npc_world.colony_inventory.get(commodity, 0.0)
        if commodity in runtime.economy_state.commodities:
            runtime.economy_state.commodities[commodity].supply_rate = 1.0 + delivered * 0.01

    frame = runtime.scene_adapter.build_frame(
        runtime.physics_state,
        runtime.economy_state,
        runtime.drones,
    )
    runtime.render_engine.draw(frame)
    return frame


def simulate(runtime: GameRuntime, total_seconds: float) -> FrameData:
    if total_seconds <= 0:
        raise ValueError("total_seconds must be positive")

    frame: FrameData | None = None
    elapsed = 0.0
    while elapsed < total_seconds:
        dt = min(runtime.config.fixed_dt, total_seconds - elapsed)
        frame = step_runtime(runtime, dt)
        elapsed += dt

    if frame is None:
        raise RuntimeError("Simulation did not produce a frame")
    return frame


def run_headless_demo(total_seconds: float = 10.0) -> dict[str, float]:
    runtime = create_default_runtime()
    frame = simulate(runtime, total_seconds)
    return {
        "time_seconds": runtime.physics_state.time_seconds,
        "stability_index": frame.hud.stability_index,
        "drone_count": float(len(runtime.drones)),
        "entity_count": float(len(frame.entities)),
    }


if __name__ == "__main__":
    summary = run_headless_demo(30.0)
    print(
        "Headless simulation finished:",
        f"time={summary['time_seconds']:.2f}s",
        f"stability={summary['stability_index']:.4f}",
        f"drones={int(summary['drone_count'])}",
        f"entities={int(summary['entity_count'])}",
    )
