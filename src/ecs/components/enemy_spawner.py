"""Componente CEnemySpawner: contiene la lista de eventos de spawn del nivel."""

from dataclasses import dataclass, field


@dataclass
class EnemySpawner:
    """
    Componente que almacena los eventos de spawn del nivel.
    Existe una única entidad con este componente en el mundo.

    spawn_events: lista de dicts, cada uno con:
        - time      (float)  segundos en que debe aparecer
        - position  (dict)   {"x": float, "y": float}
        - size      (dict)   {"x": float, "y": float}
        - color     (dict)   {"r": int, "g": int, "b": int}
        - speed_min (float)
        - speed_max (float)
        - spawned   (bool)   True cuando ya fue creado
    """
    spawn_events: list = field(default_factory=list)
