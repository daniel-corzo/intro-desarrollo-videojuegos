from dataclasses import dataclass


@dataclass
class AppearanceTime:
    spawn_time: float
    spawned: bool = False