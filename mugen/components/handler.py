import typing as t

import glm

from ..utils import CHUNK, WORLD, get_chunk_idx

if t.TYPE_CHECKING:
    from .chunk import Chunk
    from .world import World


class ChunkManager:
    MAX_RAYCAST_DISTANCE = 8.0  # distance in voxels

    def __init__(self, world: "World") -> None:
        self.world = world
        self.app = world.app
        self.chunks = world.chunks
        self.voxel_id = 0
        self.voxel_index = 0
        self.voxel_local_pos = glm.ivec3(0, 0, 0)
        self.voxel_world_pos = glm.ivec3(0, 0, 0)
        self.voxel_normal = glm.ivec3(0, 0, 0)
        self.chunk: t.Optional["Chunk"] = None
        self.mode: t.Literal["add", "remove"] = "add"

    def add_voxel(self) -> None:
        if self.voxel_id:
            voxel_id, voxel_index, _, chunk = self.get_voxel_id(self.voxel_world_pos + self.voxel_normal)
            if not voxel_id and chunk is not None:
                assert chunk.voxels is not None and chunk.mesh is not None, f"Chunk at {chunk.position} is None!"
                chunk.voxels[voxel_index] = 1
                chunk.mesh._rebuild()
                if chunk._is_empty:
                    chunk._is_empty = False
                self.app.logger.flair(f"Added voxel at {self.voxel_world_pos + self.voxel_normal}!")

    def remove_voxel(self) -> None:
        if self.voxel_id and self.chunk is not None:
            assert self.chunk.voxels is not None and self.chunk.mesh is not None
            self.chunk.voxels[self.voxel_index] = 0
            self.chunk.mesh._rebuild()
            self.rebuild_adjacent_chunks()
            self.app.logger.flair(f"Removed voxel at {self.voxel_world_pos}!")

    def set_voxel(self) -> None:
        self.app.logger.flair("Attempting to set voxel!" if self.mode == "add" else "Attempting to remove voxel!")
        if self.mode == "add":
            return self.add_voxel()
        return self.remove_voxel()

    def toggle_mode(self) -> None:
        self.mode = "remove" if self.mode == "add" else "add"
        self.app.logger.flair(f"Current mode: {self.mode} after toggle!")

    def update(self) -> None:
        self.ray_cast()

    def _rebuild_adjacent_chunks(self, adj_pos: tuple[int, int, int]) -> None:
        idx = get_chunk_idx(adj_pos)
        if idx != -1:
            self.chunks[idx].mesh._rebuild()

    def rebuild_adjacent_chunks(self) -> None:
        lx, ly, lz = self.voxel_local_pos
        wx, wy, wz = self.voxel_world_pos

        if lx == 0:
            self._rebuild_adjacent_chunks((wx - 1, wy, wz))
        elif lx == CHUNK.SIZE - 1:
            self._rebuild_adjacent_chunks((wx + 1, wy, wz))

        if ly == 0:
            self._rebuild_adjacent_chunks((wx, wy - 1, wz))
        elif ly == CHUNK.SIZE - 1:
            self._rebuild_adjacent_chunks((wx, wy + 1, wz))

        if lz == 0:
            self._rebuild_adjacent_chunks((wx, wy, wz - 1))
        elif lz == CHUNK.SIZE - 1:
            self._rebuild_adjacent_chunks((wx, wy, wz + 1))

    @staticmethod
    def _delta(x: float, y: float) -> tuple[float, float, float]:
        dx = glm.sign(y - x)
        delta_x = min(dx / (y - x), 10000000.0) if dx != 0 else 10000000.0
        max_x = delta_x * (1.0 - glm.fract(x)) if dx > 0 else delta_x * glm.fract(x)
        return dx, delta_x, max_x

    def ray_cast(self) -> bool:
        x1, y1, z1 = self.app._player.position
        x2, y2, z2 = self.app._player.position + self.app._player._front * self.MAX_RAYCAST_DISTANCE
        current_voxel_pos = glm.ivec3(x1, y1, z1)

        step_dir = -1
        self.voxel_id = 0
        self.voxel_normal = glm.ivec3(0, 0, 0)

        dx, delta_x, max_x = self._delta(x1, x2)
        dy, delta_y, max_y = self._delta(y1, y2)
        dz, delta_z, max_z = self._delta(z1, z2)

        while not (max_x > 1.0 and max_y > 1.0 and max_z > 1.0):
            self.voxel_id, index, pos, chunk = self.get_voxel_id(current_voxel_pos)
            if self.voxel_id:
                self.voxel_index, self.voxel_local_pos, self.chunk = index, pos, chunk
                self.voxel_world_pos = current_voxel_pos
                self.voxel_normal.x = int(-dx if step_dir == 0 else self.voxel_normal.x)
                self.voxel_normal.y = int(-dy if step_dir == 1 else self.voxel_normal.y)
                self.voxel_normal.z = int(-dz if step_dir == 2 else self.voxel_normal.z)
                return True

            if max_x < max_y:
                if max_x < max_z:
                    current_voxel_pos.x += int(dx)
                    max_x += delta_x
                    step_dir = 0
                else:
                    current_voxel_pos.z += int(dz)
                    max_z += delta_z
                    step_dir = 2
            else:
                if max_y < max_z:
                    current_voxel_pos.y += int(dy)
                    max_y += delta_y
                    step_dir = 1
                else:
                    current_voxel_pos.z += int(dz)
                    max_z += delta_z
                    step_dir = 2
        return False

    def get_voxel_id(self, voxel_world_pos: glm.ivec3) -> tuple[int, int, glm.ivec3, t.Optional["Chunk"]]:
        cx, cy, cz = chunk_pos = voxel_world_pos / CHUNK.SIZE
        if 0 <= cx < WORLD.WIDTH and 0 <= cy < WORLD.HEIGHT and 0 <= cz < WORLD.DEPTH:
            chunk_idx = cx + WORLD.WIDTH * cz + WORLD.AREA * cy
            chunk = self.chunks[chunk_idx]
            assert chunk is not None and chunk.voxels is not None, f"Chunk at {chunk_pos} is None!"
            lx, ly, lz = local_pos = voxel_world_pos - chunk_pos * CHUNK.SIZE
            voxel_idx = lx + lz * CHUNK.SIZE + ly * CHUNK.AREA
            voxel_id = chunk.voxels[voxel_idx]
            return voxel_id, voxel_idx, local_pos, chunk
        return 0, 0, glm.ivec3(0, 0, 0), None

    def check_collision(self, direction: t.Literal["forward", "backward", "left", "right", "up", "down"]) -> bool:
        x1, y1, z1 = self.app._player.position

        dir_map = {
            "forward": self.app._player._front,
            "backward": -self.app._player._front,
            "left": -self.app._player._right,
            "right": self.app._player._right,
            "up": self.app._player._up,
            "down": -self.app._player._up,
        }

        x2, y2, z2 = self.app._player.position + dir_map[direction] * 3.0

        current_voxel_pos = glm.ivec3(x1, y1, z1)

        dx, delta_x, max_x = self._delta(x1, x2)
        dy, delta_y, max_y = self._delta(y1, y2)
        dz, delta_z, max_z = self._delta(z1, z2)

        while not (max_x > 1.0 and max_y > 1.0 and max_z > 1.0):
            voxel_id, _, _, _ = self.get_voxel_id(current_voxel_pos)
            if voxel_id:
                return True

            if max_x < max_y:
                if max_x < max_z:
                    current_voxel_pos.x += int(dx)
                    max_x += delta_x
                else:
                    current_voxel_pos.z += int(dz)
                    max_z += delta_z
            else:
                if max_y < max_z:
                    current_voxel_pos.y += int(dy)
                    max_y += delta_y
                else:
                    current_voxel_pos.z += int(dz)
                    max_z += delta_z
        return False
