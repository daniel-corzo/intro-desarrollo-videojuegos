"""Sistema de movimiento del jugador: aplica comandos de entrada y dispara balas."""

import math
import pygame
import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.tag_bullet import TagBullet
from src.ecs.components.input_command import InputCommand
from src.ecs.components.surface import Surface
from src.engine.service_locator import ServiceLocator


class SystemPlayerMovement(esper.Processor):

    def __init__(self, player_speed: float, bullet_surface: pygame.Surface,
                 bullet_velocity: float, max_bullets: int, bullet_sound: str):
        self.player_speed = player_speed
        self.bullet_surface = bullet_surface
        self.bullet_velocity = bullet_velocity
        self.max_bullets = max_bullets
        self._bullet_sound = bullet_sound
        # Pre-calcular dimensiones de la bala (son fijas)
        self._bullet_w = bullet_surface.get_width()
        self._bullet_h = bullet_surface.get_height()

    def process(self, delta_time):
        inp = None
        for _, (cmd,) in self.world.get_components(InputCommand):
            inp = cmd
            break
        if inp is None:
            return

        for _, (vel, pos, c_surf, _, _) in self.world.get_components(
                Velocity, Position, Surface, Active, TagPlayer):
            vel.dx = 0.0
            vel.dy = 0.0
            if inp.actions["PLAYER_LEFT"]:
                vel.dx -= self.player_speed
            if inp.actions["PLAYER_RIGHT"]:
                vel.dx += self.player_speed
            if inp.actions["PLAYER_UP"]:
                vel.dy -= self.player_speed
            if inp.actions["PLAYER_DOWN"]:
                vel.dy += self.player_speed

            if inp.actions["PLAYER_FIRE"]:
                self._fire_bullet(pos, c_surf, inp)

    def _fire_bullet(self, player_pos: Position, player_surf: Surface, inp: InputCommand):
        bullet_count = sum(1 for _ in self.world.get_component(TagBullet))
        if bullet_count >= self.max_bullets:
            return

        cx = player_pos.x + player_surf.area.width / 2
        cy = player_pos.y + player_surf.area.height / 2

        dx = inp.mouse_x - cx
        dy = inp.mouse_y - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx /= dist
        dy /= dist

        bw = self._bullet_w
        bh = self._bullet_h

        self.world.create_entity(
            Position(x=cx - bw / 2, y=cy - bh / 2),
            Velocity(dx=dx * self.bullet_velocity, dy=dy * self.bullet_velocity),
            Surface(surface=self.bullet_surface,
                    area=pygame.Rect(0, 0, bw, bh)),
            Active(),
            TagBullet()
        )
        ServiceLocator.sounds.play(self._bullet_sound)
