"""Sistema de colisiones bala-enemigo: elimina ambos al tocarse y genera explosión."""

import pygame
import esper

from src.ecs.components.position import Position
from src.ecs.components.active import Active
from src.ecs.components.tag_bullet import TagBullet
from src.ecs.components.tag_enemy import TagEnemy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_animation import CAnimation, AnimationData
from src.ecs.components.c_tag_explosion import CTagExplosion


class SystemCollisionBulletEnemy(esper.Processor):

    def __init__(self, explosion_surface: pygame.Surface, explosion_anim_cfg: dict):
        self._expl_surface = explosion_surface
        self._expl_anim_cfg = explosion_anim_cfg

    def process(self, delta_time):
        bullets = list(self.world.get_components(Position, CSurface, Active, TagBullet))
        enemies = list(self.world.get_components(Position, CSurface, Active, TagEnemy))

        for b_ent, (b_pos, b_surf, _, _) in bullets:
            for e_ent, (e_pos, e_surf, _, _) in enemies:
                if self._aabb(b_pos, b_surf, e_pos, e_surf):
                    mid_x = (b_pos.x + b_surf.area.width / 2 +
                             e_pos.x + e_surf.area.width / 2) / 2
                    mid_y = (b_pos.y + b_surf.area.height / 2 +
                             e_pos.y + e_surf.area.height / 2) / 2
                    self._spawn_explosion(mid_x, mid_y)
                    self.world.delete_entity(b_ent)
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
