import typing as t

import glm
import numpy as np
from nptyping import NDArray, Shape, UInt8

from ..renderer.meshes import ChunkMesh
from ..utils import CHUNK

if t.TYPE_CHECKING:
    from mugen import Mugen

    from .world import World


__all__: tuple[str, ...] = ("Chunk",)


class Chunk:
    mesh: ChunkMesh | None = None
    voxels: NDArray[Shape["*, *"], UInt8] | None = None

    def __init__(self, world: "World", app: "Mugen", position: tuple[int, int, int]) -> None:
        self.app = app
        self.world = world
        self.position = position
        self._is_empty = True
        self._model_matrix = glm.translate(glm.mat4(), glm.vec3(*self.position) * CHUNK.SIZE)

    def _build_mesh(self) -> None:
        self.mesh = ChunkMesh(self.app, self)

    def render(self) -> None:
        if not self._is_empty and self.mesh is not None:
            self.mesh.program["uModel"].write(self._model_matrix)  # type: ignore
            self.mesh.render()

    def _build_voxels(self) -> NDArray[Shape["*, *"], UInt8]:
        _voxels = np.zeros(CHUNK.VOLUME, dtype=np.uint8)
        cx, cy, cz = glm.ivec3(self.position) * CHUNK.SIZE
        for x in range(CHUNK.SIZE):
            for z in range(CHUNK.SIZE):
                wx, wz = x + cx, z + cz
                # world_height = int(glm.perlin(glm.vec2(wx, wz) / 100.0) * CHUNK.SIZE + CHUNK.SIZE)
                world_height = int(glm.simplex(glm.vec2(wx, wz) / 100.0) * CHUNK.SIZE + CHUNK.SIZE)
                local_height = min(world_height - cy, CHUNK.SIZE)
                for y in range(local_height):
                    _voxels[x + CHUNK.SIZE * z + CHUNK.AREA * y] = y + cy
        self._is_empty = not np.any(_voxels)
        return _voxels
