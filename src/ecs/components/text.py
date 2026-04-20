"""Componente Text: datos para renderizar texto dinámico."""

from dataclasses import dataclass, field


@dataclass
class Text:
    text: str
    font_path: str
    font_size: int
    color: tuple
    dirty: bool = field(default=True)
