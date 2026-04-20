"""Sistema de animación del jugador: MOVE cuando se mueve, IDLE cuando está quieto."""

import esper

from src.ecs.components.active import Active
from src.ecs.components.velocity import Velocity
from src.ecs.components.animation import Animation
from src.ecs.components.tag_player import TagPlayer
from src.engine.service_locator import ServiceLocator


class SystemPlayerAnimation(esper.Processor):

    def __init__(self, move_sound: str):
        self._move_sound = move_sound

    def process(self, delta_time):
        for _, (vel, c_anim, _, _) in self.world.get_components(
                Velocity, Animation, Active, TagPlayer):

            if vel.dx != 0.0 or vel.dy != 0.0:
                target = "MOVE"
            else:
                target = "IDLE"

            if c_anim.current_animation != target:
                c_anim.current_animation = target
                anim = c_anim.animations.get(target)
                if anim:
                    c_anim.current_frame = anim.start
                    c_anim.elapsed_time = 0.0

                if target == "MOVE":
                    ServiceLocator.sounds.play(self._move_sound, loops=-1)
                else:
                    ServiceLocator.sounds.stop(self._move_sound)
