import dataclasses

import numpy as np

from .base import BaseMesh

__all__: tuple[str, ...] = ("QuadMesh",)


@dataclasses.dataclass
class QuadMesh(BaseMesh):
    name: str = "QUAD"

    def __post_init__(self) -> None:
        self.vbo_format = "3f 3f"
        self.attrs = ("in_position", "in_color")
        self.vertices = np.hstack(
            [
                (
                    (0.5, 0.5, 0.0),
                    (-0.5, 0.5, 0.0),
                    (-0.5, -0.5, 0.0),
                    (0.5, 0.5, 0.0),
                    (-0.5, -0.5, 0.0),
                    (0.5, -0.5, 0.0),
                ),
                (
                    (0, 1, 0),
                    (1, 0, 0),
                    (1, 1, 0),
                    (0, 1, 0),
                    (1, 1, 0),
                    (0, 0, 1),
                ),
            ],
            dtype=np.float32,
        )
        self.program = self.app.shader.get_program(self.name)
        super().__post_init__()
