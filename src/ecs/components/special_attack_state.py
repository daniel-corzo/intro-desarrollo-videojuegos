"""Estado de la habilidad especial del jugador."""

from dataclasses import dataclass, field


@dataclass
class SpecialAttackState:
    cooldown_max: float
    cooldown_remaining: float = field(default=0.0)

    @property
    def ready(self) -> bool:
        return self.cooldown_remaining <= 0.0
