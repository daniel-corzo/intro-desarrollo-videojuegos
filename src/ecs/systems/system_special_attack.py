"""Sistema de habilidad especial: disparo de 4 balas diagonales con cooldown."""

import math
import pygame
import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active
from src.ecs.components.surface import Surface
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.tag_bullet import TagBullet
from src.ecs.components.input_command import InputCommand
from src.ecs.components.special_attack_state import SpecialAttackState
from src.engine.service_locator import ServiceLocator


class SystemSpecialAttack(esper.Processor):

    def __init__(self, special_cfg: dict):
        self._image_path = special_cfg["image"]
        self._sound_path = special_cfg["sound"]
        self._velocity = special_cfg["velocity"]
        self._spread_rad = math.radians(special_cfg["spread_deg"])

    def process(self, delta_time):
        inp = None
        for _, (cmd,) in self.world.get_components(InputCommand):
            inp = cmd
            break
        if inp is None:
            return

        for _, (pos, surf, special, _) in self.world.get_components(
                Position, Surface, SpecialAttackState, TagPlayer):
            if special.cooldown_remaining > 0.0:
                special.cooldown_remaining = max(0.0, special.cooldown_remaining - delta_time)

            if inp.actions["PLAYER_SPECIAL"] and special.ready:
                self._fire_special(pos, surf, inp)
                special.cooldown_remaining = special.cooldown_max

    def _fire_special(self, player_pos: Position, player_surf: Surface, inp: InputCommand):
        cx = player_pos.x + player_surf.area.width / 2
        cy = player_pos.y + player_surf.area.height / 2

        dx = inp.mouse_x - cx
        dy = inp.mouse_y - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            aim_angle = 0.0
        else:
            aim_angle = math.atan2(dy, dx)

        bullet_surf = ServiceLocator.images.get(self._image_path)
        bw = bullet_surf.get_width()
        bh = bullet_surf.get_height()

        # 4 balas distribuidas simétricamente alrededor del ángulo de apuntado
        offsets = [
            -1.5 * self._spread_rad,
            -0.5 * self._spread_rad,
             0.5 * self._spread_rad,
             1.5 * self._spread_rad,
        ]
        for offset in offsets:
            angle = aim_angle + offset
            vx = math.cos(angle) * self._velocity
            vy = math.sin(angle) * self._velocity
            self.world.create_entity(
                Position(x=cx - bw / 2, y=cy - bh / 2),
                Velocity(dx=vx, dy=vy),
                Surface(surface=bullet_surf, area=pygame.Rect(0, 0, bw, bh)),
                Active(),
                TagBullet(),
            )

        ServiceLocator.sounds.play(self._sound_path)
