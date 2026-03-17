from __future__ import annotations

from pathlib import Path


EXPECTED = [
    # backgrounds
    "bg_sky_day.png",
    "bg_sky_night.png",
    "bg_forest_day.png",
    "bg_forest_night.png",
    "layer_clouds.png",
    "ground.png",
    # birds
    "bird_blue_1.png",
    "bird_blue_2.png",
    "bird_blue_3.png",
    "bird_pink_1.png",
    "bird_pink_2.png",
    "bird_pink_3.png",
    "bird_ninja_1.png",
    "bird_ninja_2.png",
    "bird_ninja_3.png",
    # pipes
    "pipe_top_green.png",
    "pipe_bottom_green.png",
    "pipe_top_candy.png",
    "pipe_bottom_candy.png",
    "pipe_top_ice.png",
    "pipe_bottom_ice.png",
    # coins/effects
    "coin_1.png",
    "coin_2.png",
    "coin_3.png",
    "sparkle.png",
    "heart.png",
    # ui
    "btn_continue.png",
    "btn_play.png",
    "btn_shop.png",
    "btn_quit.png",
    "btn_menu.png",
    "btn_back.png",
    "btn_save_exit.png",
    "btn_resume.png",
    "tab_skins.png",
    "tab_upgrades.png",
    "btn_pause.png",
    "lock.png",
    "icon_disk.png",
    "icon_extra_life.png",
    "icon_slow.png",
    "icon_magnet.png",
]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    assets = root / "assets"
    missing = [name for name in EXPECTED if not (assets / name).exists()]
    if not missing:
        print("OK: все ожидаемые картинки на месте.")
        return
    print("Не хватает файлов:")
    for m in missing:
        print("-", m)


if __name__ == "__main__":
    main()

