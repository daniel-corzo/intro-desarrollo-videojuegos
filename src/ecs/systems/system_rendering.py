"""Sistema de renderizado: limpia la pantalla y dibuja todos los rectángulos."""

import pygame
import esper

from src.ecs.components.position import Position
from src.ecs.components.size import Size
from src.ecs.components.color import Color
from src.ecs.components.active import Active


class SystemRendering(esper.Processor):

    def __init__(self, screen, bg_color):
        self.screen = screen
        self.bg_color = bg_color

    def process(self, delta_time):
        self.screen.fill(self.bg_color)

        for _, (pos, size, color, _) in self.world.get_components(Position, Size, Color, Active):
            pygame.draw.rect(
                self.screen,
                (color.r, color.g, color.b),
                pygame.Rect(pos.x, pos.y, size.width, size.height)
            )

        pygame.display.flip()
