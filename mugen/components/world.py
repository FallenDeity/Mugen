import itertools
import typing as t

import numpy as np

from ..utils import CHUNK, WORLD
from .chunk import Chunk
from .handler import ChunkManager

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("World",)


class World:
    def __init__(self, app: "Mugen") -> None:
        self.app = app
        self.chunks: list[Chunk | None] = [None] * WORLD.VOLUME
        self.voxels = np.empty([WORLD.VOLUME, CHUNK.VOLUME], dtype=np.uint8)
        self._build_chunks()
        self._build_meshes()
        self.chunk_manager = ChunkManager(world=self)

    def _build_meshes(self) -> None:
        for chunk in self.chunks:
            if chunk is not None:
                chunk._build_mesh()

    def _build_chunks(self) -> None:
        for x, y, z in itertools.product(range(WORLD.WIDTH), range(WORLD.HEIGHT), range(WORLD.DEPTH)):
            chunk = Chunk(world=self, app=self.app, position=(x, y, z))
            chunk_idx = x + WORLD.WIDTH * z + WORLD.AREA * y
            self.chunks[chunk_idx] = chunk
            self.voxels[chunk_idx] = chunk._build_voxels()
            chunk.voxels = self.voxels[chunk_idx]

    def render(self) -> None:
        for chunk in self.chunks:
            if chunk is not None:
                chunk.render()

    def update(self) -> None:
        self.chunk_manager.update()
