import pathlib
import typing as t

import glm
import moderngl

from ..utils import SHADERS

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

        _proj: moderngl.Uniform = self.get_program("CHUNK")["uProjection"]  # type: ignore
        _proj.write(self._player._projection)
        _model: moderngl.Uniform = self.get_program("CHUNK")["uModel"]  # type: ignore
        _model.write(glm.mat4())
        _tex: moderngl.Uniform = self.get_program("CHUNK")["uTexture"]  # type: ignore
        _tex.value = 0

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
        _view: moderngl.Uniform = self.get_program("CHUNK")["uView"]  # type: ignore
        _view.write(self._player._view)
