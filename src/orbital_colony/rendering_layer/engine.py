from __future__ import annotations

from math import sqrt
from typing import Any

from orbital_colony.core_physics import PhysicsState
from orbital_colony.economy_engine import EconomyState
from orbital_colony.npc_ai import Drone

from .models import FrameData, HudData, RenderConfig, RenderEntity


def _mass_to_radius(mass: float) -> float:
    return max(2.0, sqrt(max(mass, 0.0)) * 2.0)


class SceneAdapter:
    def build_frame(
        self,
        physics_state: PhysicsState,
        economy_state: EconomyState,
        drones: list[Drone],
    ) -> FrameData:
        entities: list[RenderEntity] = []
        for body in physics_state.bodies:
            entities.append(
                RenderEntity(
                    id=f"body:{body.name}",
                    kind="celestial_body",
                    position=body.position,
                    radius=_mass_to_radius(body.mass),
                    color=(96, 148, 255),
                    label=body.name,
                    vector=body.velocity,
                )
            )

        if physics_state.colony is not None:
            entities.append(
                RenderEntity(
                    id=f"colony:{physics_state.colony.name}",
                    kind="colony",
                    position=physics_state.colony.position,
                    radius=_mass_to_radius(physics_state.colony.mass) + 3.0,
                    color=(233, 234, 191),
                    label=physics_state.colony.name,
                    vector=physics_state.colony.velocity,
                )
            )

        for drone in drones:
            entities.append(
                RenderEntity(
                    id=f"drone:{drone.id}",
                    kind="drone",
                    position=drone.position,
                    radius=3.0,
                    color=(250, 160, 110),
                    label=drone.state.value,
                )
            )

        hud = HudData(
            stability_index=physics_state.stability_index,
            commodity_prices={name: c.price for name, c in economy_state.commodities.items()},
            drone_states={drone.id: drone.state.value for drone in drones},
        )
        return FrameData(entities=entities, hud=hud)


class RenderEngine:
    def __init__(self, config: RenderConfig | None = None) -> None:
        self.config = config or RenderConfig()

    def draw(self, frame: FrameData, surface: Any = None) -> dict[str, Any]:
        world = {
            "entities_drawn": len(frame.entities),
            "stability": frame.hud.stability_index,
            "commodity_count": len(frame.hud.commodity_prices),
            "drone_count": len(frame.hud.drone_states),
        }
        if surface is None:
            return world

        try:
            import pygame  # type: ignore
        except Exception as exc:
            raise RuntimeError("Pygame is required for surface drawing mode") from exc

        surface.fill((14, 20, 34))
        for entity in frame.entities:
            sx = int(self.config.width / 2 + (entity.position[0] - self.config.camera[0]) * self.config.world_scale)
            sy = int(self.config.height / 2 + (entity.position[1] - self.config.camera[1]) * self.config.world_scale)
            pygame.draw.circle(surface, entity.color, (sx, sy), max(1, int(entity.radius)))
            if self.config.show_debug_vectors and entity.vector is not None:
                ex = int(sx + entity.vector[0] * 4)
                ey = int(sy + entity.vector[1] * 4)
                pygame.draw.line(surface, (230, 230, 230), (sx, sy), (ex, ey), 1)

        return world
