"""Sistema de colisiones jugador-enemigo: reinicia al jugador y elimina al enemigo."""

import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.size import Size
from src.ecs.components.active import Active
from src.ecs.components.c_tag_player import CTagPlayer
from src.ecs.components.c_tag_enemy import CTagEnemy


class SystemCollisionPlayerEnemy(esper.Processor):

    def __init__(self, spawn_x: float, spawn_y: float):
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y

    def process(self, delta_time):
        players = list(self.world.get_components(Position, Velocity, Size, Active, CTagPlayer))
        enemies = list(self.world.get_components(Position, Size, Active, CTagEnemy))

        for p_ent, (p_pos, p_vel, p_size, _, _) in players:
            for e_ent, (e_pos, e_size, _, _) in enemies:
                if self._aabb(p_pos, p_size, e_pos, e_size):
                    p_pos.x = self.spawn_x
                    p_pos.y = self.spawn_y
                    p_vel.dx = 0.0
                    p_vel.dy = 0.0
                    self.world.delete_entity(e_ent)
                    break

    @staticmethod
    def _aabb(p1: Position, s1: Size, p2: Position, s2: Size) -> bool:
        return not (
            p1.x + s1.width  <= p2.x or
            p2.x + s2.width  <= p1.x or
            p1.y + s1.height <= p2.y or
            p2.y + s2.height <= p1.y
        )
