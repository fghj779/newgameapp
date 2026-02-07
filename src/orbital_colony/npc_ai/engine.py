from __future__ import annotations

from dataclasses import replace

from .models import Drone, DroneState, NpcConfig, NpcWorldState


def _available_resource(priority: list[str], resources: dict[str, float]) -> str | None:
    for name in priority:
        if resources.get(name, 0.0) > 0.0:
            return name
    for name, qty in resources.items():
        if qty > 0.0:
            return name
    return None


class NpcAiEngine:
    def __init__(self, config: NpcConfig | None = None) -> None:
        self.config = config or NpcConfig()

    def step(
        self,
        drones: list[Drone],
        world: NpcWorldState,
        dt_seconds: float,
    ) -> tuple[list[Drone], NpcWorldState]:
        if dt_seconds <= 0:
            raise ValueError("dt_seconds must be positive")

        next_world = NpcWorldState(
            resource_nodes=dict(world.resource_nodes),
            colony_inventory=dict(world.colony_inventory),
            colony_damage=world.colony_damage,
            resource_priority=list(world.resource_priority),
            time_seconds=world.time_seconds + dt_seconds,
        )
        next_drones = [self._step_drone(replace(drone), next_world, dt_seconds) for drone in drones]
        return next_drones, next_world

    def _step_drone(self, drone: Drone, world: NpcWorldState, dt_seconds: float) -> Drone:
        if drone.energy <= self.config.low_energy_threshold and drone.state != DroneState.RECHARGE:
            drone.state = DroneState.RECHARGE
            drone.target_resource = None

        if drone.state == DroneState.IDLE:
            self._on_idle(drone, world)
        elif drone.state == DroneState.SEEK_RESOURCE:
            self._on_seek_resource(drone, world)
        elif drone.state == DroneState.GATHER:
            self._on_gather(drone, world, dt_seconds)
        elif drone.state == DroneState.DELIVER:
            self._on_deliver(drone, world, dt_seconds)
        elif drone.state == DroneState.REPAIR:
            self._on_repair(drone, world, dt_seconds)
        elif drone.state == DroneState.RECHARGE:
            self._on_recharge(drone, dt_seconds)

        if drone.state in (DroneState.SEEK_RESOURCE, DroneState.GATHER, DroneState.REPAIR, DroneState.DELIVER):
            drone.energy = max(0.0, drone.energy - self.config.active_energy_burn * dt_seconds)
            if drone.energy <= self.config.low_energy_threshold and drone.state != DroneState.RECHARGE:
                drone.state = DroneState.RECHARGE
                drone.target_resource = None

        return drone

    def _on_idle(self, drone: Drone, world: NpcWorldState) -> None:
        if world.colony_damage > 0.0 and drone.energy > self.config.low_energy_threshold:
            drone.state = DroneState.REPAIR
            return

        target = _available_resource(world.resource_priority, world.resource_nodes)
        if target is not None:
            drone.state = DroneState.SEEK_RESOURCE
            drone.target_resource = target
        else:
            drone.target_resource = None

    def _on_seek_resource(self, drone: Drone, world: NpcWorldState) -> None:
        target = drone.target_resource or _available_resource(world.resource_priority, world.resource_nodes)
        if target is None:
            drone.state = DroneState.IDLE
            drone.target_resource = None
            return
        if world.resource_nodes.get(target, 0.0) <= 0.0:
            drone.target_resource = _available_resource(world.resource_priority, world.resource_nodes)
            if drone.target_resource is None:
                drone.state = DroneState.IDLE
                return
        drone.state = DroneState.GATHER

    def _on_gather(self, drone: Drone, world: NpcWorldState, dt_seconds: float) -> None:
        if drone.target_resource is None:
            drone.state = DroneState.SEEK_RESOURCE
            return

        available = world.resource_nodes.get(drone.target_resource, 0.0)
        if available <= 0.0:
            drone.state = DroneState.SEEK_RESOURCE
            return

        remaining_capacity = max(0.0, drone.cargo_capacity - drone.cargo_amount)
        gathered = min(self.config.gather_rate * dt_seconds, available, remaining_capacity)
        if gathered <= 0.0:
            drone.state = DroneState.DELIVER if drone.cargo_amount > 0.0 else DroneState.SEEK_RESOURCE
            return

        world.resource_nodes[drone.target_resource] = available - gathered
        drone.cargo_type = drone.target_resource
        drone.cargo_amount += gathered

        if drone.cargo_amount >= drone.cargo_capacity or world.resource_nodes[drone.target_resource] <= 0.0:
            drone.state = DroneState.DELIVER

    def _on_deliver(self, drone: Drone, world: NpcWorldState, dt_seconds: float) -> None:
        if drone.cargo_type is None or drone.cargo_amount <= 0.0:
            drone.state = DroneState.IDLE
            drone.cargo_type = None
            drone.cargo_amount = 0.0
            return

        delivered = min(self.config.delivery_rate * dt_seconds, drone.cargo_amount)
        world.colony_inventory[drone.cargo_type] = world.colony_inventory.get(drone.cargo_type, 0.0) + delivered
        drone.delivered_total += delivered
        drone.cargo_amount -= delivered

        if drone.cargo_amount <= 0.0:
            drone.cargo_amount = 0.0
            drone.cargo_type = None
            drone.state = DroneState.IDLE

    def _on_repair(self, drone: Drone, world: NpcWorldState, dt_seconds: float) -> None:
        if world.colony_damage <= 0.0:
            world.colony_damage = 0.0
            drone.state = DroneState.IDLE
            return
        world.colony_damage = max(0.0, world.colony_damage - self.config.repair_rate * dt_seconds)
        if world.colony_damage <= 0.0:
            drone.state = DroneState.IDLE

    def _on_recharge(self, drone: Drone, dt_seconds: float) -> None:
        drone.energy = min(drone.max_energy, drone.energy + self.config.recharge_rate * dt_seconds)
        if drone.energy >= self.config.resume_energy_threshold:
            drone.state = DroneState.IDLE
