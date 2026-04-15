"""Sistema de spawn: crea enemigos en el momento indicado por el nivel."""

import math
import random
import pygame
import esper

from src.ecs.components.enemy_spawner import EnemySpawner
from src.ecs.components.position import Position
from src.ecs.components.velocity import Velocity
from src.ecs.components.active import Active
from src.ecs.components.tag_enemy import TagEnemy
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_animation import CAnimation, AnimationData
from src.ecs.components.c_hunter_state import CHunterState, HunterFSM


class SystemEnemySpawner(esper.Processor):

    def __init__(self):
        self.elapsed_time = 0.0

    def process(self, delta_time):
        self.elapsed_time += delta_time

        for _, spawner in self.world.get_component(EnemySpawner):
            for event in spawner.spawn_events:
                if event["spawned"]:
                    continue
                if self.elapsed_time >= event["time"]:
                    self._spawn(event)
                    event["spawned"] = True

    def _spawn(self, event):
        pos = event["position"]
        surface: pygame.Surface = event["surface"]
        is_hunter = event["enemy_type_name"] == "Hunter"

        if is_hunter:
            self._spawn_hunter(pos, surface, event)
        else:
            self._spawn_asteroid(pos, surface, event)

    # -------------------------------------------------------------------------
    def _spawn_asteroid(self, pos, surface, event):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(event["speed_min"], event["speed_max"])
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed

        w = surface.get_width()
        h = surface.get_height()

        self.world.create_entity(
            Position(x=float(pos["x"]), y=float(pos["y"])),
            Velocity(dx=dx, dy=dy),
            CSurface(surface=surface, area=pygame.Rect(0, 0, w, h)),
            Active(),
            TagEnemy()
        )

    def _spawn_hunter(self, pos, surface, event):
        anim_cfg = event["animations_cfg"]
        num_frames = anim_cfg["number_frames"]
        frame_w = surface.get_width() // num_frames
        frame_h = surface.get_height()

        animations = {}
        for a in anim_cfg["list"]:
            animations[a["name"]] = AnimationData(
                name=a["name"],
                start=a["start"],
                end=a["end"],
                framerate=a["framerate"]
            )

        spawn_x = float(pos["x"])
        spawn_y = float(pos["y"])

        self.world.create_entity(
            Position(x=spawn_x, y=spawn_y),
            Velocity(dx=0.0, dy=0.0),
            CSurface(surface=surface, area=pygame.Rect(0, 0, frame_w, frame_h)),
            CAnimation(
                animations=animations,
                current_animation="IDLE",
                current_frame=animations["IDLE"].start,
                elapsed_time=0.0,
                number_frames=num_frames,
                frame_width=frame_w,
                looping=True
            ),
            CHunterState(
                origin_x=spawn_x + frame_w / 2,
                origin_y=spawn_y + frame_h / 2,
                velocity_chase=event["velocity_chase"],
                velocity_return=event["velocity_return"],
                distance_start_chase=event["distance_start_chase"],
                distance_start_return=event["distance_start_return"],
                state=HunterFSM.IDLE
            ),
            Active(),
            TagEnemy()
        )
