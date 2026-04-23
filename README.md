# Intro to Game Development

Coursework for **MISW4407 — Introduction to Video Game Development** at Universidad de los Andes. Explores foundational game programming concepts through hands-on implementation of an ECS-based game engine in Python.

> **Status**: Active — content will be added progressively over the next 6 weeks as the course advances.

## Project Structure

```
├── main.py                 # Entry point
├── esper/                  # Vendored esper 2.5 (required for pygbag/web)
├── assets/                 # Game assets and JSON configs
├── src/
│   ├── create/             # Entity factory / creation utilities
│   ├── ecs/
│   │   ├── components/     # Data components (position, velocity, sprite, etc.)
│   │   └── systems/        # Logic systems (movement, rendering, collision, etc.)
│   └── engine/
│       └── game_engine.py  # Core game loop and engine orchestration
├── pyproject.toml
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

## Play Online

**[Play Space Ranger on itch.io](https://daniel-corzo.itch.io/space-ranger)**

## Running

**Desktop:**
```bash
pip install -r requirements.txt
python main.py
```

**Web (pygbag — local dev):**
```bash
python -m pygbag main.py
```
Then open `http://localhost:8000` in your browser.

**Web (pygbag — build archive for itch.io):**
```bash
pygbag --archive main.py
```
Upload `build/web/intro-desarrollo-videojuegos.apk` to itch.io as an HTML game.

> `esper` is vendored in the `esper/` folder so it is available in the WebAssembly runtime. This is required because pygbag runs on Pyodide, which cannot use packages installed in your local virtualenv.
> `pygame` must be imported directly in `main.py` so pygbag knows to preload it for pyodide.

## Topics Covered

- Game loop architecture
- ECS design pattern
- 2D rendering and sprite management
- Input handling
- Collision detection
- Game state management

## License

MIT
