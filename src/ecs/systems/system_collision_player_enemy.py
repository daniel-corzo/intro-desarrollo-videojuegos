"""Sistema de colisiones jugador-enemigo: reinicia al jugador, elimina enemigo y genera explosión."""

import pygame
import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.tag_enemy import TagEnemy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_animation import CAnimation, AnimationData
from src.ecs.components.c_tag_explosion import CTagExplosion


class SystemCollisionPlayerEnemy(esper.Processor):

    def __init__(self, spawn_x: float, spawn_y: float,
                 explosion_surface: pygame.Surface, explosion_anim_cfg: dict):
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self._expl_surface = explosion_surface
        self._expl_anim_cfg = explosion_anim_cfg

    def process(self, delta_time):
        players = list(self.world.get_components(Position, Velocity, CSurface, Active, TagPlayer))
        enemies = list(self.world.get_components(Position, CSurface, Active, TagEnemy))

        for p_ent, (p_pos, p_vel, p_surf, _, _) in players:
            for e_ent, (e_pos, e_surf, _, _) in enemies:
                if self._aabb(p_pos, p_surf, e_pos, e_surf):
                    mid_x = (p_pos.x + p_surf.area.width / 2 +
                             e_pos.x + e_surf.area.width / 2) / 2
                    mid_y = (p_pos.y + p_surf.area.height / 2 +
                             e_pos.y + e_surf.area.height / 2) / 2
                    self._spawn_explosion(mid_x, mid_y)
                    p_pos.x = self.spawn_x
                    p_pos.y = self.spawn_y
                    p_vel.dx = 0.0
                    p_vel.dy = 0.0
                    self.world.delete_entity(e_ent)
                    break

    # -------------------------------------------------------------------------
    def _spawn_explosion(self, cx: float, cy: float):
        cfg = self._expl_anim_cfg
        num_frames = cfg["number_frames"]
        frame_w = self._expl_surface.get_width() // num_frames
        frame_h = self._expl_surface.get_height()

        animations = {}
        for a in cfg["list"]:
            animations[a["name"]] = AnimationData(
                name=a["name"], start=a["start"], end=a["end"], framerate=a["framerate"]
            )

        self.world.create_entity(
            Position(x=cx - frame_w / 2, y=cy - frame_h / 2),
            CSurface(
                surface=self._expl_surface,
                area=pygame.Rect(0, 0, frame_w, frame_h)
            ),
            CAnimation(
                animations=animations,
                current_animation="EXPLODE",
                current_frame=animations["EXPLODE"].start,
                elapsed_time=0.0,
                number_frames=num_frames,
                frame_width=frame_w,
                looping=False
            ),
            Active(),
            CTagExplosion()
        )

    @staticmethod
    def _aabb(p1: Position, s1: CSurface, p2: Position, s2: CSurface) -> bool:
        return not (
            p1.x + s1.area.width  <= p2.x or
            p2.x + s2.area.width  <= p1.x or
            p1.y + s1.area.height <= p2.y or
            p2.y + s2.area.height <= p1.y
        )
