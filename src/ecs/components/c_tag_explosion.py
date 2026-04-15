"""Componente CTagExplosion: marca a una entidad como explosión."""

from dataclasses import dataclass


@dataclass
class CTagExplosion:
    """Marcador: la entidad es una explosión. Se elimina al terminar su animación."""
    pass
