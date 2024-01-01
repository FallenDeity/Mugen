import typing as t

import pygame
from mugen.renderer import Camera
from mugen.utils import PLAYER

if t.TYPE_CHECKING:
    from mugen import Mugen


__all__: tuple[str, ...] = ("Player",)


class Player(Camera):
    def __init__(self, *, app: "Mugen") -> None:
        super().__init__(position=PLAYER.POSITION)
        self.app = app

    def update(self) -> None:
        self.mouse_listener()
        self.key_listener()
        super().update()

    def mouse_listener(self) -> None:
        dx, dy = pygame.mouse.get_rel()
        self.rotate_yaw(PLAYER.MOUSE_SENSITIVITY * dx if dx else 0)
        self.rotate_pitch(PLAYER.MOUSE_SENSITIVITY * dy if dy else 0)

    def key_listener(self) -> None:
        key = pygame.key.get_pressed()
        velocity = PLAYER.SPEED * self.app._delta_time
        _key_map: dict[tuple[int, ...], t.Callable[[float], None]] = {
            (pygame.K_w,): self.move_forward,
            (pygame.K_s,): self.move_backward,
            (pygame.K_a,): self.move_left,
            (pygame.K_d,): self.move_right,
            (pygame.K_q,): self.move_up,
            (pygame.K_e,): self.move_down,
        }
        for keys, func in _key_map.items():
            if any(key[k] for k in keys):
                func(velocity)
