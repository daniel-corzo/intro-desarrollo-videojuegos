"""Sistema de entrada: lee teclado y ratón, actualiza InputCommand (patrón Command)."""

import pygame
import esper

from src.ecs.components.input_command import InputCommand


class SystemInput(esper.Processor):

    def __init__(self):
        self._prev_mouse_down = False
        self._prev_space = False

    def process(self, delta_time):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        space_pressed = bool(keys[pygame.K_SPACE])

        for _, (inp,) in self.world.get_components(InputCommand):
            inp.actions["PLAYER_LEFT"]  = bool(keys[pygame.K_LEFT])
            inp.actions["PLAYER_RIGHT"] = bool(keys[pygame.K_RIGHT])
            inp.actions["PLAYER_UP"]    = bool(keys[pygame.K_UP])
            inp.actions["PLAYER_DOWN"]  = bool(keys[pygame.K_DOWN])

            # FIRE es edge-triggered: solo True en el frame en que se presiona
            inp.actions["PLAYER_FIRE"] = mouse_pressed and not self._prev_mouse_down
            # SPECIAL es edge-triggered: solo True en el frame en que se presiona
            inp.actions["PLAYER_SPECIAL"] = space_pressed and not self._prev_space
            inp.mouse_x = mouse_pos[0]
            inp.mouse_y = mouse_pos[1]

        self._prev_mouse_down = mouse_pressed
        self._prev_space = space_pressed
