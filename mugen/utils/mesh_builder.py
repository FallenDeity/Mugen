import itertools
import typing as t

import numpy as np
from nptyping import NDArray, Shape, UInt8

from . import CHUNK

__all__: tuple[str, ...] = ("build_chunk_mesh",)


def is_voxel_visible(chunk_voxels: NDArray[Shape["*, *"], UInt8], x: int, y: int, z: int) -> bool:
    if 0 <= x < CHUNK.SIZE and 0 <= y < CHUNK.SIZE and 0 <= z < CHUNK.SIZE:
        return not chunk_voxels[x + CHUNK.SIZE * z + CHUNK.AREA * y]
    return True


def add_data(vertex: NDArray[Shape["*, *"], UInt8], idx: int, *vertices: t.Tuple[t.Any, ...]) -> int:
    for v in vertices:
        for i in v:
            vertex[idx] = i
            idx += 1
    return idx


def build_chunk_mesh(chunk_voxels: NDArray[Shape["*, *"], UInt8], format_size: int) -> NDArray[Shape["*, *"], UInt8]:
    # front faces of the voxel
    # each face is made of 2 triangles and each triangle is made of 3 vertices so 2 * 3 * 3 = 18
    # 5 here is (x, y, z, voxel_id, face_id)
    vertex = np.empty(CHUNK.VOLUME * 18 * format_size, dtype=np.uint8)
    idx = 0
    for x, z, y in itertools.product(range(CHUNK.SIZE), repeat=3):
        if voxel_id := chunk_voxels[x + CHUNK.SIZE * z + CHUNK.AREA * y]:
            if is_voxel_visible(chunk_voxels, x, y + 1, z):
                v0 = (x, y + 1, z, voxel_id, 0)
                v1 = (x + 1, y + 1, z, voxel_id, 0)
                v2 = (x + 1, y + 1, z + 1, voxel_id, 0)
                v3 = (x, y + 1, z + 1, voxel_id, 0)
                idx = add_data(vertex, idx, v0, v3, v2, v0, v2, v1)
            # bottom face
            if is_voxel_visible(chunk_voxels, x, y - 1, z):
                v0 = (x, y, z, voxel_id, 1)
                v1 = (x + 1, y, z, voxel_id, 1)
                v2 = (x + 1, y, z + 1, voxel_id, 1)
                v3 = (x, y, z + 1, voxel_id, 1)
                idx = add_data(vertex, idx, v0, v2, v3, v0, v1, v2)
            # right face
            if is_voxel_visible(chunk_voxels, x + 1, y, z):
                v0 = (x + 1, y, z, voxel_id, 2)
                v1 = (x + 1, y + 1, z, voxel_id, 2)
                v2 = (x + 1, y + 1, z + 1, voxel_id, 2)
                v3 = (x + 1, y, z + 1, voxel_id, 2)
                idx = add_data(vertex, idx, v0, v1, v2, v0, v2, v3)
            # left face
            if is_voxel_visible(chunk_voxels, x - 1, y, z):
                v0 = (x, y, z, voxel_id, 3)
                v1 = (x, y + 1, z, voxel_id, 3)
                v2 = (x, y + 1, z + 1, voxel_id, 3)
                v3 = (x, y, z + 1, voxel_id, 3)
                idx = add_data(vertex, idx, v0, v2, v1, v0, v3, v2)
            # back face
            if is_voxel_visible(chunk_voxels, x, y, z - 1):
                v0 = (x, y, z, voxel_id, 4)
                v1 = (x, y + 1, z, voxel_id, 4)
                v2 = (x + 1, y + 1, z, voxel_id, 4)
                v3 = (x + 1, y, z, voxel_id, 4)
                idx = add_data(vertex, idx, v0, v1, v2, v0, v2, v3)
            # front face
            if is_voxel_visible(chunk_voxels, x, y, z + 1):
                v0 = (x, y, z + 1, voxel_id, 5)
                v1 = (x, y + 1, z + 1, voxel_id, 5)
                v2 = (x + 1, y + 1, z + 1, voxel_id, 5)
                v3 = (x + 1, y, z + 1, voxel_id, 5)
                idx = add_data(vertex, idx, v0, v2, v1, v0, v3, v2)

    return vertex[: idx + 1]
