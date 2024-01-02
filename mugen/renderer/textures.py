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
        self._textures: dict[str, moderngl.Texture | moderngl.TextureArray] = {}
        self._load_textures()
        self.app.logger.info(f"Loaded {len(self._textures)} textures.")
        self.get_texture("TEST").use(location=0)
        self.get_texture("TEXTURE_ARRAY_0").use(location=1)
        self.get_texture("WATER").use(location=2)

    def _load_texture(self, path: str, tex_array: bool = False) -> moderngl.Texture | moderngl.TextureArray:
        image = pygame.image.load(path)
        image = pygame.transform.flip(image, flip_x=True, flip_y=False)
        texture: moderngl.Texture | moderngl.TextureArray
        if tex_array:
            layers = 3 * image.get_height() // image.get_width()
            texture = self.ctx.texture_array(
                (image.get_width(), image.get_height() // layers, layers),
                4,
                pygame.image.tostring(image, "RGBA", False),
            )
        else:
            texture = self.ctx.texture(image.get_size(), 4, pygame.image.tostring(image, "RGBA", False))
        texture.anisotropy = 32
        texture.build_mipmaps()
        texture.filter = moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR
        return texture

    def _load_textures(self) -> None:
        self.app.logger.info("Loading textures...")
        for texture in TEXTURES:
            self.app.logger.info(f"Loading texture '{texture.name}' from '{texture.value}'")
            self._textures[texture.name] = self._load_texture(
                texture.value.as_posix(), tex_array="array" in texture.name.lower()
            )
        self.app.logger.info("Textures loaded.")

    def get_texture(self, name: str) -> moderngl.Texture | moderngl.TextureArray:
        if name not in self._textures:
            raise ValueError(f"Texture '{name}' not found. Valid textures are: {list(self._textures.keys())}")
        return self._textures[name]
