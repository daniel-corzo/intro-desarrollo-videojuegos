"""Motor del juego: inicialización, game loop y limpieza."""

import asyncio
import json
import pygame
import esper

from src.ecs.components.enemy_spawner import EnemySpawner
from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.input_command import InputCommand
from src.ecs.components.surface import Surface
from src.ecs.components.animation import Animation, AnimationData

from src.ecs.systems.system_input import SystemInput
from src.ecs.systems.system_player_movement import SystemPlayerMovement
from src.ecs.systems.system_player_animation import SystemPlayerAnimation
from src.ecs.systems.system_hunter_animation import SystemHunterAnimation
from src.ecs.systems.system_enemy_spawner import SystemEnemySpawner
from src.ecs.systems.system_hunter_movement import SystemHunterMovement
from src.ecs.systems.system_movement import SystemMovement
from src.ecs.systems.system_animation import SystemAnimation
from src.ecs.systems.system_screen_bounce import SystemScreenBounce
from src.ecs.systems.system_player_boundary import SystemPlayerBoundary
from src.ecs.systems.system_bullet_boundary import SystemBulletBoundary
from src.ecs.systems.system_collision_bullet_enemy import SystemCollisionBulletEnemy
from src.ecs.systems.system_collision_player_enemy import SystemCollisionPlayerEnemy
from src.ecs.systems.system_rendering import SystemRendering
from src.ecs.systems.system_explosion_cleanup import SystemExplosionCleanup


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

        with open("assets/cfg/explosion.json") as f:
            explosion_cfg = json.load(f)

        level_events  = level_full["enemy_spawn_events"]
        player_spawn  = level_full["player_spawn"]["position"]
        max_bullets   = level_full["player_spawn"]["max_bullets"]

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

        # ---- Cargar imágenes -----------------------------------------------
        # Pre-cargar una superficie por tipo de enemigo (se comparte entre entidades)
        enemy_surfaces = {}
        for etype, ecfg in enemies_cfg.items():
            enemy_surfaces[etype] = pygame.image.load(ecfg["image"]).convert_alpha()

        bullet_surface = pygame.image.load(bullet_cfg["image"]).convert_alpha()
        explosion_surface = pygame.image.load(explosion_cfg["image"]).convert_alpha()

        # ---- Resolver eventos de spawn -------------------------------------
        spawn_events = []
        for event in level_events:
            etype = event["enemy_type"]
            enemy = enemies_cfg[etype]
            spawn_events.append({
                "time":                   event["time"],
                "position":               event["position"],
                "enemy_type_name":        etype,
                "surface":                enemy_surfaces[etype],
                "animations_cfg":         enemy.get("animations"),
                "speed_min":              enemy.get("velocity_min", 0),
                "speed_max":              enemy.get("velocity_max", 0),
                "velocity_chase":         enemy.get("velocity_chase", 0),
                "velocity_return":        enemy.get("velocity_return", 0),
                "distance_start_chase":   enemy.get("distance_start_chase", 0),
                "distance_start_return":  enemy.get("distance_start_return", 0),
                "spawned":                False,
            })

        # Entidad singleton con los datos del spawner
        self.world.create_entity(EnemySpawner(spawn_events=spawn_events))

        # ---- Entidad jugador -----------------------------------------------
        player_surface = pygame.image.load(player_cfg["image"]).convert_alpha()
        p_anim_cfg = player_cfg["animations"]
        p_num_frames = p_anim_cfg["number_frames"]
        p_frame_w = player_surface.get_width() // p_num_frames
        p_frame_h = player_surface.get_height()

        player_animations = {}
        for a in p_anim_cfg["list"]:
            player_animations[a["name"]] = AnimationData(
                name=a["name"], start=a["start"], end=a["end"], framerate=a["framerate"]
            )

        spawn_x = float(player_spawn["x"])
        spawn_y = float(player_spawn["y"])

        self.world.create_entity(
            Position(x=spawn_x, y=spawn_y),
            Velocity(dx=0.0, dy=0.0),
            Surface(
                surface=player_surface,
                area=pygame.Rect(0, 0, p_frame_w, p_frame_h)
            ),
            Animation(
                animations=player_animations,
                current_animation="IDLE",
                current_frame=player_animations["IDLE"].start,
                elapsed_time=0.0,
                number_frames=p_num_frames,
                frame_width=p_frame_w,
                looping=True
            ),
            Active(),
            TagPlayer()
        )

        # Entidad singleton de comandos de entrada
        self.world.create_entity(InputCommand())

        # ---- Datos de explosión para los sistemas de colisión ---------------
        expl_anim_cfg = explosion_cfg["animations"]

        # ---- Registrar sistemas (mayor prioridad = se ejecuta primero) ------
        #
        # Criterio: las prioridades reflejan el pipeline de datos del frame.
        # Se usan múltiplos de 10 para dejar espacio a futuras inserciones.
        #
        #  100  Leer input del teclado/ratón
        #   90  Establecer velocidad del jugador (consume input)
        #   80  Actualizar estado de animación player/hunter (consume velocidad)
        #   70  Mover el Hunter según FSM (produce velocidad del hunter)
        #   60  Spawnear nuevas entidades
        #   50  Integrar velocidad → posición (consume velocidades)
        #   40  Avanzar cuadros de animación (después de moverse)
        #   30  Aplicar bordes y rebotes (corrige posiciones)
        #   20  Detectar colisiones (sobre posiciones ya corregidas)
        #   10  Renderizar (todo ya está en su lugar)
        #    0  Limpiar entidades terminadas

        self.world.add_processor(SystemInput(),                                          priority=100)
        self.world.add_processor(
            SystemPlayerMovement(
                player_speed=player_cfg["input_velocity"],
                bullet_surface=bullet_surface,
                bullet_velocity=bullet_cfg["velocity"],
                max_bullets=max_bullets
            ),                                                                           priority=90)
        self.world.add_processor(SystemPlayerAnimation(),                                priority=80)
        self.world.add_processor(SystemHunterAnimation(),                                priority=80)
        self.world.add_processor(SystemHunterMovement(),                                 priority=70)
        self.world.add_processor(SystemEnemySpawner(),                                   priority=60)
        self.world.add_processor(SystemMovement(),                                       priority=50)
        self.world.add_processor(SystemAnimation(),                                      priority=40)
        self.world.add_processor(SystemScreenBounce(size["w"], size["h"]),               priority=30)
        self.world.add_processor(SystemPlayerBoundary(size["w"], size["h"]),             priority=30)
        self.world.add_processor(SystemBulletBoundary(size["w"], size["h"]),             priority=30)
        self.world.add_processor(
            SystemCollisionBulletEnemy(explosion_surface, expl_anim_cfg),                priority=20)
        self.world.add_processor(
            SystemCollisionPlayerEnemy(spawn_x, spawn_y, explosion_surface, expl_anim_cfg),
                                                                                         priority=20)
        self.world.add_processor(SystemRendering(self.screen, self.bg_color),            priority=10)
        self.world.add_processor(SystemExplosionCleanup(),                               priority=0)

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
