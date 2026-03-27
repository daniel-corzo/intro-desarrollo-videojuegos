"""Motor del juego: inicialización, game loop y limpieza."""

import json
import pygame
import esper

from src.ecs.components.enemy_spawner import EnemySpawner
from src.ecs.systems.system_enemy_spawner import SystemEnemySpawner
from src.ecs.systems.system_movement import SystemMovement
from src.ecs.systems.system_screen_bounce import SystemScreenBounce
from src.ecs.systems.system_rendering import SystemRendering


class GameEngine:

    def __init__(self) -> None:
        self.is_running = False

    def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
        self._clean()

    # -------------------------------------------------------------------------
    # INICIAR
    # -------------------------------------------------------------------------
    def _create(self):
        # Cargar configuración
        with open("assets/cfg/window.json") as f:
            window_cfg = json.load(f)

        with open("assets/cfg/enemies.json") as f:
            enemies_cfg = json.load(f)

        with open("assets/cfg/level_01.json") as f:
            level_cfg = json.load(f)["enemy_spawn_events"]

        # Inicializar pygame y ventana
        pygame.init()
        size = window_cfg["size"]
        self.screen = pygame.display.set_mode((size["w"], size["h"]))
        pygame.display.set_caption(window_cfg["title"])
        self.clock = pygame.time.Clock()
        self.framerate = window_cfg["framerate"]
        bg = window_cfg["bg_color"]
        self.bg_color = (bg["r"], bg["g"], bg["b"])
        self.delta_time = 0.0

        # Crear el mundo ECS
        self.world = esper.World()

        # Resolver eventos: cruzar datos del nivel con datos del enemigo
        # enemies_cfg es un dict: { "TypeA": { size, color, velocity_min, velocity_max }, ... }
        spawn_events = []
        for event in level_cfg:
            enemy = enemies_cfg[event["enemy_type"]]
            spawn_events.append({
                "time":      event["time"],
                "position":  event["position"],
                "size":      enemy["size"],
                "color":     enemy["color"],
                "speed_min": enemy["velocity_min"],
                "speed_max": enemy["velocity_max"],
                "spawned":   False
            })

        # Crear la única entidad con el componente EnemySpawner
        self.world.create_entity(EnemySpawner(spawn_events=spawn_events))

        # Registrar sistemas (mayor prioridad = se ejecuta primero)
        self.world.add_processor(SystemEnemySpawner(),                        priority=4)
        self.world.add_processor(SystemMovement(),                            priority=3)
        self.world.add_processor(SystemScreenBounce(size["w"], size["h"]),    priority=2)
        self.world.add_processor(SystemRendering(self.screen, self.bg_color), priority=1)

    # -------------------------------------------------------------------------
    # CALCULAR TIEMPO
    # -------------------------------------------------------------------------
    def _calculate_time(self):
        self.delta_time = self.clock.tick(self.framerate) / 1000.0

    # -------------------------------------------------------------------------
    # PROCESAR EVENTOS
    # -------------------------------------------------------------------------
    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    # -------------------------------------------------------------------------
    # ACTUALIZAR
    # -------------------------------------------------------------------------
    def _update(self):
        self.world.process(self.delta_time)

    # -------------------------------------------------------------------------
    # DIBUJAR
    # -------------------------------------------------------------------------
    def _draw(self):
        pass  # El renderizado lo maneja SystemRendering dentro de _update

    # -------------------------------------------------------------------------
    # TERMINAR
    # -------------------------------------------------------------------------
    def _clean(self):
        pygame.quit()
