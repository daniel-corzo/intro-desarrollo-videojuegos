"""Sistema de límites del jugador: lo confina dentro de la pantalla."""

import esper

from src.ecs.components.position import Position
from src.ecs.components.size import Size
from src.ecs.components.active import Active
from src.ecs.components.tag_player import TagPlayer


class SystemPlayerBoundary(esper.Processor):

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def process(self, delta_time):
        for _, (pos, size, _, _) in self.world.get_components(Position, Size, Active, TagPlayer):
            pos.x = max(0.0, min(pos.x, self.screen_width  - size.width))
            pos.y = max(0.0, min(pos.y, self.screen_height - size.height))
