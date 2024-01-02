import enum
import math
import pathlib
import random
import typing as t

import glm

__all__: tuple[str, ...] = (
    "WINDOW",
    "SHADERS",
    "CAMERA",
    "CHUNK",
    "PLAYER",
    "TEXTURES",
    "WORLD",
)


class WINDOW:
    RESOLUTION = (1280, 720)
    TITLE = "Mugen"
    FPS = 60
    ICON = "assets/icon.png"


class CHUNK:
    SIZE = 48
    H_SIZE = SIZE // 2
    AREA = SIZE * SIZE
    VOLUME = AREA * SIZE
    CHUNK_SPHERE_RADIUS = math.sqrt(3) * H_SIZE


class CAMERA:
    ASP_RATIO = WINDOW.RESOLUTION[0] / WINDOW.RESOLUTION[1]
    FOV = 50.0
    V_FOV = glm.radians(FOV)
    H_FOV = 2 * math.atan(math.tan(V_FOV / 2) * ASP_RATIO)
    NEAR = 0.1
    FAR = 1000.0
    PITCH_LIMIT = glm.radians(89.0)


class WORLD:
    BG_COLOR = glm.vec3(0.58, 0.83, 0.99)
    SEED = random.randint(-(2**63), 2**63 - 1)
    WIDTH = 30
    HEIGHT = 2
    DEPTH = WIDTH
    AREA = WIDTH * DEPTH
    VOLUME = AREA * HEIGHT
    CENTER_XZ = WIDTH * CHUNK.H_SIZE
    CENTER_Y = HEIGHT * CHUNK.H_SIZE
    WATER_LINE = 3.6
    WATER_AREA = 5 * CHUNK.SIZE * WIDTH
    CLOUD_SCALE = 25
    CLOUD_HEIGHT = HEIGHT * CHUNK.SIZE * 2


class PLAYER:
    SIZE = 3
    SPEED = 12.0
    ROTATION_SPEED = 3
    MOUSE_SENSITIVITY = 0.002
    POSITION = glm.vec3(WORLD.CENTER_XZ, WORLD.CENTER_Y * 1.5, WORLD.CENTER_XZ)


class SHADERS(enum.Enum):
    QUAD_VERT = pathlib.Path("assets/shaders/quad.vert")
    QUAD_FRAG = pathlib.Path("assets/shaders/quad.frag")
    CHUNK_VERT = pathlib.Path("assets/shaders/chunk.vert")
    CHUNK_FRAG = pathlib.Path("assets/shaders/chunk.frag")
    CUBE_VERT = pathlib.Path("assets/shaders/cube.vert")
    CUBE_FRAG = pathlib.Path("assets/shaders/cube.frag")
    CLOUD_VERT = pathlib.Path("assets/shaders/cloud.vert")
    CLOUD_FRAG = pathlib.Path("assets/shaders/cloud.frag")
    WATER_VERT = pathlib.Path("assets/shaders/water.vert")
    WATER_FRAG = pathlib.Path("assets/shaders/water.frag")

    def __get__(self, instance: t.Any, owner: t.Type[t.Any]) -> pathlib.Path:
        return self.value


class TEXTURES(enum.Enum):
    TEST = pathlib.Path("assets/textures/test.png")
    TEXTURE_ARRAY_0 = pathlib.Path("assets/textures/tex_array_0.png")
    WATER = pathlib.Path("assets/textures/water.png")

    def __get__(self, instance: t.Any, owner: t.Type[t.Any]) -> pathlib.Path:
        return self.value
