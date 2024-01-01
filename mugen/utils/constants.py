import enum
import math
import pathlib
import typing as t

import glm

__all__: tuple[str, ...] = (
    "WINDOW",
    "SHADERS",
    "CAMERA",
    "CHUNK",
    "PLAYER",
    "TEXTURES",
)


class WINDOW:
    RESOLUTION = (1280, 720)
    TITLE = "Mugen"
    FPS = 60
    ICON = "assets/icon.png"


class CHUNK:
    SIZE = 32
    H_SIZE = SIZE // 2
    AREA = SIZE * SIZE
    VOLUME = AREA * SIZE


class CAMERA:
    ASP_RATIO = WINDOW.RESOLUTION[0] / WINDOW.RESOLUTION[1]
    FOV = 50.0
    V_FOV = glm.radians(FOV)
    H_FOV = 2 * math.atan(math.tan(V_FOV / 2) * ASP_RATIO)
    NEAR = 0.1
    FAR = 2000.0
    PITCH_LIMIT = glm.radians(89.0)


class PLAYER:
    SPEED = 5.0
    ROTATION_SPEED = 0.03
    POSITION = glm.vec3(CHUNK.H_SIZE, CHUNK.SIZE, 1.5 * CHUNK.SIZE)
    MOUSE_SENSITIVITY = 0.003


class SHADERS(enum.Enum):
    QUAD_VERT = pathlib.Path("assets/shaders/quad.vert")
    QUAD_FRAG = pathlib.Path("assets/shaders/quad.frag")
    CHUNK_VERT = pathlib.Path("assets/shaders/chunk.vert")
    CHUNK_FRAG = pathlib.Path("assets/shaders/chunk.frag")

    def __get__(self, instance: t.Any, owner: t.Type[t.Any]) -> pathlib.Path:
        return self.value


class TEXTURES(enum.Enum):
    TEST = pathlib.Path("assets/textures/test.png")

    def __get__(self, instance: t.Any, owner: t.Type[t.Any]) -> pathlib.Path:
        return self.value
