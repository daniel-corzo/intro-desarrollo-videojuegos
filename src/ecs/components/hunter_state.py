"""Componente HunterState: estado de la IA del enemigo Hunter."""

from dataclasses import dataclass, field
from enum import Enum


class HunterFSM(Enum):
    IDLE = "IDLE"
    CHASING = "CHASING"
    RETURNING = "RETURNING"


@dataclass
class HunterState:
    """
    Almacena la configuración y el estado de la máquina de estados del Hunter.

    origin_x / origin_y       : posición de origen (punto de aparición)
    velocity_chase            : velocidad al perseguir al jugador
    velocity_return           : velocidad al regresar al origen
    distance_start_chase      : distancia máxima al jugador para iniciar persecución
    distance_start_return     : distancia máxima al origen antes de forzar retorno
    state                     : estado actual de la FSM
    """
    origin_x: float
    origin_y: float
    velocity_chase: float
    velocity_return: float
    distance_start_chase: float
    distance_start_return: float
    state: HunterFSM = field(default=HunterFSM.IDLE)
