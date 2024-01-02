import dataclasses

import numpy as np
from nptyping import NDArray, Shape, UInt8

from .base import BaseMesh

__all__: tuple[str, ...] = ("WaterMesh",)


@dataclasses.dataclass
class WaterMesh(BaseMesh):
    name: str = "WATER"

    def __post_init__(self) -> None:
        self.vbo_format = "2u1 3u1"
        self.attrs = ("tex_coord", "in_position")
        self.vertices = self.get_vertex_data()
        self.program = self.app.shader.get_program(self.name)
        super().__post_init__()

    def get_vertex_data(self) -> NDArray[Shape["6, 5"], UInt8]:
        vertices = np.array([(0, 0, 0), (1, 0, 1), (1, 0, 0), (0, 0, 0), (0, 0, 1), (1, 0, 1)], dtype=np.uint8)
        tex_coords = np.array([(0, 0), (1, 1), (1, 0), (0, 0), (0, 1), (1, 1)], dtype=np.uint8)
        vertex_data = np.hstack([tex_coords, vertices])
        return vertex_data
