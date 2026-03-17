from __future__ import annotations

from dataclasses import dataclass
import random
from pathlib import Path
from typing import Dict, List, Tuple

import pygame

from . import settings


Color = Tuple[int, int, int]


def _safe_load_image(path: Path, *, use_colorkey: bool = False) -> pygame.Surface | None:
    #print("Loading:", path)
    if not path.exists():
        return None

    try:
        loaded = pygame.image.load(str(path))
        if use_colorkey:
            surf = loaded.convert()
            key = surf.get_at((0, 0))
            surf.set_colorkey(key)
        else:
            surf = loaded.convert_alpha()
        return surf
    except Exception:
        return None


def _scale(surf: pygame.Surface, size: Tuple[int, int]) -> pygame.Surface:
    if surf.get_width() == size[0] and surf.get_height() == size[1]:
        return surf
    return pygame.transform.smoothscale(surf, size)
    try:
        loaded = pygame.image.load(str(path))
        if use_colorkey:
            surf = loaded.convert()
            key = surf.get_at((0, 0))
            surf.set_colorkey(key)
        else:
            surf = loaded.convert_alpha()
        return surf
    except Exception:
        return None


def _rounded_rect(surface: pygame.Surface, rect: pygame.Rect, color: Color, radius: int = 14) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def _make_button_surface(size: Tuple[int, int], text: str, accent: Color) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    _rounded_rect(surf, pygame.Rect(0, 0, w, h), (20, 20, 28), radius=18)
    _rounded_rect(surf, pygame.Rect(3, 3, w - 6, h - 6), (34, 34, 48), radius=16)
    pygame.draw.rect(surf, accent, pygame.Rect(8, h - 10, w - 16, 4), border_radius=2)

    font = pygame.font.Font(None, 42)
    label = font.render(text, True, (235, 235, 240))
    surf.blit(label, label.get_rect(center=(w // 2, h // 2 - 2)))
    return surf


def _make_panel_surface(size: Tuple[int, int]) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    _rounded_rect(surf, pygame.Rect(0, 0, w, h), (18, 18, 26), radius=22)
    _rounded_rect(surf, pygame.Rect(6, 6, w - 12, h - 12), (30, 30, 44), radius=18)
    pygame.draw.rect(surf, (255, 255, 255, 20), pygame.Rect(10, 10, w - 20, 28), border_radius=14)
    return surf


def _make_bg(size: Tuple[int, int], top: Color, bottom: Color) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    return surf.convert()


def _make_cloud_layer(size: Tuple[int, int]) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    rng = random.Random(7)
    for _ in range(14):
        x = rng.randrange(0, w)
        y = rng.randrange(0, h // 2)
        r = rng.randrange(26, 54)
        color = (255, 255, 255, 35)
        pygame.draw.circle(surf, color, (x, y), r)
        pygame.draw.circle(surf, color, (x + r // 2, y + 6), int(r * 0.8))
        pygame.draw.circle(surf, color, (x - r // 2, y + 10), int(r * 0.7))
    return surf


def _make_ground(size: Tuple[int, int]) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (26, 22, 28), pygame.Rect(0, 0, w, h))
    pygame.draw.rect(surf, (56, 44, 36), pygame.Rect(0, 22, w, h - 22))
    for x in range(0, w, 40):
        pygame.draw.rect(surf, (75, 58, 46), pygame.Rect(x + 10, 38, 20, 10), border_radius=4)
    pygame.draw.rect(surf, (140, 220, 120), pygame.Rect(0, 0, w, 10))
    return surf


def _make_pipe(size: Tuple[int, int], theme: str, flipped: bool) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if theme == "green":
        base = (92, 210, 132)
        shade = (62, 160, 100)
        rim = (32, 90, 60)
    elif theme == "candy":
        base = (250, 160, 200)
        shade = (210, 120, 170)
        rim = (140, 70, 110)
    else:  # ice
        base = (160, 220, 250)
        shade = (120, 180, 220)
        rim = (70, 110, 150)

    pygame.draw.rect(surf, shade, pygame.Rect(0, 0, w, h), border_radius=18)
    pygame.draw.rect(surf, base, pygame.Rect(8, 6, w - 16, h - 12), border_radius=14)
    pygame.draw.rect(surf, rim, pygame.Rect(0, 0, w, 26), border_radius=12)
    pygame.draw.rect(surf, (255, 255, 255, 35), pygame.Rect(14, 40, 10, h - 80), border_radius=8)

    if flipped:
        surf = pygame.transform.flip(surf, False, True)
    return surf


def _make_bird_frame(size: Tuple[int, int], theme: str, frame_idx: int) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2

    if theme == "blue":
        body = (120, 190, 255)
        wing = (80, 150, 230)
        beak = (255, 190, 70)
    elif theme == "pink":
        body = (255, 150, 210)
        wing = (230, 110, 170)
        beak = (255, 205, 90)
    else:  # ninja
        body = (70, 70, 90)
        wing = (40, 40, 60)
        beak = (255, 205, 90)

    pygame.draw.circle(surf, body, (cx, cy), 22)
    pygame.draw.circle(surf, (255, 255, 255), (cx + 10, cy - 6), 7)
    pygame.draw.circle(surf, (10, 10, 14), (cx + 12, cy - 6), 3)
    pygame.draw.polygon(surf, beak, [(cx + 18, cy + 2), (cx + 34, cy + 7), (cx + 18, cy + 12)])

    wing_offset = [-4, 0, -2][frame_idx % 3]
    pygame.draw.ellipse(surf, wing, pygame.Rect(cx - 16, cy + 2 + wing_offset, 24, 14))

    if theme == "ninja":
        pygame.draw.rect(surf, (15, 15, 22), pygame.Rect(cx - 22, cy - 10, 44, 14), border_radius=7)
        pygame.draw.circle(surf, (255, 255, 255), (cx + 10, cy - 6), 7)
        pygame.draw.circle(surf, (10, 10, 14), (cx + 12, cy - 6), 3)

    return surf


def _make_coin_frame(size: Tuple[int, int], frame_idx: int) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    squash = [0, 2, 0][frame_idx % 3]
    r = 12
    pygame.draw.ellipse(surf, (255, 215, 90), pygame.Rect(cx - r, cy - r + squash, 2 * r, 2 * r - 2 * squash))
    pygame.draw.ellipse(surf, (255, 245, 160), pygame.Rect(cx - r + 4, cy - r + 4 + squash, 2 * r - 8, 2 * r - 8 - 2 * squash))
    pygame.draw.ellipse(surf, (255, 255, 255, 60), pygame.Rect(cx - 5, cy - 10 + squash, 6, 10))
    return surf


def _make_icon(size: Tuple[int, int], kind: str) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if kind == "pause":
        _rounded_rect(surf, pygame.Rect(0, 0, w, h), (20, 20, 28), radius=16)
        pygame.draw.rect(surf, (235, 235, 240), pygame.Rect(18, 16, 10, h - 32), border_radius=4)
        pygame.draw.rect(surf, (235, 235, 240), pygame.Rect(w - 28, 16, 10, h - 32), border_radius=4)
    elif kind == "lock":
        pygame.draw.rect(surf, (235, 235, 240), pygame.Rect(10, 24, w - 20, h - 18), border_radius=10)
        pygame.draw.arc(surf, (235, 235, 240), pygame.Rect(16, 6, w - 32, 30), 3.14, 0, 6)
        pygame.draw.circle(surf, (20, 20, 28), (w // 2, 40), 6)
    elif kind == "disk":
        _rounded_rect(surf, pygame.Rect(0, 0, w, h), (20, 20, 28), radius=16)
        pygame.draw.rect(surf, (235, 235, 240), pygame.Rect(12, 12, w - 24, h - 24), border_radius=10)
        pygame.draw.rect(surf, (20, 20, 28), pygame.Rect(18, 18, w - 36, 18), border_radius=6)
    elif kind == "heart":
        pygame.draw.circle(surf, (255, 120, 160), (w // 2 - 6, h // 2 - 2), 10)
        pygame.draw.circle(surf, (255, 120, 160), (w // 2 + 6, h // 2 - 2), 10)
        pygame.draw.polygon(surf, (255, 120, 160), [(w // 2 - 16, h // 2 + 2), (w // 2 + 16, h // 2 + 2), (w // 2, h // 2 + 20)])
    else:
        _rounded_rect(surf, pygame.Rect(0, 0, w, h), (34, 34, 48), radius=14)
    return surf


@dataclass
class Assets:
    root: Path

    bgs: Dict[str, pygame.Surface]
    clouds: pygame.Surface
    ground: pygame.Surface

    birds: Dict[str, List[pygame.Surface]]
    pipes: Dict[str, Dict[str, pygame.Surface]]  # skin -> {"top": surf, "bottom": surf}
    coins: List[pygame.Surface]

    ui: Dict[str, pygame.Surface]
    icons: Dict[str, pygame.Surface]

    @classmethod
    def load(cls, project_root: Path) -> "Assets":
        assets_root = project_root / settings.ASSETS_DIRNAME
        w, h = settings.WIDTH, settings.HEIGHT

        # backgrounds
        bg_day = _safe_load_image(assets_root / "bg_sky_day.png") or _make_bg((w, h), (40, 60, 100), (90, 140, 220))
        bg_night = _safe_load_image(assets_root / "bg_sky_night.png") or _make_bg((w, h), (10, 12, 30), (40, 60, 120))
        bg_forest_day = _safe_load_image(assets_root / "bg_forest_day.png") or _make_bg((w, h), (30, 70, 60), (70, 140, 110))
        bg_forest_night = _safe_load_image(assets_root / "bg_forest_night.png") or _make_bg((w, h), (8, 18, 20), (30, 70, 60))
        bg_day = _scale(bg_day, (w, h))
        bg_night = _scale(bg_night, (w, h))
        bg_forest_day = _scale(bg_forest_day, (w, h))
        bg_forest_night = _scale(bg_forest_night, (w, h))

        clouds = _safe_load_image(assets_root / "layer_clouds.png") or _make_cloud_layer((w, h))
        ground = _safe_load_image(assets_root / "ground.png") or _make_ground((w, settings.GROUND_HEIGHT))
        clouds = _scale(clouds, (w, h))
        ground = _scale(ground, (w, settings.GROUND_HEIGHT))

        birds: Dict[str, List[pygame.Surface]] = {}
        for skin_id, theme in (("bird_blue", "blue"), ("bird_pink", "pink"), ("bird_ninja", "ninja")):
            frames: List[pygame.Surface] = []
            for i in range(1, 4):
                img = _safe_load_image(assets_root / f"{skin_id}_{i}.png", use_colorkey=False)
                frame = img or _make_bird_frame((64, 64), theme=theme, frame_idx=i - 1)
                frames.append(_scale(frame, (64, 64)))
            birds[skin_id] = frames

        pipes: Dict[str, Dict[str, pygame.Surface]] = {}
        pipe_map = {"pipe_green": "green", "pipe_candy": "candy", "pipe_ice": "ice"}
        for skin_id, theme in pipe_map.items():
            top = _safe_load_image(assets_root / f"pipe_top_{theme}.png") or _make_pipe((settings.PIPE_WIDTH, settings.PIPE_HEIGHT), theme=theme, flipped=True)
            bottom = _safe_load_image(assets_root / f"pipe_bottom_{theme}.png") or _make_pipe((settings.PIPE_WIDTH, settings.PIPE_HEIGHT), theme=theme, flipped=False)
            top = _scale(top, (settings.PIPE_WIDTH, settings.PIPE_HEIGHT))
            bottom = _scale(bottom, (settings.PIPE_WIDTH, settings.PIPE_HEIGHT))
            pipes[skin_id] = {"top": top, "bottom": bottom}

        coins: List[pygame.Surface] = []
        for i in range(1, 4):
            img = _safe_load_image(assets_root / f"coin_{i}.png", use_colorkey=False)
            c = img or _make_coin_frame((settings.COIN_SIZE, settings.COIN_SIZE), frame_idx=i - 1)
            coins.append(_scale(c, (settings.COIN_SIZE, settings.COIN_SIZE)))

        panel = _make_panel_surface((720, 360))
        panel_pause = panel.copy()

        ui = {
            "panel": panel,
            "panel_pause": panel_pause,
            "btn_play": _safe_load_image(assets_root / "btn_play.png") or _make_button_surface((240, 72), "PLAY", (120, 190, 255)),
            "btn_continue": _safe_load_image(assets_root / "btn_continue.png") or _make_button_surface((240, 72), "CONTINUE", (140, 220, 120)),
            "btn_shop": _safe_load_image(assets_root / "btn_shop.png") or _make_button_surface((240, 72), "SHOP", (255, 190, 70)),
            "btn_quit": _safe_load_image(assets_root / "btn_quit.png") or _make_button_surface((240, 72), "QUIT", (255, 120, 160)),
            "btn_retry": _safe_load_image(assets_root / "btn_retry.png") or _make_button_surface((240, 72), "RETRY", (120, 190, 255)),
            "btn_menu": _safe_load_image(assets_root / "btn_menu.png") or _make_button_surface((240, 72), "MENU", (255, 190, 70)),
            "btn_back": _safe_load_image(assets_root / "btn_back.png") or _make_button_surface((200, 64), "BACK", (200, 200, 210)),
            "btn_save_exit": _safe_load_image(assets_root / "btn_save_exit.png") or _make_button_surface((240, 72), "SAVE & EXIT", (140, 220, 120)),
            "btn_resume": _safe_load_image(assets_root / "btn_resume.png") or _make_button_surface((240, 72), "RESUME", (120, 190, 255)),
            "tab_skins": _safe_load_image(assets_root / "tab_skins.png") or _make_button_surface((220, 64), "SKINS", (255, 190, 70)),
            "tab_upgrades": _safe_load_image(assets_root / "tab_upgrades.png") or _make_button_surface((220, 64), "UPGRADES", (140, 220, 120)),
        }

        icons = {
            "pause": _scale((_safe_load_image(assets_root / "btn_pause.png", use_colorkey=False) or _make_icon((64, 64), "pause")), (64, 64)),
            "lock": _scale((_safe_load_image(assets_root / "lock.png", use_colorkey=False) or _make_icon((48, 48), "lock")), (48, 48)),
            "disk": _scale((_safe_load_image(assets_root / "icon_disk.png", use_colorkey=False) or _make_icon((64, 64), "disk")), (64, 64)),
            "heart": _scale((_safe_load_image(assets_root / "heart.png", use_colorkey=False) or _make_icon((32, 32), "heart")), (32, 32)),
            "icon_extra_life": _scale((_safe_load_image(assets_root / "icon_extra_life.png", use_colorkey=False) or _make_icon((64, 64), "heart")), (64, 64)),
            "icon_slow": _scale((_safe_load_image(assets_root / "icon_slow.png", use_colorkey=False) or _make_icon((64, 64), "other")), (64, 64)),
            "icon_magnet": _scale((_safe_load_image(assets_root / "icon_magnet.png", use_colorkey=False) or _make_icon((64, 64), "other")), (64, 64)),
        }

        return cls(
            root=assets_root,
            bgs={
                "bg_sky_day": bg_day,
                "bg_sky_night": bg_night,
                "bg_forest_day": bg_forest_day,
                "bg_forest_night": bg_forest_night,
            },
            clouds=clouds,
            ground=ground,
            birds=birds,
            pipes=pipes,
            coins=coins,
            ui=ui,
            icons=icons,
        )

