# application/services/vip_service.py
"""VIP特权服务 - 统一管理VIP特权配置读取"""

import json
import os
from functools import lru_cache
from typing import Dict, Any, Optional


@lru_cache(maxsize=1)
def _load_vip_config() -> Dict[str, Any]:
    """加载VIP配置（带缓存）"""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', 'configs', 'vip_privileges.json'
    )
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"vip_levels": []}


def get_vip_privileges(vip_level: int) -> Dict[str, Any]:
    """获取指定VIP等级的特权配置"""
    config = _load_vip_config()
    for lv in config.get('vip_levels', []):
        if lv.get('level') == vip_level:
            return lv.get('privileges', {})
    # 返回VIP0的默认值
    return {
        'daily_copper_chest': 0,
        'fortune_talisman_uses': 3,
        'vitality_max': 100,
        'cultivation_modes': [8],
        'arena_normal_limit': 5,
        'arena_gold_limit': 10,
        'beast_slot': 5,
        'manor_yellow_land_open': False,
        'manor_silver_land_open': False,
        'manor_gold_land_open': False,
        'war_spirit_free_wash': 1,
    }


def get_fortune_talisman_limit(vip_level: int) -> int:
    """获取招财神符每日使用次数上限"""
    return get_vip_privileges(vip_level).get('fortune_talisman_uses', 3)


def get_vitality_max(vip_level: int) -> int:
    """获取活力值上限"""
    return get_vip_privileges(vip_level).get('vitality_max', 100)


def get_arena_limits(vip_level: int) -> tuple:
    """获取擂台次数限制 (普通场, 黄金场)"""
    priv = get_vip_privileges(vip_level)
    return priv.get('arena_normal_limit', 5), priv.get('arena_gold_limit', 10)


def get_beast_slot_limit(vip_level: int) -> int:
    """获取幻兽栏数量上限"""
    return get_vip_privileges(vip_level).get('beast_slot', 5)


def get_cultivation_modes(vip_level: int) -> list:
    """获取可用的修炼时长模式"""
    return get_vip_privileges(vip_level).get('cultivation_modes', [8])


def can_use_manor_land(vip_level: int, land_type: str) -> bool:
    """检查是否可以使用庄园土地"""
    priv = get_vip_privileges(vip_level)
    if land_type == 'yellow':
        return priv.get('manor_yellow_land_open', False)
    elif land_type == 'silver':
        return priv.get('manor_silver_land_open', False)
    elif land_type == 'gold':
        return priv.get('manor_gold_land_open', False)
    return False


def get_war_spirit_free_wash(vip_level: int) -> int:
    """获取战灵每日免费洗练次数"""
    return get_vip_privileges(vip_level).get('war_spirit_free_wash', 1)
