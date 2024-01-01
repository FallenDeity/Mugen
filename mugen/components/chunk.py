import itertools
import typing as t

import glm
import numpy as np
from nptyping import NDArray, Shape, UInt8

from ..renderer.meshes import ChunkMesh
from ..utils import CHUNK

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("Chunk",)


class Chunk:
    def __init__(self, app: "Mugen") -> None:
        self.app = app
        self.voxels = self._build_voxels()
        self.mesh = ChunkMesh(chunk=self, app=self.app)

    def render(self) -> None:
        self.mesh.render()

    @staticmethod
    def _build_voxels() -> NDArray[Shape["*, *"], UInt8]:
        _voxels = np.zeros(CHUNK.VOLUME, dtype=np.uint8)
        for x, y, z in itertools.product(range(CHUNK.SIZE), repeat=3):
            _noise = glm.simplex(glm.vec3(x / 10, y / 10, z / 10))
            _voxels[x + CHUNK.SIZE * y + CHUNK.AREA * z] = glm.clamp(int(glm.mix(0, 255, _noise)), 0, 255)
        return _voxels
