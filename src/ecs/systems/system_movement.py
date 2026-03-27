"""Sistema de movimiento: actualiza la posición según la velocidad."""

import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active


class SystemMovement(esper.Processor):

    def process(self, delta_time):
        for _, (pos, vel, _) in self.world.get_components(Position, Velocity, Active):
            pos.x += vel.dx * delta_time
            pos.y += vel.dy * delta_time
