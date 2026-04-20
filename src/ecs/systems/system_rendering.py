"""Sistema de renderizado: limpia la pantalla y dibuja todos los sprites activos."""

import esper

from src.ecs.components.position import Position
from src.ecs.components.active import Active
from src.ecs.components.surface import Surface


class SystemRendering(esper.Processor):

    def __init__(self, screen, bg_color):
        self.screen = screen
        self.bg_color = bg_color

    def process(self, delta_time):
        self.screen.fill(self.bg_color)

        for _, (pos, c_surf, _) in self.world.get_components(Position, Surface, Active):
            self.screen.blit(c_surf.surface, (pos.x, pos.y), c_surf.area)
