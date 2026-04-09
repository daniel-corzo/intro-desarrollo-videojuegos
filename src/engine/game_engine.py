"""Motor del juego: inicialización, game loop y limpieza."""

import asyncio
import json
import pygame
import esper

from src.ecs.components.enemy_spawner import EnemySpawner
from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.size import Size
from src.ecs.components.color import Color
from src.ecs.components.active import Active
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.input_command import InputCommand

from src.ecs.systems.system_input import SystemInput
from src.ecs.systems.system_player_movement import SystemPlayerMovement
from src.ecs.systems.system_enemy_spawner import SystemEnemySpawner
from src.ecs.systems.system_movement import SystemMovement
from src.ecs.systems.system_screen_bounce import SystemScreenBounce
from src.ecs.systems.system_player_boundary import SystemPlayerBoundary
from src.ecs.systems.system_bullet_boundary import SystemBulletBoundary
from src.ecs.systems.system_collision_bullet_enemy import SystemCollisionBulletEnemy
from src.ecs.systems.system_collision_player_enemy import SystemCollisionPlayerEnemy
from src.ecs.systems.system_rendering import SystemRendering


class GameEngine:

    def __init__(self) -> None:
        self.is_running = False

    async def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
            await asyncio.sleep(0)
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
            level_full = json.load(f)

        with open("assets/cfg/player.json") as f:
            player_cfg = json.load(f)

        with open("assets/cfg/bullet.json") as f:
            bullet_cfg = json.load(f)

        level_events   = level_full["enemy_spawn_events"]
        player_spawn   = level_full["player_spawn"]["position"]
        max_bullets    = level_full["player_spawn"]["max_bullets"]

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

        # Resolver eventos de spawn: cruzar nivel con tipos de enemigo
        spawn_events = []
        for event in level_events:
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

        # Entidad singleton con los datos del spawner
        self.world.create_entity(EnemySpawner(spawn_events=spawn_events))

        # Entidad jugador
        p = player_cfg
        self.world.create_entity(
            Position(x=float(player_spawn["x"]), y=float(player_spawn["y"])),
            Velocity(dx=0.0, dy=0.0),
            Size(width=float(p["size"]["x"]), height=float(p["size"]["y"])),
            Color(r=p["color"]["r"], g=p["color"]["g"], b=p["color"]["b"]),
            Active(),
            TagPlayer()
        )

        # Entidad singleton de comandos de entrada
        self.world.create_entity(InputCommand())

        # Registrar sistemas (mayor prioridad = se ejecuta primero)
        self.world.add_processor(SystemInput(),                                                   priority=10)
        self.world.add_processor(SystemPlayerMovement(p["input_velocity"], bullet_cfg, max_bullets), priority=9)
        self.world.add_processor(SystemEnemySpawner(),                                            priority=8)
        self.world.add_processor(SystemMovement(),                                                priority=7)
        self.world.add_processor(SystemScreenBounce(size["w"], size["h"]),                        priority=6)
        self.world.add_processor(SystemPlayerBoundary(size["w"], size["h"]),                      priority=5)
        self.world.add_processor(SystemBulletBoundary(size["w"], size["h"]),                      priority=4)
        self.world.add_processor(SystemCollisionBulletEnemy(),                                    priority=3)
        self.world.add_processor(SystemCollisionPlayerEnemy(
            float(player_spawn["x"]), float(player_spawn["y"])),                                  priority=2)
        self.world.add_processor(SystemRendering(self.screen, self.bg_color),                     priority=1)

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
