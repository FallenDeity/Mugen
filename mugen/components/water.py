import typing as t

from ..renderer.meshes import WaterMesh

if t.TYPE_CHECKING:
    from mugen import Mugen


class Water:
    def __init__(self, app: "Mugen") -> None:
        self.app = app
        self.mesh = WaterMesh(self.app)

    def render(self) -> None:
        self.mesh.render()
