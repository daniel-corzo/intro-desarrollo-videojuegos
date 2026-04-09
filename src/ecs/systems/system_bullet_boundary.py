"""Sistema de límites de balas: elimina las balas que salen de la pantalla."""

import esper

from src.ecs.components.position import Position
from src.ecs.components.size import Size
from src.ecs.components.active import Active
from src.ecs.components.tag_bullet import TagBullet


class SystemBulletBoundary(esper.Processor):

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def process(self, delta_time):
        to_delete = []
        for ent, (pos, size, _, _) in self.world.get_components(Position, Size, Active, TagBullet):
            if (pos.x + size.width < 0 or pos.x > self.screen_width or
                    pos.y + size.height < 0 or pos.y > self.screen_height):
                to_delete.append(ent)

        for ent in to_delete:
            self.world.delete_entity(ent)
