"""Sistema de spawn: crea rectángulos en el momento indicado por el nivel."""

import math
import random
import esper

from src.ecs.components.enemy_spawner import EnemySpawner
from src.ecs.components.position import Position
from src.ecs.components.size import Size
from src.ecs.components.velocity import Velocity
from src.ecs.components.color import Color
from src.ecs.components.active import Active
from src.ecs.components.c_tag_enemy import CTagEnemy


class SystemEnemySpawner(esper.Processor):

    def __init__(self):
        self.elapsed_time = 0.0

    def process(self, delta_time):
        self.elapsed_time += delta_time

        for _, spawner in self.world.get_component(EnemySpawner):
            for event in spawner.spawn_events:
                if event["spawned"]:
                    continue
                if self.elapsed_time >= event["time"]:
                    self._spawn(event)
                    event["spawned"] = True

    def _spawn(self, event):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(event["speed_min"], event["speed_max"])
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed

        pos = event["position"]
        sz = event["size"]
        col = event["color"]

        self.world.create_entity(
            Position(x=pos["x"], y=pos["y"]),
            Velocity(dx=dx, dy=dy),
            Size(width=sz["x"], height=sz["y"]),
            Color(r=col["r"], g=col["g"], b=col["b"]),
            Active(),
            CTagEnemy()
        )
