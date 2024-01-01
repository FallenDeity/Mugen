import typing as t

from ..components import Chunk

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("Scene",)


class Scene:
    def __init__(self, app: "Mugen") -> None:
        self.app = app
        self.chunk = Chunk(self.app)

    def render(self) -> None:
        self.chunk.render()

    def update(self) -> None:
        pass
