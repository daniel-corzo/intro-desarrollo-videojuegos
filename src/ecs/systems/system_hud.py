"""Sistema HUD: actualiza el texto y la barra de cooldown del especial."""

from __future__ import annotations

import pygame
import esper

from src.ecs.components.text import Text
from src.ecs.components.special_attack_state import SpecialAttackState
from src.ecs.components.tag_player import TagPlayer
from src.ecs.components.tag_hud import TagHud

_BAR_W = 70
_BAR_H = 6
_COLOR_READY  = (100, 255, 120)
_COLOR_CHARGE = (255, 200, 60)


class SystemHud(esper.Processor):

    def __init__(self, screen: pygame.Surface):
        self._screen = screen

    def process(self, delta_time):
        special = None
        for _, (sp, _) in self.world.get_components(SpecialAttackState, TagPlayer):
            special = sp
            break
        if special is None:
            return

        if special.ready:
            new_text = "ESPECIAL: LISTO"
            color = _COLOR_READY
        else:
            secs = special.cooldown_remaining
            new_text = f"ESPECIAL: {secs:.1f}s"
            color = _COLOR_CHARGE

        for _, (txt, hud) in self.world.get_components(Text, TagHud):
            if hud.key == "special_label" and txt.text != new_text:
                txt.text = new_text
                txt.color = color
                txt.dirty = True

        self._draw_bar(special)

    def _draw_bar(self, special: SpecialAttackState):
        if special.ready:
            fill = _BAR_W
            color = _COLOR_READY
        else:
            ratio = 1.0 - (special.cooldown_remaining / special.cooldown_max)
            fill = int(_BAR_W * ratio)
            color = _COLOR_CHARGE

        bar_x, bar_y = 10, 22
        pygame.draw.rect(self._screen, (60, 60, 60), (bar_x, bar_y, _BAR_W, _BAR_H))
        if fill > 0:
            pygame.draw.rect(self._screen, color, (bar_x, bar_y, fill, _BAR_H))
        pygame.draw.rect(self._screen, (200, 200, 200), (bar_x, bar_y, _BAR_W, _BAR_H), 1)
