"""Componente Surface: textura y área de recorte para una entidad con sprite."""

import pygame
from dataclasses import dataclass


@dataclass
class Surface:
    """
    Reemplaza Size + Color. Almacena la superficie completa (sprite sheet o imagen
    simple) y el rect del cuadro activo dentro de ella.

    surface : pygame.Surface  — imagen completa cargada en memoria
    area    : pygame.Rect     — sub-rect del cuadro actual (se actualiza con la animación)
                                width/height de area se usan en colisiones y bordes.
    """
    surface: pygame.Surface
    area: pygame.Rect

    @classmethod
    def from_text(cls, text: str, font: pygame.font.Font, color: tuple) -> "Surface":
        rendered = font.render(text, True, color)
        return cls(surface=rendered, area=rendered.get_rect())
