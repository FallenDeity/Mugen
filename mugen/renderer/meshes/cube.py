import dataclasses
import typing as t

import numpy as np
from nptyping import Float16, NDArray, Shape

from .base import BaseMesh

__all__: tuple[str, ...] = ("CubeMesh",)


@dataclasses.dataclass
class CubeMesh(BaseMesh):
    name: str = "CUBE"

    def __post_init__(self) -> None:
        self.vbo_format = "2f2 3f2"
        self.attrs = ("tex_coord", "in_position")
        self.vertices = self.get_vertex_data()
        self.program = self.app.shader.get_program(self.name)
        super().__post_init__()

    @staticmethod
    def get_data(
        vertices: list[t.Tuple[int, int, int]], indices: list[tuple[int, int, int]]
    ) -> NDArray[Shape["*, *"], Float16]:
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype=np.float16)

    def get_vertex_data(self) -> NDArray[Shape["*, *"], Float16]:
        vertices = [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1), (0, 1, 0), (0, 0, 0), (1, 0, 0), (1, 1, 0)]
        indices = [
            (0, 2, 3),
            (0, 1, 2),
            (1, 7, 2),
            (1, 6, 7),
            (6, 5, 4),
            (4, 7, 6),
            (3, 4, 5),
            (3, 5, 0),
            (3, 7, 4),
            (3, 2, 7),
            (0, 6, 1),
            (0, 5, 6),
        ]
        vertex_data = self.get_data(vertices, indices)
        tex_coord_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indices = [
            (0, 2, 3),
            (0, 1, 2),
            (0, 2, 3),
            (0, 1, 2),
            (0, 1, 2),
            (2, 3, 0),
            (2, 3, 0),
            (2, 0, 1),
            (0, 2, 3),
            (0, 1, 2),
            (3, 1, 2),
            (3, 0, 1),
        ]
        tex_coord_data = self.get_data(tex_coord_vertices, tex_coord_indices)  # type: ignore
        vertex_data = np.hstack([tex_coord_data, vertex_data])
        return vertex_data
