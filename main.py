#!/usr/bin/python3
"""Función Main"""

import asyncio
import pygame
from src.engine.game_engine import GameEngine


async def main():
    engine = GameEngine()
    await engine.run()


asyncio.run(main())
