"""Marcador para entidades de HUD (barras, indicadores, etc.)."""

from dataclasses import dataclass


@dataclass
class TagHud:
    key: str = ""
