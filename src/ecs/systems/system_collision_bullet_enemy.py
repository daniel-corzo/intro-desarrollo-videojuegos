"""Sistema de colisiones bala-enemigo: elimina ambos al tocarse y genera explosión."""

import pygame
import esper

from src.ecs.components.position import Position
from src.ecs.components.active import Active
from src.ecs.components.tag_bullet import TagBullet
from src.ecs.components.tag_enemy import TagEnemy
from src.ecs.components.tag_explosion import TagExplosion
from src.ecs.components.surface import Surface
from src.ecs.components.animation import Animation, AnimationData


class SystemCollisionBulletEnemy(esper.Processor):

    def __init__(self, explosion_surface: pygame.Surface, explosion_anim_cfg: dict):
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
        bullets = list(self.world.get_components(Position, Surface, Active, TagBullet))
        if not bullets:
            return
        enemies = list(self.world.get_components(Position, Surface, Active, TagEnemy))

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
