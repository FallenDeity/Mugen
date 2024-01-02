import typing as t

import glm
import numba
import numpy as np
from nptyping import NDArray, Shape, UInt8

from ..renderer.meshes import ChunkMesh
from ..utils import CHUNK
from ..utils.noise_generator import height_map, set_voxel_id

if t.TYPE_CHECKING:
    from mugen import Mugen

    from .world import World


__all__: tuple[str, ...] = ("Chunk",)


CHUNK_SIZE = numba.int32(CHUNK.SIZE)
CHUNK_AREA = numba.int32(CHUNK.AREA)


class Chunk:
    mesh: ChunkMesh | None = None
    voxels: NDArray[Shape["*, *"], UInt8] | None = None

    def __init__(self, world: "World", app: "Mugen", position: tuple[int, int, int]) -> None:
        self.app = app
        self.world = world
        self.position = position
        self._is_empty = True
        self._model_matrix = glm.translate(glm.mat4(), glm.vec3(*self.position) * CHUNK.SIZE)
        self.center = (glm.vec3(*self.position) + 0.5) * CHUNK.SIZE
        self.is_on_frustum = self.app._player.frustum.is_on_frustum

    def _build_mesh(self) -> None:
        if self.mesh is None:
            self.mesh = ChunkMesh(self.app, self)

    def render(self) -> None:
        if not self._is_empty and self.is_on_frustum(self):
            if self.mesh is None:
                self._build_mesh()
            self.mesh.program["uModel"].write(self._model_matrix)  # type: ignore
            self.mesh.render()  # type: ignore

    def _build_voxels(self) -> NDArray[Shape["*, *"], UInt8]:
        if self.voxels is None:
            _voxels = np.zeros(CHUNK.VOLUME, dtype=np.uint8)
            cx, cy, cz = glm.ivec3(self.position) * CHUNK.SIZE
            self.generate_terrain(_voxels, cx, cy, cz)
            self._is_empty = not np.any(_voxels)
            return _voxels
        return self.voxels

    @staticmethod
    @numba.njit  # type: ignore
    def generate_terrain(voxels: NDArray[Shape["*, *"], UInt8], cx: int, cy: int, cz: int) -> None:
        for x in range(CHUNK_SIZE):
            wx = x + cx
            for z in range(CHUNK_SIZE):
                wz = z + cz
                world_height = height_map(wx, wz)
                local_height = min(world_height - cy, CHUNK_SIZE)
                for y in range(local_height):
                    wy = y + cy
                    set_voxel_id(voxels, (x, y, z), (wx, wy, wz), world_height)
