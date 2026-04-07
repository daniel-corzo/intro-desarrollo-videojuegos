"""Sistema de entrada: lee teclado y ratón, actualiza CInputCommand (patrón Command)."""

import pygame
import esper

from src.ecs.components.c_input_command import CInputCommand


class SystemInput(esper.Processor):

    def __init__(self):
        self._prev_mouse_down = False

    def process(self, delta_time):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()

        for _, (inp,) in self.world.get_components(CInputCommand):
            inp.actions["PLAYER_LEFT"]  = bool(keys[pygame.K_LEFT])
            inp.actions["PLAYER_RIGHT"] = bool(keys[pygame.K_RIGHT])
            inp.actions["PLAYER_UP"]    = bool(keys[pygame.K_UP])
            inp.actions["PLAYER_DOWN"]  = bool(keys[pygame.K_DOWN])

            # FIRE es edge-triggered: solo True en el frame en que se presiona
            inp.actions["PLAYER_FIRE"] = mouse_pressed and not self._prev_mouse_down
            inp.mouse_x = mouse_pos[0]
            inp.mouse_y = mouse_pos[1]

        self._prev_mouse_down = mouse_pressed
