from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import pygame
import random

from . import settings


@dataclass
class Bird:
    x: int
    y: float
    vel_y: float = 0.0
    alive: bool = True
    invuln_timer: float = 0.0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - 22, int(self.y) - 18, 44, 36)

    def jump(self) -> None:
        self.vel_y = settings.JUMP_VELOCITY

    def update(self, dt: float) -> None:
        self.vel_y += settings.GRAVITY * dt
        self.y += self.vel_y * dt

        if self.invuln_timer > 0:
            self.invuln_timer = max(0.0, self.invuln_timer - dt)


@dataclass
class PipePair:
    x: float
    gap_y: int
    passed: bool = False

    def top_rect(self) -> pygame.Rect:
        top_height = self.gap_y - settings.PIPE_GAP // 2
        return pygame.Rect(int(self.x), 0, settings.PIPE_WIDTH, top_height)

    def bottom_rect(self) -> pygame.Rect:
        bottom_y = self.gap_y + settings.PIPE_GAP // 2
        return pygame.Rect(int(self.x), bottom_y, settings.PIPE_WIDTH, settings.HEIGHT - settings.GROUND_HEIGHT - bottom_y)

    def update(self, dt: float, speed: float) -> None:
        self.x -= speed * dt

    def offscreen(self) -> bool:
        return self.x + settings.PIPE_WIDTH < -20


@dataclass
class Coin:
    x: float
    y: float
    taken: bool = False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x) - settings.COIN_SIZE // 2, int(self.y) - settings.COIN_SIZE // 2, settings.COIN_SIZE, settings.COIN_SIZE)

    def update(self, dt: float, speed: float) -> None:
        self.x -= speed * dt

    def offscreen(self) -> bool:
        return self.x < -40


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: Tuple[int, int, int]
    r: int

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 500 * dt
        self.life -= dt

    def draw(self, screen: pygame.Surface) -> None:
        if self.life <= 0:
            return
        alpha = max(0, min(255, int(255 * (self.life / 0.6))))
        s = pygame.Surface((self.r * 2 + 2, self.r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.r + 1, self.r + 1), self.r)
        screen.blit(s, (int(self.x) - self.r, int(self.y) - self.r))


class GameSession:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.bird = Bird(x=220, y=settings.HEIGHT // 2)
        self.pipes: List[PipePair] = []
        self.coins: List[Coin] = []
        self.particles: List[Particle] = []
        self.score = 0
        self.coins_run = 0
        self.spawn_timer = 0.0
        self.cloud_x = 0.0

    def add_sparkle(self, x: float, y: float, color=(255, 215, 90)) -> None:
        rng = random.Random(int(x * 10 + y * 3) % 9999)
        for _ in range(10):
            vx = rng.uniform(-160, 160)
            vy = rng.uniform(-240, -80)
            r = int(rng.randint(2, 4))
            self.particles.append(Particle(x=x, y=y, vx=vx, vy=vy, life=0.6, color=color, r=r))

    def update_particles(self, dt: float) -> None:
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

