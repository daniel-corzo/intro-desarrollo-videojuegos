"""Motor del juego: inicialización, game loop y limpieza."""

import asyncio
import json
import pygame
import esper

from src.engine.service_locator import ServiceLocator

from src.ecs.components.enemy_spawner import EnemySpawner
from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.tag_hud import TagHud
from src.ecs.components.input_command import InputCommand
from src.ecs.components.surface import Surface
from src.ecs.components.animation import Animation, AnimationData
from src.ecs.components.text import Text
from src.ecs.components.pausable import Pausable
from src.ecs.components.special_attack_state import SpecialAttackState

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
from src.ecs.systems.system_special_attack import SystemSpecialAttack
from src.ecs.systems.system_hud import SystemHud
from src.ecs.systems.system_text_rendering import SystemTextRendering


class GameEngine:

    def __init__(self) -> None:
        self.is_running = False
        self.paused = False

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
        ServiceLocator.reset()

        # ---- Cargar configuración -------------------------------------------
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

        with open("assets/cfg/interface.json") as f:
            interface_cfg = json.load(f)

        with open("assets/cfg/special.json") as f:
            special_cfg = json.load(f)

        level_events  = level_full["enemy_spawn_events"]
        player_spawn  = level_full["player_spawn"]["position"]
        max_bullets   = level_full["player_spawn"]["max_bullets"]

        # ---- Inicializar pygame y ventana ------------------------------------
        pygame.init()
        pygame.mixer.init()
        size = window_cfg["size"]
        self.screen = pygame.display.set_mode((size["w"], size["h"]))
        pygame.display.set_caption(window_cfg["title"])
        self.clock = pygame.time.Clock()
        self.framerate = window_cfg["framerate"]
        bg = window_cfg["bg_color"]
        self.bg_color = (bg["r"], bg["g"], bg["b"])
        self.delta_time = 0.0

        # ---- Crear el mundo ECS ---------------------------------------------
        self.world = esper.World()

        # ---- Precargar sonidos vía ServiceLocator ---------------------------
        self._move_sound = player_cfg["sound_move"]
        ServiceLocator.sounds.get(bullet_cfg["sound"])
        ServiceLocator.sounds.get(explosion_cfg["sound"])
        ServiceLocator.sounds.get(special_cfg["sound"])
        ServiceLocator.sounds.get(self._move_sound)
        for ecfg in enemies_cfg.values():
            if "sound" in ecfg:
                ServiceLocator.sounds.get(ecfg["sound"])
            if "sound_chase" in ecfg:
                ServiceLocator.sounds.get(ecfg["sound_chase"])

        # ---- Cargar imágenes vía ServiceLocator -----------------------------
        enemy_surfaces = {}
        for etype, ecfg in enemies_cfg.items():
            enemy_surfaces[etype] = ServiceLocator.images.get(ecfg["image"])

        bullet_surface    = ServiceLocator.images.get(bullet_cfg["image"])
        explosion_surface = ServiceLocator.images.get(explosion_cfg["image"])
        player_surface    = ServiceLocator.images.get(player_cfg["image"])

        # ---- Resolver eventos de spawn --------------------------------------
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
                "sound":                  enemy.get("sound", ""),
                "sound_chase":            enemy.get("sound_chase", ""),
                "spawned":                False,
            })

        # Entidad singleton del spawner
        self.world.create_entity(EnemySpawner(spawn_events=spawn_events))

        # ---- Entidad jugador ------------------------------------------------
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
            SpecialAttackState(cooldown_max=special_cfg["cooldown"]),
            Active(),
            TagPlayer()
        )

        # ---- Entidad singleton de comandos de entrada -----------------------
        self.world.create_entity(InputCommand())

        # ---- Crear entidades de texto de la interfaz ------------------------
        font_path = interface_cfg["font"]
        texts_cfg = interface_cfg["texts"]

        for key, tcfg in texts_cfg.items():
            font = ServiceLocator.fonts.get(font_path, tcfg["size"])
            c = tcfg["color"]
            color = (c["r"], c["g"], c["b"])
            rendered = font.render(tcfg["text"], True, color)

            anchor = tcfg.get("anchor", "top_left")
            px, py = float(tcfg["position"]["x"]), float(tcfg["position"]["y"])
            w, h = rendered.get_size()

            if anchor == "top_center":
                px -= w / 2
            elif anchor == "center":
                px -= w / 2
                py -= h / 2

            surf = Surface(surface=rendered, area=rendered.get_rect())
            txt = Text(
                text=tcfg["text"],
                font_path=font_path,
                font_size=tcfg["size"],
                color=color,
                dirty=False
            )
            pos = Position(x=px, y=py)

            is_paused_text = key in ("paused", "paused_sub")
            is_special_label = key == "special_label"

            if is_paused_text:
                # Inicia sin Active (invisible hasta pausar)
                self.world.create_entity(pos, surf, txt, Pausable())
            elif is_special_label:
                self.world.create_entity(pos, surf, txt, TagHud(key="special_label"), Active())
            else:
                self.world.create_entity(pos, surf, txt, Active())

        # ---- Datos de explosión para los sistemas de colisión ---------------
        expl_anim_cfg = explosion_cfg["animations"]

        # ---- Registrar sistemas (mayor prioridad = se ejecuta primero) ------
        #
        #  100  Leer input del teclado/ratón
        #   90  Establecer velocidad del jugador (consume input)
        #   85  Habilidad especial (consume input, produce entidades)
        #   80  Actualizar estado de animación player/hunter (consume velocidad)
        #   70  Mover el Hunter según FSM (produce velocidad del hunter)
        #   60  Spawnear nuevas entidades
        #   50  Integrar velocidad → posición (consume velocidades)
        #   40  Avanzar cuadros de animación (después de moverse)
        #   30  Aplicar bordes y rebotes (corrige posiciones)
        #   20  Detectar colisiones (sobre posiciones ya corregidas)
        #   15  Actualizar superficies de texto dinámico (antes del render)
        #   10  Renderizar sprites activos sobre pantalla (fill + blit, sin flip)
        #    5  HUD de barra de cooldown (dibuja encima de sprites antes del flip)
        #    0  Limpiar entidades terminadas
        #    El flip de pygame.display se hace en _draw() después de world.process()

        self.world.add_processor(SystemInput(),                                          priority=100)
        self.world.add_processor(
            SystemPlayerMovement(
                player_speed=player_cfg["input_velocity"],
                bullet_surface=bullet_surface,
                bullet_velocity=bullet_cfg["velocity"],
                max_bullets=max_bullets,
                bullet_sound=bullet_cfg["sound"]
            ),                                                                           priority=90)
        self.world.add_processor(SystemSpecialAttack(special_cfg),                      priority=85)
        self.world.add_processor(SystemPlayerAnimation(self._move_sound),                priority=80)
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
        self.world.add_processor(SystemTextRendering(),                                  priority=15)
        self.world.add_processor(SystemRendering(self.screen, self.bg_color),            priority=10)
        self.world.add_processor(SystemHud(self.screen),                                 priority=5)
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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self._toggle_pause()

    def _toggle_pause(self):
        self.paused = not self.paused

        # Detener sonido de movimiento al pausar
        if self.paused:
            ServiceLocator.sounds.stop(self._move_sound)

        for eid, _ in self.world.get_components(Pausable):
            if self.paused and not self.world.has_component(eid, Active):
                self.world.add_component(eid, Active())
            elif not self.paused and self.world.has_component(eid, Active):
                self.world.remove_component(eid, Active)

    # -------------------------------------------------------------------------
    # ACTUALIZAR
    # -------------------------------------------------------------------------
    def _update(self):
        if self.paused:
            # Solo actualizar texto y renderizar; la simulación se detiene
            self.world.get_processor(SystemTextRendering).process(self.delta_time)
            self.world.get_processor(SystemRendering).process(self.delta_time)
        else:
            self.world.process(self.delta_time)

    # -------------------------------------------------------------------------
    # DIBUJAR
    # -------------------------------------------------------------------------
    def _draw(self):
        pygame.display.flip()

    # -------------------------------------------------------------------------
    # TERMINAR
    # -------------------------------------------------------------------------
    def _clean(self):
        pygame.quit()
