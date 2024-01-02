import math
import random

import numba
from nptyping import NDArray, Shape, UInt8
from opensimplex.internals import _init, _noise2, _noise3

from .constants import CHUNK, WORLD

__all__: tuple[str, ...] = (
    "noise2",
    "noise3",
    "height_map",
    "set_voxel_id",
)


perm, perm_grad_index3 = _init(seed=WORLD.SEED)


CENTER_XZ = numba.int32(WORLD.CENTER_XZ)
CENTER_Y = numba.int32(WORLD.CENTER_Y)
HEIGHT_FREQ = numba.float32(0.005)
CHUNK_SIZE = numba.int32(CHUNK.SIZE)
CHUNK_AREA = numba.int32(CHUNK.AREA)

SAND = 1
GRASS = 2
DIRT = 3
STONE = 4
SNOW = 5
LEAVES = 6
WOOD = 7

SNOW_LVL = 50
STONE_LVL = 40
DIRT_LVL = 35
GRASS_LVL = 8
SAND_LVL = 6

TREE_PROBABILITY = 0.004
TREE_WIDTH, TREE_HEIGHT = 4, 8
TREE_H_WIDTH, TREE_H_HEIGHT = TREE_WIDTH // 2, TREE_HEIGHT // 2


@numba.njit(cache=True)  # type: ignore
def noise2(x: float, y: float) -> float:
    return float(_noise2(x, y, perm))


@numba.njit(cache=True)  # type: ignore
def noise3(x: float, y: float, z: float) -> float:
    return float(_noise3(x, y, z, perm, perm_grad_index3))


@numba.njit  # type: ignore
def height_map(x: float, z: float) -> int:
    # island mask
    island = 1 / (pow(0.0025 * math.hypot(x - CENTER_XZ, z - CENTER_XZ), 20) + 0.0001)
    island = min(island, 1)

    # amplitude
    a1 = CENTER_Y
    a2, a4, a8 = a1 * 0.5, a1 * 0.25, a1 * 0.125

    # frequency
    f1 = HEIGHT_FREQ * 1.5
    f2, f4, f8 = f1 * 2, f1 * 4, f1 * 8

    if noise2(0.1 * x, 0.1 * z) < 0:
        a1 /= 1.03

    height = noise2(x * f1, z * f1) * a1 + a1
    height += noise2(x * f2, z * f2) * a2 - a2
    height += noise2(x * f4, z * f4) * a4 + a4
    height += noise2(x * f8, z * f8) * a8 - a8
    height = max(height, noise2(x * f8, z * f8) + 2)
    return int(height * island)


@numba.njit  # type: ignore
def get_index(x: int, y: int, z: int) -> int:
    return int(x + CHUNK_SIZE * z + CHUNK_AREA * y)


@numba.njit  # type: ignore
def set_voxel_id(
    voxels: NDArray[Shape["*, *"], UInt8],
    local_pos: tuple[int, int, int],
    world_pos: tuple[int, int, int],
    world_height: int,
) -> None:
    x, y, z = local_pos
    wx, wy, wz = world_pos
    if wy < world_height - random.randint(3, 6):
        # create caves
        is_cave = noise3(wx * 0.09, wy * 0.09, wz * 0.09) > 0
        voxel_id = 0 if is_cave and noise2(wx * 0.1, wz * 0.1) * 3 + 3 < wy < world_height - 10 else STONE
    else:
        # block level rng
        rng = int(random.random() * 7)
        ry = wy - rng
        if SNOW_LVL <= ry < world_height:
            voxel_id = SNOW
        elif STONE_LVL <= ry < SNOW_LVL:
            voxel_id = STONE
        elif DIRT_LVL <= ry < STONE_LVL:
            voxel_id = DIRT
        elif GRASS_LVL <= ry < DIRT_LVL:
            voxel_id = GRASS
        else:
            voxel_id = SAND
    voxels[get_index(x, y, z)] = voxel_id
    # place tree
    if wy < DIRT_LVL:
        place_tree(voxels, x, y, z, voxel_id)


@numba.njit  # type: ignore
def place_tree(voxels: NDArray[Shape["*, *"], UInt8], x: int, y: int, z: int, voxel_id: int) -> None:
    rnd = random.random()
    if voxel_id != GRASS or rnd > TREE_PROBABILITY:
        return None
    if y + TREE_HEIGHT >= CHUNK_SIZE:
        return None
    if x - TREE_H_WIDTH < 0 or x + TREE_H_WIDTH >= CHUNK_SIZE:
        return None
    if z - TREE_H_WIDTH < 0 or z + TREE_H_WIDTH >= CHUNK_SIZE:
        return None

    voxels[get_index(x, y, z)] = DIRT

    # leaves
    m = 0
    for n, iy in enumerate(range(TREE_H_HEIGHT, TREE_HEIGHT - 1)):
        k = iy % 2
        rng = int(random.random() * 2)
        for ix in range(-TREE_H_WIDTH + m, TREE_H_WIDTH - m * rng):
            for iz in range(-TREE_H_WIDTH + m * rng, TREE_H_WIDTH - m):
                if (ix + iz) % 4:
                    voxels[get_index(x + ix + k, y + iy, z + iz + k)] = LEAVES
        m += 1 if n > 0 else 3 if n > 1 else 0

    # tree trunk
    for iy in range(1, TREE_HEIGHT - 2):
        voxels[get_index(x, y + iy, z)] = WOOD

    # top
    voxels[get_index(x, y + TREE_HEIGHT - 2, z)] = LEAVES
