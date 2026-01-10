"""
龙宫之谜活动配置加载（进程内缓存）。

数据来源：configs/dragonpalace.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

_CACHE: Optional[Dict[str, Any]] = None


def get_dragonpalace_config() -> Dict[str, Any]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    root = Path(__file__).resolve().parents[2]
    p = root / "configs" / "dragonpalace.json"
    with p.open("r", encoding="utf-8") as f:
        _CACHE = json.load(f)
    return _CACHE


