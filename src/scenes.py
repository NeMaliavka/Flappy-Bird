from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame
import random

from . import settings
from .assets import Assets
from .gameplay import Coin, GameSession, PipePair
from .save_data import SaveData
from .shop_data import SHOP_BGS, SHOP_BIRDS, SHOP_PIPES, UPGRADES
from .ui import Button, Card, draw_text

HEADER_H = 64
HEADER_GAP = 12
CARD_H = 84
CARD_GAP = 12
SECTION_GAP = 24


def _mouse_pos() -> Tuple[int, int]:
    return pygame.mouse.get_pos()


def _point_in_rect(p: Tuple[int, int], r: pygame.Rect) -> bool:
    return r.collidepoint(p[0], p[1])


def _format_price(price: int) -> str:
    return "FREE" if price <= 0 else f"{price}c"


def _upgrade_key(upgrade_id: str) -> str:
    return f"{upgrade_id}_level"


class Scene:
    def __init__(self, app: "App") -> None:
        self.app = app

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        pass


@dataclass
class Toast:
    text: str
    timer: float = 1.2


class MenuScene(Scene):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.panel_rect = self.app.assets.ui["panel"].get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 35))

        def go_play() -> None:
            self.app.start_new_run()
            self.app.set_scene("play")

        def go_continue() -> None:
            self.app.set_scene("play")

        def go_shop() -> None:
            self.app.set_scene("shop")

        def do_quit() -> None:
            self.app.running = False

        ui = self.app.assets.ui
        # Кнопки создаём без финальных координат — разложим их в _layout()
        self.btn_continue = Button(pygame.Rect(0, 0, 240, 72), ui["btn_continue"], go_continue, enabled=self.app.had_save_file)
        self.btn_play = Button(pygame.Rect(0, 0, 240, 72), ui["btn_play"], go_play)
        self.btn_shop = Button(pygame.Rect(0, 0, 240, 72), ui["btn_shop"], go_shop)
        self.btn_quit = Button(pygame.Rect(0, 0, 240, 72), ui["btn_quit"], do_quit)
        self.buttons = [self.btn_continue, self.btn_play, self.btn_shop, self.btn_quit]

        # Позиции текста внутри панели
        self.title_pos = (self.panel_rect.centerx, self.panel_rect.y + 54)
        self.hint_pos = (self.panel_rect.centerx, self.panel_rect.y + 98)

        self._layout()

    def _layout(self) -> None:
        """Раскладывает кнопки внутри панели без 'магических' X/Y."""
        rect = self.panel_rect
        cx = rect.centerx

        # зона под заголовок/подсказку
        top_padding = 22
        title_block_h = 112  # заголовок + подсказка + небольшой воздух

        # зона под кнопки
        area_top = rect.y + top_padding + title_block_h
        area_bottom = rect.bottom - 22
        area_h = max(0, area_bottom - area_top)

        # Хотим крупные кнопки, но если не помещается — автоматически ужимаем высоту и промежуток.
        n = len(self.buttons)
        btn_w = 250
        target_h = 68
        target_gap = 12

        if n <= 0:
            return

        # Подберём gap и высоту под доступную высоту area_h
        gap = min(target_gap, 14)
        max_btn_h = (area_h - (n - 1) * gap) // n if area_h > 0 else 0
        btn_h = max(54, min(target_h, int(max_btn_h)))

        # Если всё ещё не влезает — уменьшаем gap
        stack_h = n * btn_h + (n - 1) * gap
        if stack_h > area_h and n > 1:
            gap = max(6, int((area_h - n * btn_h) // (n - 1)))
            stack_h = n * btn_h + (n - 1) * gap

        # Немного поднимаем стек, чтобы нижняя кнопка не упиралась в край окна.
        start_y = area_top + max(0, (area_h - stack_h) // 2) - 8

        for i, b in enumerate(self.buttons):
            b.rect = pygame.Rect(cx - btn_w // 2, start_y + i * (btn_h + gap), btn_w, btn_h)

    def handle_event(self, event: pygame.event.Event) -> None:
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt: float) -> None:
        self.app.update_background(dt)

    def draw(self, screen: pygame.Surface) -> None:
        self.app.draw_background(screen)

        # декоративный верхний бар + монеты (контрастно читается на любом фоне)
        top_bar = pygame.Surface((settings.WIDTH, 86), pygame.SRCALPHA)
        top_bar.fill((0, 0, 0, 70))
        screen.blit(top_bar, (0, 0))

        coin_pill = pygame.Surface((260, 44), pygame.SRCALPHA)
        pygame.draw.rect(coin_pill, (18, 18, 26, 210), coin_pill.get_rect(), border_radius=16)
        pygame.draw.rect(coin_pill, (255, 235, 180, 60), coin_pill.get_rect(), width=2, border_radius=16)
        pill_rect = coin_pill.get_rect(topright=(settings.WIDTH - 18, 20))
        screen.blit(coin_pill, pill_rect)

        coin_text = f"Монеты: {self.app.save.coins_total}"
        draw_text(screen, coin_text, (pill_rect.x + 16, pill_rect.y + 10), size=30, color=(255, 235, 180), center=False, shadow=True)

        panel = self.app.assets.ui["panel"]
        rect = self.panel_rect
        screen.blit(panel, rect)

        # Заголовок/подсказка центрируем относительно панели (а не окна)
        draw_text(screen, settings.TITLE, self.title_pos, size=56, center=True)
        draw_text(
            screen,
            "Пробел — прыжок, Esc — пауза",
            self.hint_pos,
            size=28,
            center=True,
            color=(200, 200, 210),
        )

        for b in self.buttons:
            b.draw(screen)


class ShopScene(Scene):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.tab = "skins"  # skins / upgrades
        self.toast: Optional[Toast] = None
        self.scroll_y = 0
        self.scroll_max = 0
        self.viewport = pygame.Rect(0, 96, settings.WIDTH, settings.HEIGHT - 96)

        ui = self.app.assets.ui
        self.btn_back = Button(pygame.Rect(20, 18, 200, 64), ui["btn_back"], lambda: self.app.set_scene("menu"))
        self.btn_tab_skins = Button(pygame.Rect(settings.WIDTH // 2 - 230, 18, 220, 64), ui["tab_skins"], lambda: self._set_tab("skins"))
        self.btn_tab_upg = Button(pygame.Rect(settings.WIDTH // 2 + 10, 18, 220, 64), ui["tab_upgrades"], lambda: self._set_tab("upgrades"))
        self.buttons = [self.btn_back, self.btn_tab_skins, self.btn_tab_upg]
        self.cards: List[Card] = []
        self._rebuild_cards()

    def _clamp_scroll(self) -> None:
        if self.scroll_y < 0:
            self.scroll_y = 0
        if self.scroll_y > self.scroll_max:
            self.scroll_y = self.scroll_max

    def _set_tab(self, tab: str) -> None:
        self.tab = tab
        self.scroll_y = 0
        self._rebuild_cards()

    def _toast(self, text: str) -> None:
        self.toast = Toast(text=text)

    def _buy_skin(self, cat: str, item_id: str, price: int) -> None:
        owned = self.app.save.data["owned"][cat]
        if item_id in owned:
            return
        if self.app.save.coins_total < price:
            self._toast("Не хватает монет!")
            return
        self.app.save.coins_total -= price
        owned.append(item_id)
        self.app.save.save()
        self._toast("Куплено!")

    def _select_skin(self, cat: str, item_id: str) -> None:
        self.app.save.data["selected"][{"birds": "bird", "bgs": "bg", "pipes": "pipes"}[cat]] = item_id
        self.app.save.save()
        self._toast("Выбрано!")

    def _buy_or_select_skin(self, cat: str, item: dict) -> None:
        item_id = item["id"]
        price = int(item["price"])
        owned = item_id in self.app.save.data["owned"][cat]
        if not owned:
            self._buy_skin(cat, item_id, price)
        else:
            self._select_skin(cat, item_id)
        self._rebuild_cards()

    def _buy_upgrade(self, upg: dict) -> None:
        key = _upgrade_key(upg["id"])
        cur = int(self.app.save.data["upgrades"].get(key, 0))
        max_level = int(upg["max_level"])
        if cur >= max_level:
            self._toast("Макс. уровень!")
            return
        price = int(upg["prices"][cur])
        if self.app.save.coins_total < price:
            self._toast("Не хватает монет!")
            return
        self.app.save.coins_total -= price
        self.app.save.data["upgrades"][key] = cur + 1
        self.app.save.save()
        self._toast("Апгрейд куплен!")
        self._rebuild_cards()

    def _rebuild_cards(self) -> None:
        self.cards = []
        s = self.app.save.data

        if self.tab == "skins":
            groups = [
                ("birds", "Птички", SHOP_BIRDS),
                ("bgs", "Фоны", SHOP_BGS),
                ("pipes", "Трубы", SHOP_PIPES),
            ]
            y = 110
            for cat, title, items in groups:
                self.cards.append(
                    Card(
                        rect=pygame.Rect(40, y, settings.WIDTH - 80, HEADER_H),
                        title=title,
                        subtitle="Клик — купить / выбрать",
                        price_text="",
                        owned=True,
                        selected=False,
                        on_buy_or_select=lambda: None,
                        is_header=True
                    )
                )
                y += HEADER_H + HEADER_GAP

                for item in items:
                    item_id = item["id"]
                    owned = item_id in s["owned"][cat]
                    sel_key = {"birds": "bird", "bgs": "bg", "pipes": "pipes"}[cat]
                    selected = s["selected"][sel_key] == item_id
                    price = int(item["price"])
                    price_text = "SELECT" if owned else _format_price(price)
                    if selected:
                        price_text = "ON"
                    icon = None
                    if cat == "birds":
                        icon = self.app.assets.birds.get(item_id, self.app.assets.birds["bird_blue"])[0]
                    elif cat == "pipes":
                        icon = self.app.assets.pipes.get(item_id, self.app.assets.pipes["pipe_green"])["bottom"]
                        icon = pygame.transform.smoothscale(icon, (56, 56))
                    elif cat == "bgs":
                        icon = self.app.assets.bgs.get(item_id, self.app.assets.bgs["bg_sky_day"])
                        icon = pygame.transform.smoothscale(icon, (56, 56))

                    if icon is not None:
                        icon = pygame.transform.smoothscale(icon, (56, 56))

                    card_rect = pygame.Rect(40, y, settings.WIDTH - 80, CARD_H)
                    self.cards.append(
                        Card(
                            rect=card_rect,
                            title=item["title"],
                            subtitle=("Куплено" if owned else "Нажми, чтобы купить"),
                            price_text=price_text,
                            owned=owned,
                            selected=selected,
                            on_buy_or_select=lambda c=cat, it=item: self._buy_or_select_skin(c, it),
                            icon=icon,
                            locked_icon=self.app.assets.icons["lock"],
                        )
                    )
                    y +=  CARD_H + CARD_GAP

                y += SECTION_GAP
        else:
            y = 120
            for upg in UPGRADES:
                key = _upgrade_key(upg["id"])
                cur = int(s["upgrades"].get(key, 0))
                max_level = int(upg["max_level"])
                if cur >= max_level:
                    price_text = "MAX"
                else:
                    price_text = _format_price(int(upg["prices"][cur]))

                subtitle = f"Уровень: {cur}/{max_level}"
                icon_key = f"icon_{upg['id']}"
                icon = self.app.assets.icons.get(icon_key)
                if icon is not None:
                    icon = pygame.transform.smoothscale(icon, (56, 56))

                card_rect = pygame.Rect(40, y, settings.WIDTH - 80, 90)
                self.cards.append(
                    Card(
                        rect=card_rect,
                        title=upg["title"],
                        subtitle=subtitle,
                        price_text=price_text,
                        owned=cur > 0,
                        selected=False,
                        on_buy_or_select=lambda u=upg: self._buy_upgrade(u),
                        icon=icon,
                        locked_icon=None,
                    )
                )
                y += 102

        # посчитать максимальную прокрутку
        if self.cards:
            bottom = max(c.rect.bottom for c in self.cards)
        else:
            bottom = self.viewport.top
        content_h = bottom - self.viewport.top + 20
        self.scroll_max = max(0, content_h - self.viewport.h)
        self._clamp_scroll()

    def handle_event(self, event: pygame.event.Event) -> None:
        for b in self.buttons:
            b.handle_event(event)

        # прокрутка магазина колёсиком (только внутри области списка)
        if event.type == pygame.MOUSEWHEEL:
            mx, my = _mouse_pos()
            if self.viewport.collidepoint(mx, my):
                self.scroll_y -= int(event.y * 42)
                self._clamp_scroll()
            return

        # клики по карточкам: учитываем scroll_y
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.viewport.collidepoint(event.pos):
                return
            adj_pos = (event.pos[0], event.pos[1] + self.scroll_y)
            adj_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": adj_pos, "button": 1})
            for c in self.cards:
                c.handle_event(adj_event)

    def update(self, dt: float) -> None:
        self.app.update_background(dt)
        if self.toast is not None:
            self.toast.timer -= dt
            if self.toast.timer <= 0:
                self.toast = None

    def draw(self, screen: pygame.Surface) -> None:
        self.app.draw_background(screen)

        #draw_text(screen, "МАГАЗИН", (settings.WIDTH // 2, 70), size=52, center=True)
        draw_text(screen, 
            f"Монеты: {self.app.save.coins_total}", 
            (settings.WIDTH - 120, 26), 
            size=32, 
            color=(255, 235, 180), 
            center=True,
            shadow=True)

        for b in self.buttons:
            b.draw(screen)

        old_clip = screen.get_clip()
        screen.set_clip(self.viewport)
        for c in self.cards:
            c.draw(screen, y_offset=-self.scroll_y)
        screen.set_clip(old_clip)

        if self.toast is not None:
            draw_text(screen, self.toast.text, (settings.WIDTH // 2, settings.HEIGHT - 34), size=32, center=True, color=(255, 235, 180))


class GameOverScene(Scene):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        cx = settings.WIDTH // 2
        cy = settings.HEIGHT // 2 - 10
        ui = self.app.assets.ui
        self.btn_retry = Button(pygame.Rect(cx - 120, cy + 40, 240, 72), ui["btn_retry"], self._retry)
        self.btn_menu = Button(pygame.Rect(cx - 120, cy + 120, 240, 72), ui["btn_menu"], lambda: self.app.set_scene("menu"))
        self.buttons = [self.btn_retry, self.btn_menu]

    def _retry(self) -> None:
        self.app.start_new_run()
        self.app.set_scene("play")

    def handle_event(self, event: pygame.event.Event) -> None:
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt: float) -> None:
        self.app.update_background(dt)

    def draw(self, screen: pygame.Surface) -> None:
        self.app.draw_background(screen)
        panel = self.app.assets.ui["panel"]
        rect = panel.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 20))
        screen.blit(panel, rect)

        draw_text(screen, "GAME OVER", (settings.WIDTH // 2, rect.y + 62), size=64, center=True)
        draw_text(screen, f"Счёт: {self.app.session.score}", (settings.WIDTH // 2, rect.y + 100), size=42, center=True)
        draw_text(screen, f"Монеты за забег: +{self.app.session.coins_run}", (settings.WIDTH // 2, rect.y + 130), size=30, center=True, color=(255, 235, 180))
        draw_text(screen, f"Рекорд: {self.app.save.best_score}", (settings.WIDTH // 2, rect.y + 160), size=30, center=True, color=(200, 200, 210))

        for b in self.buttons:
            b.draw(screen)


class PlayScene(Scene):
    def __init__(self, app: "App") -> None:
        super().__init__(app)
        self.paused = False
        self.pause_panel = self.app.assets.ui["panel_pause"]

        ui = self.app.assets.ui
        self.btn_resume = Button(pygame.Rect(settings.WIDTH // 2 - 120, settings.HEIGHT // 2 - 30, 240, 72), ui["btn_resume"], self._resume)
        self.btn_save_exit = Button(pygame.Rect(settings.WIDTH // 2 - 120, settings.HEIGHT // 2 + 60, 240, 72), ui["btn_save_exit"], self._save_exit)
        self.btn_pause = Button(pygame.Rect(settings.WIDTH - 80, 16, 64, 64), self.app.assets.icons["pause"], self._pause)

        self.pause_buttons = [self.btn_resume, self.btn_save_exit]

        self._bird_anim = 0.0
        self._coin_anim = 0.0
        self._ground_x = 0.0

        self.start_hint = 1.4

    def _pause(self) -> None:
        self.paused = True

    def _resume(self) -> None:
        self.paused = False

    def _save_exit(self) -> None:
        self.app.save.save()
        self.app.set_scene("menu")

    def _die_or_lose_life(self) -> None:
        lives = self.app.lives
        if lives > 0:
            self.app.lives -= 1
            self.app.session.bird.invuln_timer = 1.0
            self.app.session.add_sparkle(self.app.session.bird.x, self.app.session.bird.y, color=(255, 120, 160))
        else:
            self.app.finish_run()
            self.app.set_scene("game_over")

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
            return

        if self.paused:
            for b in self.pause_buttons:
                b.handle_event(event)
            return

        self.btn_pause.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.app.session.bird.jump()
            self.start_hint = 0.0

    def update(self, dt: float) -> None:
        self.app.update_background(dt)
        self._bird_anim += dt * 10.0
        self._coin_anim += dt * 10.0

        # ground scroll
        speed = self.app.pipe_speed()
        self._ground_x = (self._ground_x - speed * dt) % settings.WIDTH

        if self.paused:
            return

        self.app.session.update_particles(dt)

        bird = self.app.session.bird
        bird.update(dt)

        # floor/ceiling
        if bird.y > settings.HEIGHT - settings.GROUND_HEIGHT - 18:
            bird.y = settings.HEIGHT - settings.GROUND_HEIGHT - 18
            self._die_or_lose_life()
        if bird.y < 18:
            bird.y = 18
            bird.vel_y = 0

        # spawn pipes
        self.app.session.spawn_timer += dt
        if self.app.session.spawn_timer >= settings.PIPE_SPAWN_SEC:
            self.app.session.spawn_timer = 0.0
            gap_y = int(random.randint(140, settings.HEIGHT - settings.GROUND_HEIGHT - 140))
            x = settings.WIDTH + 40
            self.app.session.pipes.append(PipePair(x=x, gap_y=gap_y))

            # coins in gap (1-2)
            for _ in range(int(random.randint(1, 3))):
                cy = float(random.randint(gap_y - 50, gap_y + 50))
                cx = x + settings.PIPE_WIDTH // 2 + float(random.randint(-10, 50))
                self.app.session.coins.append(Coin(x=cx, y=cy))

        # update pipes + score
        for p in self.app.session.pipes:
            p.update(dt, speed)
            if not p.passed and p.x + settings.PIPE_WIDTH < bird.x:
                p.passed = True
                self.app.session.score += 1
                self.app.session.coins_run += 1
                self.app.session.add_sparkle(bird.x + 10, bird.y - 10)

        self.app.session.pipes = [p for p in self.app.session.pipes if not p.offscreen()]

        # update coins (magnet)
        magnet_r = self.app.magnet_radius()
        for c in self.app.session.coins:
            c.update(dt, speed)
            if c.taken:
                continue
            if magnet_r > 0:
                dx = bird.x - c.x
                dy = bird.y - c.y
                dist2 = dx * dx + dy * dy
                if dist2 < magnet_r * magnet_r:
                    c.x += dx * dt * 6.5
                    c.y += dy * dt * 6.5

            if c.rect().colliderect(bird.rect()):
                c.taken = True
                self.app.session.coins_run += 1
                self.app.session.add_sparkle(c.x, c.y)

        self.app.session.coins = [c for c in self.app.session.coins if not c.offscreen() and not c.taken]

        # collisions (ignore while invulnerable)
        if bird.invuln_timer <= 0:
            br = bird.rect()
            for p in self.app.session.pipes:
                if br.colliderect(p.top_rect()) or br.colliderect(p.bottom_rect()):
                    self._die_or_lose_life()
                    break

    def draw(self, screen: pygame.Surface) -> None:
        self.app.draw_background(screen)

        # clouds
        clouds = self.app.assets.clouds
        cx = int(self.app.session.cloud_x)
        screen.blit(clouds, (cx, 0))
        screen.blit(clouds, (cx - settings.WIDTH, 0))

        # pipes
        pipe_skin = self.app.save.data["selected"]["pipes"]
        pipe_assets = self.app.assets.pipes.get(pipe_skin, self.app.assets.pipes["pipe_green"])
        for p in self.app.session.pipes:
            top = pipe_assets["top"]
            bottom = pipe_assets["bottom"]
            top_y = p.top_rect().bottom - top.get_height()
            screen.blit(top, (int(p.x), top_y))
            screen.blit(bottom, (int(p.x), p.bottom_rect().y))

        # coins
        coin_frame = int(self._coin_anim) % 3
        coin_img = self.app.assets.coins[coin_frame]
        for c in self.app.session.coins:
            r = coin_img.get_rect(center=(int(c.x), int(c.y)))
            screen.blit(coin_img, r)

        # particles
        for p in self.app.session.particles:
            p.draw(screen)

        # ground
        ground = self.app.assets.ground
        y = settings.HEIGHT - settings.GROUND_HEIGHT
        x1 = int(-self._ground_x)
        screen.blit(ground, (x1, y))
        screen.blit(ground, (x1 + settings.WIDTH, y))

        # bird
        bird_skin = self.app.save.data["selected"]["bird"]
        frames = self.app.assets.birds.get(bird_skin, self.app.assets.birds["bird_blue"])
        frame = frames[int(self._bird_anim) % 3]
        angle = max(-25, min(35, -self.app.session.bird.vel_y * 0.08))
        rotated = pygame.transform.rotozoom(frame, angle, 1.0)
        br = rotated.get_rect(center=(self.app.session.bird.x, int(self.app.session.bird.y)))
        if self.app.session.bird.invuln_timer > 0:
            if int(self.app.session.bird.invuln_timer * 12) % 2 == 0:
                screen.blit(rotated, br)
        else:
            screen.blit(rotated, br)

        # hud
        draw_text(screen, f"Score: {self.app.session.score}", (settings.HUD_MARGIN, settings.HUD_MARGIN), size=34)
        draw_text(screen, f"+{self.app.session.coins_run}", (settings.HUD_MARGIN, settings.HUD_MARGIN + 32), size=28, color=(255, 235, 180))

        # lives
        lx = settings.WIDTH - 160
        for i in range(self.app.lives + 1):
            screen.blit(self.app.assets.icons["heart"], (lx + i * 36, settings.HUD_MARGIN + 2))

        # pause icon
        screen.blit(self.app.assets.icons["pause"], self.btn_pause.rect)

        if self.start_hint > 0:
            draw_text(screen, "Нажми ПРОБЕЛ!", (settings.WIDTH // 2, 120), size=48, center=True, color=(255, 235, 180))
            self.start_hint -= 1 / settings.FPS

        if self.paused:
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 40))
            screen.blit(overlay, (0, 0))

            rect = self.pause_panel.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
            screen.blit(self.pause_panel, rect)

            draw_text(screen, "PAUSE", (settings.WIDTH // 2, rect.y + 60), size=64, center=True)
            for b in self.pause_buttons:
                b.draw(screen)


class App:
    def __init__(self, project_root: Path, screen: pygame.Surface) -> None:
        self.project_root = project_root
        self.screen = screen
        self.running = True

        self.had_save_file = (project_root / settings.SAVE_FILENAME).exists()
        self.save = SaveData.load_or_create(project_root / settings.SAVE_FILENAME)
        self.assets = Assets.load(project_root)

        self.session = GameSession()
        self.lives = 0
        self._scenes: Dict[str, Scene] = {}
        self._scene_name = "menu"

        self._cloud_speed = 25.0
        self.session.cloud_x = 0.0

        self.start_new_run()
        self._build_scenes()

    def _build_scenes(self) -> None:
        self._scenes = {
            "menu": MenuScene(self),
            "shop": ShopScene(self),
            "play": PlayScene(self),
            "game_over": GameOverScene(self),
        }

    def set_scene(self, name: str) -> None:
        self._scene_name = name

    @property
    def scene(self) -> Scene:
        return self._scenes[self._scene_name]

    def start_new_run(self) -> None:
        self.session.reset()
        self.lives = 1 if self.save.data["upgrades"].get("extra_life_level", 0) >= 1 else 0

    def finish_run(self) -> None:
        self.save.coins_total += int(self.session.coins_run)
        if self.session.score > self.save.best_score:
            self.save.best_score = int(self.session.score)
        self.save.save()

    def pipe_speed(self) -> float:
        base = 260.0
        slow_level = int(self.save.data["upgrades"].get("slow_level", 0))
        factor = [1.0, 0.95, 0.90, 0.85][max(0, min(3, slow_level))]
        return base * factor

    def magnet_radius(self) -> float:
        lvl = int(self.save.data["upgrades"].get("magnet_level", 0))
        return [0.0, 70.0, 100.0, 130.0][max(0, min(3, lvl))]

    def update_background(self, dt: float) -> None:
        self.session.cloud_x += self._cloud_speed * dt
        if self.session.cloud_x > settings.WIDTH:
            self.session.cloud_x -= settings.WIDTH

    def draw_background(self, screen: pygame.Surface) -> None:
        bg_id = self.save.data["selected"]["bg"]
        bg = self.assets.bgs.get(bg_id, self.assets.bgs["bg_sky_day"])
        screen.blit(bg, (0, 0))

