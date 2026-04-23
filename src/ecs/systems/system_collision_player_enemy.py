"""Sistema de colisiones jugador-enemigo: reinicia al jugador, elimina enemigo y genera explosión."""

from __future__ import annotations

import pygame
import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.tag_enemy import TagEnemy
from src.ecs.components.tag_explosion import TagExplosion
from src.ecs.components.surface import Surface
from src.ecs.components.animation import Animation, AnimationData
from src.engine.service_locator import ServiceLocator

_EXPLOSION_SOUND = "assets/snd/explosion.ogg"


class SystemCollisionPlayerEnemy(esper.Processor):

    def __init__(self, spawn_x: float, spawn_y: float,
                 explosion_surface: pygame.Surface, explosion_anim_cfg: dict):
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self._expl_surface = explosion_surface

        # Pre-calcular una sola vez para todas las explosiones
        cfg = explosion_anim_cfg
        num_frames = cfg["number_frames"]
        self._expl_frame_w = explosion_surface.get_width() // num_frames
        self._expl_frame_h = explosion_surface.get_height()
        self._expl_num_frames = num_frames
        self._expl_animations = {
            a["name"]: AnimationData(
                name=a["name"], start=a["start"], end=a["end"], framerate=a["framerate"]
            )
            for a in cfg["list"]
        }

    def process(self, delta_time):
        players = list(self.world.get_components(Position, Velocity, Surface, Active, TagPlayer))
        enemies = list(self.world.get_components(Position, Surface, Active, TagEnemy))

        for p_ent, (p_pos, p_vel, p_surf, _, _) in players:
            for e_ent, (e_pos, e_surf, _, _) in enemies:
                if self._aabb(p_pos, p_surf, e_pos, e_surf):
                    mid_x = (p_pos.x + p_surf.area.width / 2 +
                             e_pos.x + e_surf.area.width / 2) / 2
                    mid_y = (p_pos.y + p_surf.area.height / 2 +
                             e_pos.y + e_surf.area.height / 2) / 2
                    self._spawn_explosion(mid_x, mid_y)
                    ServiceLocator.sounds.play(_EXPLOSION_SOUND)
                    p_pos.x = self.spawn_x
                    p_pos.y = self.spawn_y
                    p_vel.dx = 0.0
                    p_vel.dy = 0.0
                    self.world.delete_entity(e_ent)
                    break

    # -------------------------------------------------------------------------
    def _spawn_explosion(self, cx: float, cy: float):
        fw, fh = self._expl_frame_w, self._expl_frame_h
        self.world.create_entity(
            Position(x=cx - fw / 2, y=cy - fh / 2),
            Surface(
                surface=self._expl_surface,
                area=pygame.Rect(0, 0, fw, fh)
            ),
            Animation(
                animations=self._expl_animations,
                current_animation="EXPLODE",
                current_frame=self._expl_animations["EXPLODE"].start,
                elapsed_time=0.0,
                number_frames=self._expl_num_frames,
                frame_width=fw,
                looping=False
            ),
            Active(),
            TagExplosion()
        )

    @staticmethod
    def _aabb(p1: Position, s1: Surface, p2: Position, s2: Surface) -> bool:
        return not (
            p1.x + s1.area.width  <= p2.x or
            p2.x + s2.area.width  <= p1.x or
            p1.y + s1.area.height <= p2.y or
            p2.y + s2.area.height <= p1.y
        )
