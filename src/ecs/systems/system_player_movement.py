"""Sistema de movimiento del jugador: aplica comandos de entrada y dispara balas."""

import math
import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.size import Size
from src.ecs.components.color import Color
from src.ecs.components.active import Active
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.tag_bullet import TagBullet
from src.ecs.components.input_command import InputCommand


class SystemPlayerMovement(esper.Processor):

    def __init__(self, player_speed: float, bullet_cfg: dict, max_bullets: int):
        self.player_speed = player_speed
        self.bullet_cfg = bullet_cfg
        self.max_bullets = max_bullets

    def process(self, delta_time):
        # Leer el único componente de entrada
        inp = None
        for _, (cmd,) in self.world.get_components(InputCommand):
            inp = cmd
            break
        if inp is None:
            return

        # Actualizar velocidad del jugador según las acciones
        for _, (vel, pos, size, _, _) in self.world.get_components(
                Velocity, Position, Size, Active, TagPlayer):
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
                self._fire_bullet(pos, size, inp)

    def _fire_bullet(self, player_pos: Position, player_size: Size, inp: InputCommand):
        bullet_count = sum(1 for _ in self.world.get_component(TagBullet))
        if bullet_count >= self.max_bullets:
            return

        cx = player_pos.x + player_size.width / 2
        cy = player_pos.y + player_size.height / 2

        dx = inp.mouse_x - cx
        dy = inp.mouse_y - cy
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dx /= dist
        dy /= dist

        b = self.bullet_cfg
        speed = b["velocity"]
        bw = b["size"]["x"]
        bh = b["size"]["y"]

        self.world.create_entity(
            Position(x=cx - bw / 2, y=cy - bh / 2),
            Velocity(dx=dx * speed, dy=dy * speed),
            Size(width=bw, height=bh),
            Color(r=b["color"]["r"], g=b["color"]["g"], b=b["color"]["b"]),
            Active(),
            TagBullet()
        )
