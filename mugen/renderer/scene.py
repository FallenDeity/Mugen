import typing as t

import moderngl

from ..components import Clouds, Water, World
from .marker import VoxelMarker

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("Scene",)


class Scene:
    def __init__(self, app: "Mugen") -> None:
        self.app = app
        self.world = World(self.app)
        self.marker = VoxelMarker(self.world.chunk_manager)
        self.clouds = Clouds(self.app)
        self.water = Water(self.app)

    def render(self) -> None:
        self.app.ctx.disable(moderngl.CULL_FACE)
        self.clouds.render()
        self.water.render()
        self.app.ctx.enable(moderngl.CULL_FACE)

        self.world.render()
        self.marker.render()

    def update(self) -> None:
        self.world.update()
        self.marker.update()
        self.clouds.update()
