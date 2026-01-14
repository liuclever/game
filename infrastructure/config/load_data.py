# game/infrastructure/config/load_data.py
from pathlib import Path
import json
from typing import Dict

from domain.entities.map import Map
from domain.entities.monster import Monster

# 项目根目录：.../game
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "configs"


def load_maps() -> Dict[int, Map]:
    path = CONFIG_DIR / "maps.json"
    with path.open("r", encoding="utf-8") as f:
        raw_list = json.load(f)

    maps: Dict[int, Map] = {}
    for item in raw_list:
        m = Map(
            id=item["id"],
            name=item["name"],
            min_level=item["min_level"],
            max_level=item["max_level"],
        )
        maps[m.id] = m
    return maps


def load_monsters() -> Dict[int, Monster]:
    path = CONFIG_DIR / "monsters.json"
    with path.open("r", encoding="utf-8") as f:
        raw_list = json.load(f)

    monsters: Dict[int, Monster] = {}
    for item in raw_list:
        m = Monster(
            id=item["id"],
            name=item["name"],
            map_id=item["map_id"],
            level=item["level"],
            base_exp=item["base_exp"],
            base_gold=item["base_gold"],
        )
        monsters[m.id] = m
    return monsters
