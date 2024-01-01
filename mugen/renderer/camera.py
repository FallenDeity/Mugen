import glm

from ..utils import CAMERA

__all__: tuple[str, ...] = ("Camera",)


class Camera:
    _up = glm.vec3(0.0, 1.0, 0.0)
    _front = glm.vec3(0.0, 0.0, -1.0)
    _right = glm.vec3(1.0, 0.0, 0.0)

    def __init__(self, position: glm.vec3, yaw: float = -90.0, pitch: float = 0.0) -> None:
        self.position = glm.vec3(position)
        self.yaw = glm.radians(yaw)
        self.pitch = glm.radians(pitch)

        self._projection = glm.perspective(CAMERA.V_FOV, CAMERA.ASP_RATIO, CAMERA.NEAR, CAMERA.FAR)
        self._view = glm.mat4()

    def update(self) -> None:
        self._front.x = glm.cos(self.yaw) * glm.cos(self.pitch)
        self._front.y = glm.sin(self.pitch)
        self._front.z = glm.sin(self.yaw) * glm.cos(self.pitch)
        self._front = glm.normalize(self._front)

        self._right = glm.normalize(glm.cross(self._front, glm.vec3(0, 1, 0)))
        self._up = glm.normalize(glm.cross(self._right, self._front))

        self._view = glm.lookAt(self.position, self.position + self._front, self._up)

    def rotate_pitch(self, offset: float) -> None:
        self.pitch -= offset
        self.pitch = glm.clamp(self.pitch, -CAMERA.PITCH_LIMIT, CAMERA.PITCH_LIMIT)  # type: ignore

    def rotate_yaw(self, offset: float) -> None:
        self.yaw += offset

    def move_forward(self, offset: float) -> None:
        self.position += self._front * offset

    def move_right(self, offset: float) -> None:
        self.position += self._right * offset

    def move_up(self, offset: float) -> None:
        self.position += self._up * offset

    def move_backward(self, offset: float) -> None:
        self.position -= self._front * offset

    def move_left(self, offset: float) -> None:
        self.position -= self._right * offset

    def move_down(self, offset: float) -> None:
        self.position -= self._up * offset

    @property
    def projection(self) -> glm.mat4:
        return self._projection

    @property
    def view(self) -> glm.mat4:
        return self._view
