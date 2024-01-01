import dataclasses
import typing as t

import moderngl
from nptyping import NDArray, Shape

if t.TYPE_CHECKING:
    from mugen import Mugen


@dataclasses.dataclass
class BaseMesh:
    app: "Mugen"
    vbo_format: str = dataclasses.field(init=False)
    attrs: tuple[str, ...] = dataclasses.field(init=False)
    ctx: moderngl.Context = dataclasses.field(init=False, repr=False)
    program: moderngl.Program = dataclasses.field(init=False, repr=False)
    vao: moderngl.VertexArray = dataclasses.field(init=False)
    vertices: NDArray[Shape["*, *"], t.Any] = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.ctx = self.app.ctx
        self.vao = self.get_vao(self.vertices)

    def get_vao(self, vertices: NDArray[Shape["*, *"], t.Any]) -> moderngl.VertexArray:
        vbo: moderngl.Buffer = self.ctx.buffer(vertices)
        vao: moderngl.VertexArray = self.ctx.vertex_array(
            self.program, [(vbo, self.vbo_format, *self.attrs)], skip_errors=True
        )
        return vao

    def render(self) -> None:
        self.vao.render()
