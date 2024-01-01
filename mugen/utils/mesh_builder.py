import typing as t

import numpy as np
from nptyping import NDArray, Shape, UInt8, UInt32
from numba import int64, njit

from . import CHUNK, WORLD

__all__: tuple[str, ...] = (
    "build_chunk_mesh",
    "get_chunk_idx",
)


CHUNK_VOLUME = int64(CHUNK.VOLUME)
CHUNK_AREA = int64(CHUNK.AREA)
CHUNK_SIZE = int64(CHUNK.SIZE)
WORLD_WIDTH = int64(WORLD.WIDTH)
WORLD_HEIGHT = int64(WORLD.HEIGHT)
WORLD_DEPTH = int64(WORLD.DEPTH)
WORLD_AREA = int64(WORLD.AREA)


@njit  # type: ignore
def pack(x: int, y: int, z: int, voxel_id: t.Any, face_id: int, ao: int, flip: int) -> int:
    # x: 6 bits, y: 6 bits, z: 6 bits, voxel_id: 8 bits, face_id: 3 bits, ao: 2 bits, flip: 1 bit
    a, b, c, d, e, f, g = x, y, z, voxel_id, face_id, ao, flip
    return int((a << 26) | (b << 20) | (c << 14) | (d << 6) | (e << 3) | (f << 1) | g)


@njit  # type: ignore
def ambient_occlusion(
    local_pos: tuple[int, int, int],
    world_pos: tuple[int, int, int],
    world_voxels: NDArray[Shape["*, *"], UInt8],
    plane: str,
) -> t.Tuple[int, ...]:
    x, y, z = local_pos
    wx, wy, wz = world_pos
    if plane == "Y":
        directions: list[t.Tuple[t.Tuple[int, int, int], t.Tuple[int, int, int]]] = [
            ((x, y, z - 1), (wx, wy, wz - 1)),
            ((x - 1, y, z - 1), (wx - 1, wy, wz - 1)),
            ((x - 1, y, z), (wx - 1, wy, wz)),
            ((x - 1, y, z + 1), (wx - 1, wy, wz + 1)),
            ((x, y, z + 1), (wx, wy, wz + 1)),
            ((x + 1, y, z + 1), (wx + 1, wy, wz + 1)),
            ((x + 1, y, z), (wx + 1, wy, wz)),
            ((x + 1, y, z - 1), (wx + 1, wy, wz - 1)),
        ]
        a, b, c, d, e, f, g, h = [is_voxel_visible(a, b, world_voxels) for a, b in directions]
    elif plane == "X":
        directions = [
            ((x, y, z - 1), (wx, wy, wz - 1)),
            ((x, y - 1, z - 1), (wx, wy - 1, wz - 1)),
            ((x, y - 1, z), (wx, wy - 1, wz)),
            ((x, y - 1, z + 1), (wx, wy - 1, wz + 1)),
            ((x, y, z + 1), (wx, wy, wz + 1)),
            ((x, y + 1, z + 1), (wx, wy + 1, wz + 1)),
            ((x, y + 1, z), (wx, wy + 1, wz)),
            ((x, y + 1, z - 1), (wx, wy + 1, wz - 1)),
        ]
        a, b, c, d, e, f, g, h = [is_voxel_visible(a, b, world_voxels) for a, b in directions]
    else:
        directions = [
            ((x - 1, y, z), (wx - 1, wy, wz)),
            ((x - 1, y - 1, z), (wx - 1, wy - 1, wz)),
            ((x, y - 1, z), (wx, wy - 1, wz)),
            ((x + 1, y - 1, z), (wx + 1, wy - 1, wz)),
            ((x + 1, y, z), (wx + 1, wy, wz)),
            ((x + 1, y + 1, z), (wx + 1, wy + 1, wz)),
            ((x, y + 1, z), (wx, wy + 1, wz)),
            ((x - 1, y + 1, z), (wx - 1, wy + 1, wz)),
        ]
        a, b, c, d, e, f, g, h = [is_voxel_visible(a, b, world_voxels) for a, b in directions]
    return a + b + c, g + h + a, e + f + g, c + d + e


@njit  # type: ignore
def get_chunk_idx(position: tuple[int, int, int]) -> int:
    wx, wy, wz = position
    x = wx // CHUNK_SIZE
    y = wy // CHUNK_SIZE
    z = wz // CHUNK_SIZE
    if not (0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT and 0 <= z < WORLD_DEPTH):
        return -1
    return int(x + WORLD_WIDTH * z + WORLD_AREA * y)


@njit  # type: ignore
def is_voxel_visible(
    local_pos: tuple[int, int, int],
    world_pos: tuple[int, int, int],
    world_voxels: NDArray[Shape["*, *"], UInt8],
) -> bool:
    idx = get_chunk_idx(world_pos)
    if idx == -1:
        return False
    chunk_voxels = world_voxels[idx]
    x, y, z = local_pos
    v_idx = x % CHUNK_SIZE + z % CHUNK_SIZE * CHUNK_SIZE + y % CHUNK_SIZE * CHUNK_AREA
    if chunk_voxels[v_idx]:
        return False
    return True


@njit  # type: ignore
def add_data(vertex: NDArray[Shape["*, *"], UInt8], idx: int, *vertices: t.Tuple[t.Any, ...]) -> int:
    for v in vertices:
        vertex[idx] = v
        idx += 1
    return idx


@njit  # type: ignore
def build_chunk_mesh(
    chunk_voxels: NDArray[Shape["*, *"], UInt8],
    format_size: int,
    position: tuple[int, int, int],
    world_voxels: NDArray[Shape["*, *"], UInt8],
) -> NDArray[Shape["*, *"], UInt32]:
    # front faces of the voxel
    # each face is made of 2 triangles and each triangle is made of 3 vertices so 2 * 3 * 3 = 18
    # 5 here is (x, y, z, voxel_id, face_id)
    vertex = np.empty(CHUNK_VOLUME * 18 * format_size, dtype=np.uint32)
    idx = 0
    for x in range(CHUNK_SIZE):
        for y in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                voxel_id = chunk_voxels[x + CHUNK_SIZE * z + CHUNK_AREA * y]
                if voxel_id:
                    cx, cy, cz = position
                    wx = cx * CHUNK_SIZE + x
                    wy = cy * CHUNK_SIZE + y
                    wz = cz * CHUNK_SIZE + z
                    # top face
                    if is_voxel_visible((x, y + 1, z), (wx, wy + 1, wz), world_voxels):
                        ao = ambient_occlusion((x, y + 1, z), (wx, wy + 1, wz), world_voxels, "Y")
                        flip = ao[0] + ao[2] < ao[1] + ao[3]
                        v0 = pack(x, y + 1, z, voxel_id, 0, ao[0], flip)
                        v1 = pack(x + 1, y + 1, z, voxel_id, 0, ao[1], flip)
                        v2 = pack(x + 1, y + 1, z + 1, voxel_id, 0, ao[2], flip)
                        v3 = pack(x, y + 1, z + 1, voxel_id, 0, ao[3], flip)
                        vs = (v1, v0, v3, v1, v3, v2) if flip else (v0, v3, v2, v0, v2, v1)
                        idx = add_data(vertex, idx, *vs)
                    # bottom face
                    if is_voxel_visible((x, y - 1, z), (wx, wy - 1, wz), world_voxels):
                        ao = ambient_occlusion((x, y - 1, z), (wx, wy - 1, wz), world_voxels, "Y")
                        flip = ao[0] + ao[2] < ao[1] + ao[3]
                        v0 = pack(x, y, z, voxel_id, 1, ao[0], flip)
                        v1 = pack(x + 1, y, z, voxel_id, 1, ao[1], flip)
                        v2 = pack(x + 1, y, z + 1, voxel_id, 1, ao[2], flip)
                        v3 = pack(x, y, z + 1, voxel_id, 1, ao[3], flip)
                        vs = (v1, v3, v0, v1, v2, v3) if flip else (v0, v2, v3, v0, v1, v2)
                        idx = add_data(vertex, idx, *vs)
                    # right face
                    if is_voxel_visible((x + 1, y, z), (wx + 1, wy, wz), world_voxels):
                        ao = ambient_occlusion((x + 1, y, z), (wx + 1, wy, wz), world_voxels, "X")
                        flip = ao[0] + ao[2] < ao[1] + ao[3]
                        v0 = pack(x + 1, y, z, voxel_id, 2, ao[0], flip)
                        v1 = pack(x + 1, y + 1, z, voxel_id, 2, ao[1], flip)
                        v2 = pack(x + 1, y + 1, z + 1, voxel_id, 2, ao[2], flip)
                        v3 = pack(x + 1, y, z + 1, voxel_id, 2, ao[3], flip)
                        vs = (v3, v0, v1, v3, v1, v2) if flip else (v0, v1, v2, v0, v2, v3)
                        idx = add_data(vertex, idx, *vs)
                    # left face
                    if is_voxel_visible((x - 1, y, z), (wx - 1, wy, wz), world_voxels):
                        ao = ambient_occlusion((x - 1, y, z), (wx - 1, wy, wz), world_voxels, "X")
                        flip = ao[0] + ao[2] < ao[1] + ao[3]
                        v0 = pack(x, y, z, voxel_id, 3, ao[0], flip)
                        v1 = pack(x, y + 1, z, voxel_id, 3, ao[1], flip)
                        v2 = pack(x, y + 1, z + 1, voxel_id, 3, ao[2], flip)
                        v3 = pack(x, y, z + 1, voxel_id, 3, ao[3], flip)
                        vs = (v3, v1, v0, v3, v2, v1) if flip else (v0, v2, v1, v0, v3, v2)
                        idx = add_data(vertex, idx, *vs)
                    # back face
                    if is_voxel_visible((x, y, z - 1), (wx, wy, wz - 1), world_voxels):
                        ao = ambient_occlusion((x, y, z - 1), (wx, wy, wz - 1), world_voxels, "Z")
                        flip = ao[0] + ao[2] < ao[1] + ao[3]
                        v0 = pack(x, y, z, voxel_id, 4, ao[0], flip)
                        v1 = pack(x, y + 1, z, voxel_id, 4, ao[1], flip)
                        v2 = pack(x + 1, y + 1, z, voxel_id, 4, ao[2], flip)
                        v3 = pack(x + 1, y, z, voxel_id, 4, ao[3], flip)
                        vs = (v3, v0, v1, v3, v1, v2) if flip else (v0, v1, v2, v0, v2, v3)
                        idx = add_data(vertex, idx, *vs)
                    # front face
                    if is_voxel_visible((x, y, z + 1), (wx, wy, wz + 1), world_voxels):
                        ao = ambient_occlusion((x, y, z + 1), (wx, wy, wz + 1), world_voxels, "Z")
                        flip = ao[0] + ao[2] < ao[1] + ao[3]
                        v0 = pack(x, y, z + 1, voxel_id, 5, ao[0], flip)
                        v1 = pack(x, y + 1, z + 1, voxel_id, 5, ao[1], flip)
                        v2 = pack(x + 1, y + 1, z + 1, voxel_id, 5, ao[2], flip)
                        v3 = pack(x + 1, y, z + 1, voxel_id, 5, ao[3], flip)
                        vs = (v3, v1, v0, v3, v2, v1) if flip else (v0, v2, v1, v0, v3, v2)
                        idx = add_data(vertex, idx, *vs)

    return vertex[: idx + 1]
