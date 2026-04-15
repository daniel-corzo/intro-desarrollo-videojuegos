"""Sistema de animación del Hunter: MOVE cuando se mueve, IDLE cuando está quieto."""

import esper

from src.ecs.components.active import Active
from src.ecs.components.velocity import Velocity
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_hunter_state import CHunterState, HunterFSM
from src.ecs.components.tag_enemy import TagEnemy


class SystemHunterAnimation(esper.Processor):

    def process(self, delta_time):
        for _, (vel, c_anim, hunter, _, _) in self.world.get_components(
                Velocity, CAnimation, CHunterState, Active, TagEnemy):

            if hunter.state in (HunterFSM.CHASING, HunterFSM.RETURNING):
                target = "MOVE"
            else:
                target = "IDLE"

            if c_anim.current_animation != target:
                c_anim.current_animation = target
                anim = c_anim.animations.get(target)
                if anim:
                    c_anim.current_frame = anim.start
                    c_anim.elapsed_time = 0.0
