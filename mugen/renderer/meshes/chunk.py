import dataclasses
import typing as t

from ...utils import build_chunk_mesh
from .base import BaseMesh

if t.TYPE_CHECKING:
    from mugen.components import Chunk


__all__: tuple[str, ...] = ("ChunkMesh",)


@dataclasses.dataclass
class ChunkMesh(BaseMesh):
    chunk: "Chunk"
    name: str = "CHUNK"

    def __post_init__(self) -> None:
        self.vbo_format = "1u4"
        self.attrs = ("packed_data",)
        _format_size = sum(int(i[:1]) for i in self.vbo_format.split())
        self.vertices = build_chunk_mesh(self.chunk.voxels, _format_size, self.chunk.position, self.chunk.world.voxels)
        self.program = self.app.shader.get_program(self.name)
        super().__post_init__()

    def _rebuild(self) -> None:
        _format_size = sum(int(i[:1]) for i in self.vbo_format.split())
        self.vertices = build_chunk_mesh(self.chunk.voxels, _format_size, self.chunk.position, self.chunk.world.voxels)
        self.vao = self.get_vao(self.vertices)
