"""Sistema de animación del jugador: MOVE cuando se mueve, IDLE cuando está quieto."""

import esper

from src.ecs.components.active import Active
from src.ecs.components.velocity import Velocity
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tag_player import TagPlayer


class SystemPlayerAnimation(esper.Processor):

    def process(self, delta_time):
        for _, (vel, c_anim, _, _) in self.world.get_components(
                Velocity, CAnimation, Active, TagPlayer):

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
