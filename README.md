# Orbital Colony Management (2D)

A modular 2D colony simulation prototype in Python.

## Architecture
- `core_physics`: N-body gravity and orbital stability calculations.
- `economy_engine`: Dynamic supply-demand market for Oxygen, Fuel, Metals.
- `npc_ai`: Worker drone finite state machines for autonomous tasks.
- `rendering_layer`: Pygame rendering, camera, and HUD.

## Project Layout
- `src/orbital_colony/main.py`: Composition root / game loop entrypoint.
- `src/orbital_colony/shared/`: Shared models, constants, config utilities.
- `tests/`: Stage-by-stage stability tests.
- `docs/IMPLEMENTATION_ROADMAP.md`: Build plan and milestones.

## Current Stage
Scaffold + roadmap only.
