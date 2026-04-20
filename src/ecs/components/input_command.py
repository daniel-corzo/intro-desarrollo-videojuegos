from dataclasses import dataclass, field


@dataclass
class InputCommand:
    """
    Almacena el estado de entrada del jugador siguiendo el patrón Command.

    actions: mapa de nombre de acción → bool (True = acción activa este frame)
    mouse_x / mouse_y: posición del ratón en el momento de PLAYER_FIRE
    """
    actions: dict = field(default_factory=lambda: {
        "PLAYER_LEFT":    False,
        "PLAYER_RIGHT":   False,
        "PLAYER_UP":      False,
        "PLAYER_DOWN":    False,
        "PLAYER_FIRE":    False,
        "PLAYER_SPECIAL": False,
    })
    mouse_x: float = 0.0
    mouse_y: float = 0.0
