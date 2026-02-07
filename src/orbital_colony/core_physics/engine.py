from __future__ import annotations

from dataclasses import replace
from math import sqrt

from .models import CelestialBody, ColonyNode, PhysicsConfig, PhysicsState, Vector2


def _add(a: Vector2, b: Vector2) -> Vector2:
    return (a[0] + b[0], a[1] + b[1])


def _sub(a: Vector2, b: Vector2) -> Vector2:
    return (a[0] - b[0], a[1] - b[1])


def _scale(a: Vector2, scalar: float) -> Vector2:
    return (a[0] * scalar, a[1] * scalar)


def _norm(a: Vector2) -> float:
    return sqrt(a[0] * a[0] + a[1] * a[1])


def _acceleration_from_source(
    source_mass: float,
    source_position: Vector2,
    target_position: Vector2,
    config: PhysicsConfig,
) -> Vector2:
    delta = _sub(source_position, target_position)
    dist_sq = delta[0] * delta[0] + delta[1] * delta[1] + config.softening * config.softening
    inv_dist = 1.0 / sqrt(dist_sq)
    accel_scale = config.gravitational_constant * source_mass * inv_dist * inv_dist * inv_dist
    return _scale(delta, accel_scale)


def compute_body_accelerations(
    bodies: list[CelestialBody],
    config: PhysicsConfig,
) -> list[Vector2]:
    accelerations: list[Vector2] = []
    for i, target in enumerate(bodies):
        total = (0.0, 0.0)
        for j, source in enumerate(bodies):
            if i == j:
                continue
            total = _add(
                total,
                _acceleration_from_source(
                    source.mass,
                    source.position,
                    target.position,
                    config,
                ),
            )
        accelerations.append(total)
    return accelerations


def compute_gravity_at_point(
    point: Vector2,
    bodies: list[CelestialBody],
    config: PhysicsConfig,
) -> Vector2:
    total = (0.0, 0.0)
    for body in bodies:
        total = _add(
            total,
            _acceleration_from_source(
                body.mass,
                body.position,
                point,
                config,
            ),
        )
    return total


def compute_stability_index(
    colony: ColonyNode,
    bodies: list[CelestialBody],
    config: PhysicsConfig,
) -> float:
    tidal_stress = 0.0
    for body in bodies:
        offset = _sub(body.position, colony.position)
        dist_sq = offset[0] * offset[0] + offset[1] * offset[1] + config.softening * config.softening
        dist = sqrt(dist_sq)
        tidal_stress += config.gravitational_constant * body.mass / (dist_sq * dist)

    drift = _norm(_sub(colony.position, colony.anchor_position))
    penalty = config.tidal_scale * tidal_stress + config.drift_scale * drift
    normalized_penalty = min(max(penalty / config.max_penalty, 0.0), 1.0)
    return 1.0 - normalized_penalty


class PhysicsEngine:
    def __init__(self, config: PhysicsConfig | None = None) -> None:
        self.config = config or PhysicsConfig()

    def step(self, state: PhysicsState, dt_seconds: float) -> PhysicsState:
        if dt_seconds <= 0:
            raise ValueError("dt_seconds must be positive")

        next_bodies = [replace(body) for body in state.bodies]
        body_accels = compute_body_accelerations(next_bodies, self.config)
        for body, accel in zip(next_bodies, body_accels):
            body.velocity = _add(body.velocity, _scale(accel, dt_seconds))
            body.position = _add(body.position, _scale(body.velocity, dt_seconds))

        next_colony = None
        if state.colony is not None:
            next_colony = replace(state.colony)
            colony_accel = compute_gravity_at_point(next_colony.position, next_bodies, self.config)
            next_colony.velocity = _add(next_colony.velocity, _scale(colony_accel, dt_seconds))
            next_colony.position = _add(next_colony.position, _scale(next_colony.velocity, dt_seconds))
            stability_index = compute_stability_index(next_colony, next_bodies, self.config)
        else:
            stability_index = state.stability_index

        return PhysicsState(
            bodies=next_bodies,
            colony=next_colony,
            time_seconds=state.time_seconds + dt_seconds,
            stability_index=stability_index,
        )
