"""ServiceLocator: acceso centralizado y cacheado a sonidos, imágenes y fuentes."""

import pygame


class ImageService:
    def __init__(self):
        self._cache: dict[str, pygame.Surface] = {}

    def get(self, path: str) -> pygame.Surface:
        if path not in self._cache:
            self._cache[path] = pygame.image.load(path).convert_alpha()
        return self._cache[path]


class SoundService:
    def __init__(self):
        self._cache: dict[str, pygame.mixer.Sound] = {}
        self._channels: dict[str, pygame.mixer.Channel] = {}

    def get(self, path: str) -> pygame.mixer.Sound:
        if path not in self._cache:
            self._cache[path] = pygame.mixer.Sound(path)
        return self._cache[path]

    def play(self, path: str, loops: int = 0) -> None:
        sound = self.get(path)
        ch = sound.play(loops=loops)
        if ch is not None:
            self._channels[path] = ch

    def stop(self, path: str) -> None:
        if path in self._channels:
            self._channels[path].stop()
            del self._channels[path]
        elif path in self._cache:
            self._cache[path].stop()


class FontService:
    def __init__(self):
        self._cache: dict[tuple[str, int], pygame.font.Font] = {}

    def get(self, path: str, size: int) -> pygame.font.Font:
        key = (path, size)
        if key not in self._cache:
            self._cache[key] = pygame.font.Font(path, size)
        return self._cache[key]


class ServiceLocator:
    images: ImageService = ImageService()
    sounds: SoundService = SoundService()
    fonts: FontService = FontService()

    @classmethod
    def reset(cls) -> None:
        cls.images = ImageService()
        cls.sounds = SoundService()
        cls.fonts = FontService()
