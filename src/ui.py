from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import pygame


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: Tuple[int, int],
    size: int = 36,
    color: Tuple[int, int, int] = (235, 235, 240),
    center: bool = False,
    shadow: bool = True,
) -> pygame.Rect:
    font = pygame.font.Font(None, size)
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos

    if shadow:
        sh = font.render(text, True, (10, 10, 14))
        sh_rect = rect.copy()
        sh_rect.x += 2
        sh_rect.y += 2
        surface.blit(sh, sh_rect)

    surface.blit(img, rect)
    return rect


def draw_text_right(
    surface: pygame.Surface,
    text: str,
    top_right: Tuple[int, int],
    size: int = 36,
    color: Tuple[int, int, int] = (235, 235, 240),
    shadow: bool = True,
) -> pygame.Rect:
    font = pygame.font.Font(None, size)
    img = font.render(text, True, color)
    rect = img.get_rect()
    rect.topright = top_right

    if shadow:
        sh = font.render(text, True, (10, 10, 14))
        sh_rect = rect.copy()
        sh_rect.x += 2
        sh_rect.y += 2
        surface.blit(sh, sh_rect)

    surface.blit(img, rect)
    return rect


@dataclass
class Button:
    rect: pygame.Rect
    image: pygame.Surface
    on_click: Callable[[], None]
    enabled: bool = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.enabled:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, screen: pygame.Surface) -> None:
        img = self.image
        if img.get_width() != self.rect.w or img.get_height() != self.rect.h:
            img = pygame.transform.smoothscale(img, (self.rect.w, self.rect.h))
        if self.enabled:
            screen.blit(img, self.rect)
        else:
            img = img.copy()
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            img.blit(overlay, (0, 0))
            screen.blit(img, self.rect)


@dataclass
class Card:
    rect: pygame.Rect
    title: str
    subtitle: str
    price_text: str
    owned: bool
    selected: bool
    on_buy_or_select: Callable[[], None]
    icon: Optional[pygame.Surface] = None
    locked_icon: Optional[pygame.Surface] = None
    is_header: bool = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_buy_or_select()

    def draw(self, screen: pygame.Surface, y_offset: int = 0) -> None:
        # y_offset нужен для аккуратной прокрутки магазина:
        # не трогаем self.rect (её используют для кликов), а только рисуем со сдвигом.
        r = self.rect.move(0, y_offset)
        bg = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        base = (28, 28, 40)
        pygame.draw.rect(bg, base, bg.get_rect(), border_radius=18)

        if self.is_header:
            pygame.draw.rect(bg, (120, 190, 255), bg.get_rect(), width=2, border_radius=18)
            screen.blit(bg, r)

            x = r.x + 16
            y = r.y + 8

            draw_text(screen, self.title, (x, y), size=30, shadow=True)

            draw_text(
                screen,
                self.subtitle,
                (x, y + 26),
                size=22,
                color=(180, 180, 190),
                shadow=False
            )

            return

        if self.selected:
            pygame.draw.rect(bg, (140, 220, 120), bg.get_rect(), width=3, border_radius=18)
        elif self.owned:
            pygame.draw.rect(bg, (120, 190, 255), bg.get_rect(), width=2, border_radius=18)
        else:
            pygame.draw.rect(bg, (255, 190, 70), bg.get_rect(), width=2, border_radius=18)

        screen.blit(bg, r)

        x, y = r.x + 16, r.y + 12
        if self.icon is not None:
            icon_rect = self.icon.get_rect(topleft=(x, y + 8))
            screen.blit(self.icon, icon_rect)
            x = icon_rect.right + 12

        # правая зона под цену/лейбл (чтобы текст никогда не уезжал за карточку)
        right_pad = 18
        right_zone_w = 160
        right_zone = pygame.Rect(r.right - right_zone_w - right_pad, r.y, right_zone_w, r.h)

        # текст слева не должен заходить в правую зону
        title_rect = draw_text(screen, self.title, (x, y), size=30, shadow=True)
        draw_text(screen, self.subtitle, (x, y + 28), size=24, color=(200, 200, 210), shadow=False)

        # цена/статус — выравниваем по правому краю внутри карточки
        if self.price_text:
            draw_text_right(
                screen,
                self.price_text,
                (r.right - right_pad, y + 18),
                size=28,
                color=(255, 235, 180),
                shadow=True,
            )

        if not self.owned and self.locked_icon is not None:
            lock_img = self.locked_icon
            # Если иконка пришла большего размера — уменьшаем (часто так бывает у пиксель-арта)
            if lock_img.get_width() > 64 or lock_img.get_height() > 64:
                lock_img = pygame.transform.smoothscale(lock_img, (48, 48))
            lock_rect = lock_img.get_rect()
            lock_rect.right = r.right - 70  # было -12, сдвигаем левее
            lock_rect.bottom = r.bottom - 12
            screen.blit(lock_img, lock_rect)

