"""Sistema de movimiento del Hunter: FSM que persigue al jugador y regresa al origen."""

import math
import esper

from src.ecs.components.active import Active
from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_hunter_state import CHunterState, HunterFSM
from src.ecs.components.tag_enemy import TagEnemy
from src.ecs.components.tag_player import TagPlayer

_ARRIVAL_THRESHOLD = 8.0  # píxeles de tolerancia para considerar "llegado al origen"


class SystemHunterMovement(esper.Processor):

    def process(self, delta_time):
        # Obtener posición del jugador (centro)
        player_cx, player_cy = self._get_player_center()
        if player_cx is None:
            return

        for _, (pos, vel, c_surf, hunter, _, _) in self.world.get_components(
                Position, Velocity, CSurface, CHunterState, Active, TagEnemy):

            # Centro del hunter
            hx = pos.x + c_surf.area.width / 2
            hy = pos.y + c_surf.area.height / 2

            dist_to_player = math.hypot(player_cx - hx, player_cy - hy)
            dist_to_origin = math.hypot(hunter.origin_x - hx, hunter.origin_y - hy)

            if hunter.state == HunterFSM.IDLE:
                vel.dx = 0.0
                vel.dy = 0.0
                if dist_to_player < hunter.distance_start_chase:
                    hunter.state = HunterFSM.CHASING

            elif hunter.state == HunterFSM.CHASING:
                if dist_to_origin > hunter.distance_start_return:
                    hunter.state = HunterFSM.RETURNING
                else:
                    self._set_velocity_toward(vel, hx, hy, player_cx, player_cy,
                                              hunter.velocity_chase)

            elif hunter.state == HunterFSM.RETURNING:
                if dist_to_origin < _ARRIVAL_THRESHOLD:
                    hunter.state = HunterFSM.IDLE
                    vel.dx = 0.0
                    vel.dy = 0.0
                    pos.x = hunter.origin_x - c_surf.area.width / 2
                    pos.y = hunter.origin_y - c_surf.area.height / 2
                else:
                    self._set_velocity_toward(vel, hx, hy, hunter.origin_x, hunter.origin_y,
                                              hunter.velocity_return)

    # -------------------------------------------------------------------------
    def _get_player_center(self):
        for _, (pos, c_surf, _, _) in self.world.get_components(Position, CSurface, Active, TagPlayer):
            cx = pos.x + c_surf.area.width / 2
            cy = pos.y + c_surf.area.height / 2
            return cx, cy
        return None, None

    @staticmethod
    def _set_velocity_toward(vel: Velocity, from_x, from_y, to_x, to_y, speed):
        dx = to_x - from_x
        dy = to_y - from_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            vel.dx = (dx / dist) * speed
            vel.dy = (dy / dist) * speed
