"""Sistema de renderizado de texto: re-genera la Surface cuando Text.dirty es True."""

import esper

from src.ecs.components.text import Text
from src.ecs.components.surface import Surface
from src.engine.service_locator import ServiceLocator


class SystemTextRendering(esper.Processor):

    def process(self, delta_time):
        for _, (txt, surf) in self.world.get_components(Text, Surface):
            if not txt.dirty:
                continue
            font = ServiceLocator.fonts.get(txt.font_path, txt.font_size)
            rendered = font.render(txt.text, True, txt.color)
            surf.surface = rendered
            surf.area = rendered.get_rect()
            txt.dirty = False
