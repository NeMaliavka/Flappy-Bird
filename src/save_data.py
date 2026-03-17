from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


def default_save() -> dict:
    return {
        "coins_total": 0,
        "best_score": 0,
        "selected": {"bird": "bird_blue", "bg": "bg_sky_day", "pipes": "pipe_green"},
        "owned": {
            "birds": ["bird_blue"],
            "bgs": ["bg_sky_day"],
            "pipes": ["pipe_green"],
        },
        "upgrades": {"extra_life_level": 0, "slow_level": 0, "magnet_level": 0},
    }


@dataclass
class SaveData:
    path: Path
    data: dict

    @classmethod
    def load_or_create(cls, path: Path) -> "SaveData":
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("save is not dict")
                return cls(path=path, data=_normalize_save(data))
            except Exception:
                # битый сейв — создаём новый
                data = default_save()
                obj = cls(path=path, data=data)
                obj.save()
                return obj
        data = default_save()
        obj = cls(path=path, data=data)
        obj.save()
        return obj

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")

    @property
    def coins_total(self) -> int:
        return int(self.data.get("coins_total", 0))

    @coins_total.setter
    def coins_total(self, value: int) -> None:
        self.data["coins_total"] = int(max(0, value))

    @property
    def best_score(self) -> int:
        return int(self.data.get("best_score", 0))

    @best_score.setter
    def best_score(self, value: int) -> None:
        self.data["best_score"] = int(max(0, value))


def _normalize_save(d: dict) -> dict:
    base = default_save()

    for k in ("coins_total", "best_score"):
        if k in d:
            base[k] = int(d.get(k, base[k]) or 0)

    selected = d.get("selected", {})
    if isinstance(selected, dict):
        base["selected"]["bird"] = str(selected.get("bird", base["selected"]["bird"]))
        base["selected"]["bg"] = str(selected.get("bg", base["selected"]["bg"]))
        base["selected"]["pipes"] = str(selected.get("pipes", base["selected"]["pipes"]))

    owned = d.get("owned", {})
    if isinstance(owned, dict):
        for cat in ("birds", "bgs", "pipes"):
            v = owned.get(cat, base["owned"][cat])
            if isinstance(v, list):
                base["owned"][cat] = [str(x) for x in v]

    upgrades = d.get("upgrades", {})
    if isinstance(upgrades, dict):
        for k in ("extra_life_level", "slow_level", "magnet_level"):
            base["upgrades"][k] = int(upgrades.get(k, base["upgrades"][k]) or 0)

    # ограничения уровней
    base["upgrades"]["extra_life_level"] = 1 if base["upgrades"]["extra_life_level"] >= 1 else 0
    base["upgrades"]["slow_level"] = max(0, min(3, base["upgrades"]["slow_level"]))
    base["upgrades"]["magnet_level"] = max(0, min(3, base["upgrades"]["magnet_level"]))

    return base

