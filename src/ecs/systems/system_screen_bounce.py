"""Sistema de rebote: invierte la velocidad cuando el rectángulo toca un borde."""

import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.size import Size
from src.ecs.components.active import Active
from src.ecs.components.c_tag_enemy import CTagEnemy


class SystemScreenBounce(esper.Processor):

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def process(self, delta_time):
        for _, (pos, vel, size, _, _) in self.world.get_components(Position, Velocity, Size, Active, CTagEnemy):
            if pos.x < 0:
                pos.x = 0
                vel.dx = abs(vel.dx)

            if pos.x + size.width > self.screen_width:
                pos.x = self.screen_width - size.width
                vel.dx = -abs(vel.dx)

            if pos.y < 0:
                pos.y = 0
                vel.dy = abs(vel.dy)

            if pos.y + size.height > self.screen_height:
                pos.y = self.screen_height - size.height
                vel.dy = -abs(vel.dy)
