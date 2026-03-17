from __future__ import annotations

import os
import sys
from pathlib import Path

import pygame

from . import settings
from .scenes import App


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run(headless_test: bool = False) -> int:
    if headless_test:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()

    app = App(project_root(), screen)

    frames_left = 180 if headless_test else None

    while app.running:
        dt = clock.tick(settings.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.running = False
            else:
                app.scene.handle_event(event)

        app.scene.update(dt)
        app.scene.draw(screen)
        pygame.display.flip()

        if frames_left is not None:
            frames_left -= 1
            if frames_left <= 0:
                app.running = False

    pygame.quit()
    return 0


if __name__ == "__main__":
    headless = "--headless-test" in sys.argv
    raise SystemExit(run(headless_test=headless))

