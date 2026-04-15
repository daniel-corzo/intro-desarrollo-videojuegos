"""Sistema de rebote: invierte la velocidad cuando el sprite toca un borde.

Solo aplica a asteroides (TagEnemy sin CHunterState). Los Hunters manejan
su propio movimiento en SystemHunterMovement.
"""

import esper

from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active
from src.ecs.components.tag_enemy import TagEnemy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_hunter_state import CHunterState


class SystemScreenBounce(esper.Processor):

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def process(self, delta_time):
        for ent, (pos, vel, c_surf, _, _) in self.world.get_components(
                Position, Velocity, CSurface, Active, TagEnemy):

            # Los Hunters tienen su propio sistema de movimiento, no rebotan
            if self.world.has_component(ent, CHunterState):
                continue

            w = c_surf.area.width
            h = c_surf.area.height

            if pos.x < 0:
                pos.x = 0
                vel.dx = abs(vel.dx)

            if pos.x + w > self.screen_width:
                pos.x = self.screen_width - w
                vel.dx = -abs(vel.dx)

            if pos.y < 0:
                pos.y = 0
                vel.dy = abs(vel.dy)

            if pos.y + h > self.screen_height:
                pos.y = self.screen_height - h
                vel.dy = -abs(vel.dy)
