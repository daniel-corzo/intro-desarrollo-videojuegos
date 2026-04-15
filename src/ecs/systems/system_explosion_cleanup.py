"""Sistema de limpieza de explosiones: elimina la entidad al terminar la animación."""

import esper

from src.ecs.components.active import Active
from src.ecs.components.animation import Animation
from src.ecs.components.tag_explosion import TagExplosion


class SystemExplosionCleanup(esper.Processor):
    """
    Elimina las entidades de explosión cuya animación haya terminado.
    SystemAnimation deja de avanzar cuadros cuando looping=False y
    current_frame >= anim.end, por lo que basta con verificar esa condición.
    """

    def process(self, delta_time):
        to_delete = []
        for ent, (c_anim, _, _) in self.world.get_components(Animation, Active, TagExplosion):
            if c_anim.looping:
                continue
            anim = c_anim.animations.get(c_anim.current_animation)
            if anim and c_anim.current_frame >= anim.end:
                to_delete.append(ent)

        for ent in to_delete:
            self.world.delete_entity(ent)
