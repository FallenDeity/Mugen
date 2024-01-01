import typing as t

import glm

from .meshes import CubeMesh

if t.TYPE_CHECKING:
    from ..components.handler import ChunkManager


__all__: tuple[str, ...] = ("VoxelMarker",)


class VoxelMarker:
    def __init__(self, chunk_manager: "ChunkManager") -> None:
        self.chunk_manager = chunk_manager
        self.app = chunk_manager.app
        self.position = glm.ivec3(0, 0, 0)
        self.mesh = CubeMesh(self.app)

    def update(self) -> None:
        if self.chunk_manager.voxel_id:
            if self.chunk_manager.mode == "add":
                self.position = self.chunk_manager.voxel_world_pos + self.chunk_manager.voxel_normal
            else:
                self.position = self.chunk_manager.voxel_world_pos

    def set_uniform(self) -> None:
        self.mesh.program["uMode"].value = 1 if self.chunk_manager.mode == "add" else 0  # type: ignore
        self.mesh.program["uModel"].write(self.model_matrix)  # type: ignore

    def render(self) -> None:
        if self.chunk_manager.voxel_id:
            print(self.position)
            self.set_uniform()
            self.mesh.render()

    @property
    def model_matrix(self) -> glm.mat4:
        return glm.translate(glm.mat4(), glm.vec3(self.position))
