import typing as t

from ..components import World
from .marker import VoxelMarker

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("Scene",)


class Scene:
    def __init__(self, app: "Mugen") -> None:
        self.app = app
        self.world = World(self.app)
        self.marker = VoxelMarker(self.world.chunk_manager)

    def render(self) -> None:
        self.world.render()
        self.marker.render()

    def update(self) -> None:
        self.world.update()
        self.marker.update()
