# Intro to Game Development

Coursework for **MISW4407 — Introduction to Video Game Development** at Universidad de los Andes. Explores foundational game programming concepts through hands-on implementation of an ECS-based game engine in Python.

> **Status**: Active — content will be added progressively over the next 6 weeks as the course advances.

## Project Structure

```
├── main.py                 # Entry point
├── assets/                 # Game assets (sprites, sounds, etc.)
├── src/
│   ├── create/             # Entity factory / creation utilities
│   ├── ecs/
│   │   ├── components/     # Data components (position, velocity, sprite, etc.)
│   │   └── systems/        # Logic systems (movement, rendering, collision, etc.)
│   └── engine/
│       └── game_engine.py  # Core game loop and engine orchestration
├── requirements.txt
└── .pylintrc               # Code quality enforcement
```

## Architecture

The project follows the **Entity Component System** pattern:

| Concept    | Role |
|------------|------|
| **Entity** | A unique ID with attached components |
| **Component** | Pure data (no logic) — position, health, sprite reference |
| **System** | Logic that processes all entities matching a component signature |
| **Engine** | Game loop that ticks all systems each frame |

## Running

```bash
pip install -r requirements.txt
python main.py
```

## Topics Covered

- Game loop architecture
- ECS design pattern
- 2D rendering and sprite management
- Input handling
- Collision detection
- Game state management

## License

MIT
