"""Sistema de animación: avanza los cuadros de todas las entidades animadas."""

import esper

from src.ecs.components.active import Active
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_animation import CAnimation


class SystemAnimation(esper.Processor):
    """
    Avanza el temporizador de animación y actualiza el área de recorte del sprite.
    Respeta looping=False para animaciones de un solo ciclo (explosiones).
    """

    def process(self, delta_time):
        for _, (c_surf, c_anim, _) in self.world.get_components(CSurface, CAnimation, Active):
            anim = c_anim.animations.get(c_anim.current_animation)
            if anim is None or anim.framerate <= 0:
                continue

            c_anim.elapsed_time += delta_time
            time_per_frame = 1.0 / anim.framerate

            while c_anim.elapsed_time >= time_per_frame:
                # Animación no-looping en el último cuadro: no avanzar más
                if not c_anim.looping and c_anim.current_frame >= anim.end:
                    break
                c_anim.elapsed_time -= time_per_frame
                next_frame = c_anim.current_frame + 1
                if next_frame > anim.end:
                    if c_anim.looping:
                        next_frame = anim.start
                    else:
                        next_frame = anim.end  # Clamp en el último cuadro
                c_anim.current_frame = next_frame

            # Actualizar el área de recorte con el cuadro actual
            c_surf.area.x = c_anim.current_frame * c_anim.frame_width
