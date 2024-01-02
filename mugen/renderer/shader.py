import pathlib
import typing as t

import moderngl

from ..utils import SHADERS, WORLD

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("Shader",)


class Shader:
    def __init__(self, *, app: "Mugen") -> None:
        self.app = app
        self.ctx = app.ctx
        self._player = app._player
        self._shaders: dict[str, moderngl.Program] = {}

        self._load_shaders()

        for name in self._shaders:
            self._set_uniforms(name)

    def _set_uniforms(self, name: str) -> None:
        self.get_program(name)["uProjection"].write(self._player._projection)  # type: ignore
        if name == "CLOUD":
            self.get_program(name)["center"].value = WORLD.CENTER_XZ  # type: ignore
            self.get_program(name)["cloudScale"].value = WORLD.CLOUD_SCALE  # type: ignore
        elif name == "CHUNK" or name == "CUBE":
            self.get_program(name)["uModel"].write(self._player._view)  # type: ignore
            self.get_program(name)["uTexture"].value = 1 if name == "CHUNK" else 0  # type: ignore
        elif name == "WATER":
            self.get_program(name)["uTexture"].value = 2  # type: ignore
            self.get_program(name)["waterArea"].value = WORLD.WATER_AREA  # type: ignore
        if name == "CLOUD" or name == "CHUNK":
            self.get_program(name)["bgColor"].write(WORLD.BG_COLOR)  # type: ignore
        if name == "CHUNK" or name == "WATER":
            self.get_program(name)["waterLine"].value = WORLD.WATER_LINE  # type: ignore

    def _load_shaders(self) -> None:
        self.app.logger.info("Loading shaders...")
        _names: set[str] = {shader.name.split("_")[0] for shader in SHADERS}
        for name in _names:
            vert: pathlib.Path = getattr(SHADERS, f"{name}_VERT")
            frag: pathlib.Path = getattr(SHADERS, f"{name}_FRAG")
            self.app.logger.debug(f"Loading {name} shader...")
            self._shaders[name] = self._load_shader(vert, frag)
        self.app.logger.info("Loaded shaders.")

    def _load_shader(self, vert: pathlib.Path, frag: pathlib.Path) -> moderngl.Program:
        self.app.logger.debug(f"Loading {vert.name} and {frag.name}...")
        return self.ctx.program(vertex_shader=vert.read_text(), fragment_shader=frag.read_text())

    def get_program(self, name: str) -> moderngl.Program:
        if name not in self._shaders:
            raise ValueError(f"Invalid shader program! Valid: {', '.join(self._shaders.keys())}")
        return self._shaders[name]

    def update(self) -> None:
        for name in self._shaders:
            self.get_program(name)["uView"].write(self._player._view)  # type: ignore
