import typing as t

import moderngl
import pygame

from ..utils import TEXTURES

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("Textures",)


class Textures:
    def __init__(self, app: "Mugen") -> None:
        self.app = app
        self.ctx = self.app.ctx
        self._textures: dict[str, moderngl.Texture] = {}
        self._load_textures()
        self.app.logger.info(f"Loaded {len(self._textures)} textures.")
        self.get_texture("TEST").use()

    def _load_texture(self, path: str) -> moderngl.Texture:
        image = pygame.image.load(path)
        image = pygame.transform.flip(image, flip_x=True, flip_y=True)
        texture = self.ctx.texture(image.get_size(), 4, pygame.image.tostring(image, "RGBA", True))
        texture.anisotropy = 32
        texture.build_mipmaps()
        texture.filter = moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR
        return texture

    def _load_textures(self) -> None:
        self.app.logger.info("Loading textures...")
        for texture in TEXTURES:
            self.app.logger.info(f"Loading texture '{texture.name}' from '{texture.value}'")
            self._textures[texture.name] = self._load_texture(texture.value.as_posix())
        self.app.logger.info("Textures loaded.")

    def get_texture(self, name: str) -> moderngl.Texture:
        if name not in self._textures:
            raise ValueError(f"Texture '{name}' not found. Valid textures are: {list(self._textures.keys())}")
        return self._textures[name]
