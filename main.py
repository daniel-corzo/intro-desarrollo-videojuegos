#!/usr/bin/python3
"""Función Main"""

import asyncio
from src.engine.game_engine import GameEngine


async def main():
    engine = GameEngine()
    await engine.run()


if __name__ == "__main__":
    asyncio.run(main())
