from typing import Optional, Dict
from pathlib import Path
import json

from domain.entities.item import Item
from domain.repositories.item_repo import IItemRepo


class ConfigItemRepo(IItemRepo):
    """从 configs/items.json 读取物品模板。

    注意：为了方便开发期修改配置后无需重启服务，这个仓库会在读取时检测
    items.json 的 mtime 变化并自动重新加载。
    """

    def __init__(self):
        self._items: Dict[int, Item] = {}
        base_dir = Path(__file__).resolve().parents[2]
        self._path = base_dir / "configs" / "items.json"
        self._last_mtime: Optional[float] = None
        self._load()

    def _load(self):
        with self._path.open("r", encoding="utf-8") as f:
            raw_list = json.load(f)

        items: Dict[int, Item] = {}
        for item in raw_list:
            items[item["id"]] = Item(
                id=item["id"],
                name=item["name"],
                type=item.get("type", "material"),
                description=item.get("description", ""),
                stackable=item.get("stackable", True),
                max_stack=item.get("max_stack", 9999),
                use_effect=item.get("use_effect"),
            )

        self._items = items
        try:
            self._last_mtime = self._path.stat().st_mtime
        except OSError:
            # 文件不存在/不可访问时不阻塞；保持现有缓存
            pass

    def _ensure_latest(self):
        try:
            mtime = self._path.stat().st_mtime
        except OSError:
            return

        if self._last_mtime is None or mtime > self._last_mtime:
            self._load()

    def get_by_id(self, item_id: int) -> Optional[Item]:
        self._ensure_latest()
        return self._items.get(item_id)

    def get_all(self) -> Dict[int, Item]:
        self._ensure_latest()
        return self._items.copy()