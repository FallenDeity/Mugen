import contextlib
import sys
import traceback

with contextlib.redirect_stdout(None):
    import pygame

import moderngl

from ..renderer import Scene, Shader, Textures
from ..utils import WINDOW, Logger
from .player import Player

__all__: tuple[str, ...] = ("Mugen",)


class Mugen:
    _logger: Logger = Logger(name="Mugen", file_logging=False)

    def __init__(self) -> None:
        self._logger.info("Initializing Mugen...")
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        self.window = pygame.display.set_mode(WINDOW.RESOLUTION, flags=pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption(WINDOW.TITLE)
        pygame.display.set_icon(pygame.image.load(WINDOW.ICON))
        self._logger.info("Initialized pygame window.")

        self.ctx = moderngl.create_context()
        self.ctx.gc_mode = "auto"
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
        self.ctx.enable(flags=moderngl.BLEND | moderngl.CULL_FACE | moderngl.DEPTH_TEST)
        self._logger.info("Initialized moderngl context.")

        self.clock = pygame.time.Clock()
        self._delta_time = 0.0
        self._time = 0.0
        self._is_running = True
        self._textures = Textures(app=self)
        self._player = Player(app=self)
        self._shader = Shader(app=self)
        self._scene = Scene(app=self)

        self._logger.info("Initialized Mugen...")

    def update(self) -> None:
        self._player.update()
        self._shader.update()
        self._scene.update()

        self._delta_time = self.clock.tick(WINDOW.FPS) / 1000.0
        self._time += self._delta_time
        pygame.display.set_caption(f"{WINDOW.TITLE} | FPS: {self.clock.get_fps():.2f}")
        self._logger.debug(f"FPS: {self.clock.get_fps():.2f}")

    def render(self) -> None:
        self.ctx.clear(14 / 255, 50 / 255, 95 / 255)
        self._scene.render()
        pygame.display.flip()

    def event_handler(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self._is_running = False

    def run(self) -> None:
        try:
            while self._is_running:
                for event in pygame.event.get():
                    self.event_handler(event)
                self.update()
                self.render()
        except Exception as e:
            tb_str = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self._logger.error(f"Exception occurred: {tb_str}")
        finally:
            pygame.quit()
            sys.exit()

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def shader(self) -> Shader:
        return self._shader
