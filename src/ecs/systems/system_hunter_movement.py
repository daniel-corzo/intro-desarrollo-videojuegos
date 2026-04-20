"""Sistema de movimiento del Hunter: FSM que persigue al jugador y regresa al origen."""

import math
import esper

from src.ecs.components.active import Active
from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.surface import Surface
from src.ecs.components.hunter_state import HunterState, HunterFSM
from src.ecs.components.tag_enemy import TagEnemy
from src.ecs.components.tag_player import TagPlayer
from src.engine.service_locator import ServiceLocator

_ARRIVAL_THRESHOLD = 8.0  # píxeles de tolerancia para considerar "llegado al origen"


class SystemHunterMovement(esper.Processor):

    def __init__(self):
        self._player_eid = None  # entidad del jugador cacheada

    def process(self, delta_time):
        player_cx, player_cy = self._get_player_center()
        if player_cx is None:
            return

        for _, (pos, vel, c_surf, hunter, _, _) in self.world.get_components(
                Position, Velocity, Surface, HunterState, Active, TagEnemy):

            hx = pos.x + c_surf.area.width / 2
            hy = pos.y + c_surf.area.height / 2

            dist_to_player = math.hypot(player_cx - hx, player_cy - hy)
            dist_to_origin = math.hypot(hunter.origin_x - hx, hunter.origin_y - hy)

            if hunter.state == HunterFSM.IDLE:
                vel.dx = 0.0
                vel.dy = 0.0
                if dist_to_player < hunter.distance_start_chase:
                    hunter.state = HunterFSM.CHASING
                    if hunter.sound_chase:
                        ServiceLocator.sounds.play(hunter.sound_chase)

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
        # Usar la entidad cacheada si sigue viva y activa
        if self._player_eid is not None:
            try:
                pos = self.world.component_for_entity(self._player_eid, Position)
                c_surf = self.world.component_for_entity(self._player_eid, Surface)
                return pos.x + c_surf.area.width / 2, pos.y + c_surf.area.height / 2
            except KeyError:
                self._player_eid = None  # entidad eliminada, volver a buscar

        # Búsqueda completa solo cuando no hay caché válido
        for eid, (pos, c_surf, _, _) in self.world.get_components(
                Position, Surface, Active, TagPlayer):
            self._player_eid = eid
            return pos.x + c_surf.area.width / 2, pos.y + c_surf.area.height / 2

        return None, None

    @staticmethod
    def _set_velocity_toward(vel: Velocity, from_x, from_y, to_x, to_y, speed):
        dx = to_x - from_x
        dy = to_y - from_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            vel.dx = (dx / dist) * speed
            vel.dy = (dy / dist) * speed
