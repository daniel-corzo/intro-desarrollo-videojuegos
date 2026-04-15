"""Componente Animation: controla el flujo de animación de un sprite sheet."""

from dataclasses import dataclass, field


@dataclass
class AnimationData:
    """Define una animación nombrada dentro del sprite sheet."""
    name: str
    start: int      # primer cuadro (0-based, absoluto en el sheet)
    end: int        # último cuadro (inclusivo)
    framerate: int  # cuadros por segundo


@dataclass
class Animation:
    """
    Estado de animación de una entidad con sprite sheet horizontal.

    animations        : dict nombre→AnimationData con todas las animaciones disponibles
    current_animation : nombre de la animación activa
    current_frame     : índice absoluto del cuadro actual en el sheet
    elapsed_time      : tiempo acumulado desde el último cambio de cuadro
    number_frames     : total de cuadros en el sheet
    frame_width       : ancho en píxeles de un cuadro = surface_width // number_frames
    looping           : True → la animación se repite; False → se detiene en el último cuadro
    """
    animations: dict = field(default_factory=dict)
    current_animation: str = ""
    current_frame: int = 0
    elapsed_time: float = 0.0
    number_frames: int = 1
    frame_width: int = 0
    looping: bool = True
