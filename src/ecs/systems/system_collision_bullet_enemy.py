"""Sistema de colisiones bala-enemigo: elimina ambos al tocarse."""

import esper

from src.ecs.components.position import Position
from src.ecs.components.size import Size
from src.ecs.components.active import Active
from src.ecs.components.c_tag_bullet import CTagBullet
from src.ecs.components.c_tag_enemy import CTagEnemy


class SystemCollisionBulletEnemy(esper.Processor):

    def process(self, delta_time):
        bullets  = list(self.world.get_components(Position, Size, Active, CTagBullet))
        enemies  = list(self.world.get_components(Position, Size, Active, CTagEnemy))

        for b_ent, (b_pos, b_size, _, _) in bullets:
            for e_ent, (e_pos, e_size, _, _) in enemies:
                if self._aabb(b_pos, b_size, e_pos, e_size):
                    self.world.delete_entity(b_ent)
                    self.world.delete_entity(e_ent)
                    break  # la bala ya no existe, pasar a la siguiente

    @staticmethod
    def _aabb(p1: Position, s1: Size, p2: Position, s2: Size) -> bool:
        return not (
            p1.x + s1.width  <= p2.x or
            p2.x + s2.width  <= p1.x or
            p1.y + s1.height <= p2.y or
            p2.y + s2.height <= p1.y
        )
