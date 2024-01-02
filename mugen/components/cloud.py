import typing as t

from ..renderer.meshes import CloudMesh

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("Clouds",)


class Clouds:
    def __init__(self, app: "Mugen") -> None:
        self.app = app
        self.cloud_mesh = CloudMesh(self.app)

    def render(self) -> None:
        self.cloud_mesh.render()

    def update(self) -> None:
        self.cloud_mesh.program["uTime"].value = self.app._time  # type: ignore
