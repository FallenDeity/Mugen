import math
import typing as t

import glm

from ..utils import CAMERA, CHUNK

if t.TYPE_CHECKING:
    from ..components import Chunk
    from .camera import Camera


__all__: tuple[str, ...] = ("Frustum",)


class Frustum:
    def __init__(self, camera: "Camera") -> None:
        self.camera = camera
        self.factor_y = 1.0 / math.cos(CAMERA.V_FOV / 2)
        self.tan_y = math.tan(CAMERA.V_FOV / 2)
        self.factor_x = 1.0 / math.cos(CAMERA.H_FOV / 2)
        self.tan_x = math.tan(CAMERA.H_FOV / 2)

    def is_on_frustum(self, chunk: "Chunk") -> bool:
        sphere_vec = chunk.center - self.camera.position
        sz = glm.dot(sphere_vec, self.camera._front)
        if not (CAMERA.NEAR - CHUNK.CHUNK_SPHERE_RADIUS <= sz < CAMERA.FAR + CHUNK.CHUNK_SPHERE_RADIUS):
            return False
        sy = glm.dot(sphere_vec, self.camera._up)
        dist = self.factor_y * CHUNK.CHUNK_SPHERE_RADIUS + sz * self.tan_y
        if not (-dist <= sy < dist):
            return False
        sx = glm.dot(sphere_vec, self.camera._right)
        dist = self.factor_x * CHUNK.CHUNK_SPHERE_RADIUS + sz * self.tan_x
        if not (-dist <= sx < dist):
            return False
        return True
