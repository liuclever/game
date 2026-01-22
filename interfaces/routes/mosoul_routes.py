"""
魔魂相关API路由
"""
import json
from pathlib import Path

from flask import Blueprint, jsonify, request, session

from domain.entities.mosoul import MoSoul, MoSoulGrade, get_mosoul_template
from domain.rules.mosoul_rules import check_equip_conflict
from infrastructure.db import mosoul_repo_mysql as mosoul_repo
from infrastructure.db import player_beast_repo_mysql as beast_repo
from infrastructure.db.connection import execute_query, execute_update
from domain.services.beast_stats import calc_max_mosoul_slots

mosoul_bp = Blueprint('mosoul', __name__, url_prefix='/api/mosoul')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


_mosoul_upgrade_config_cache: dict | None = None


def _load_mosoul_upgrade_config() -> dict:
    global _mosoul_upgrade_config_cache
    if _mosoul_upgrade_config_cache is not None:
        return _mosoul_upgrade_config_cache

    base_dir = Path(__file__).resolve().parents[2]
    path = base_dir / 'configs' / 'mosoul_upgrade.json'
    try:
        with path.open('r', encoding='utf-8') as f:
            _mosoul_upgrade_config_cache = json.load(f)
    except Exception:
        _mosoul_upgrade_config_cache = {}
    return _mosoul_upgrade_config_cache


def get_soul_container_capacity(vip_level: int) -> int:
    return 100


def _get_exp_required_for_level(grade: str, level: int) -> int:
    if not grade or not level or level >= 10:
        return 0

    cfg = _load_mosoul_upgrade_config()
    upgrade_exp = (cfg.get('upgrade_exp') or {}).get(grade, {})
    levels = upgrade_exp.get('levels') or {}
    return int(levels.get(str(level), 0) or 0)


def _get_grade_exp_provide(grade: str) -> int:
    cfg = _load_mosoul_upgrade_config()
    exp_map = cfg.get('grade_exp_provide') or {}
    return int(exp_map.get(grade, 0) or 0)


def _calc_level_and_exp(
    grade: str,
    current_level: int,
    current_exp: int,
    add_exp: int,
) -> tuple[int, int, int]:
    if current_level >= 10:
        return 10, int(current_exp or 0), 0

    lvl = int(current_level or 1)
    exp = int(current_exp or 0) + int(add_exp or 0)
    gained = 0

    while lvl < 10:
        required = _get_exp_required_for_level(grade, lvl)
        if required <= 0:
            break
        if exp >= required:
            exp -= required
            lvl += 1
            gained += 1
        else:
            break

    if lvl >= 10:
        lvl = 10
        exp = 0

    return lvl, exp, gained


# ===================== 属性名称映射 =====================
ATTR_NAMES = {
    'hp': '气血',
    'physical_attack': '物攻',
    'magic_attack': '法攻',
    'physical_defense': '物防',
    'magic_defense': '法防',
    'speed': '速度',
}


def format_effect_text(effects: list, level: int) -> str:
    """格式化效果为显示文本，如 '物攻+840'"""
    parts = []
    for eff in effects:
        attr = eff.get('attr', '')
        attr_name = ATTR_NAMES.get(attr, attr)
        flat = eff.get('flat', 0) * level
        percent = eff.get('percent', 0) * level
        
        if flat > 0:
            parts.append(f"{attr_name}+{int(flat)}")
        elif percent > 0:
            parts.append(f"{attr_name}+{percent:.1f}%")
    
    return ' '.join(parts)


def ensure_mosoul_level(mosoul_row: dict) -> dict:
    """确保魔魂等级与经验匹配（自动升级）
    
    如果经验超过当前等级所需，则自动升级并更新数据库。
    """
    template = get_mosoul_template(mosoul_row['template_id'])
    if not template:
        return mosoul_row
    
    current_level = mosoul_row['level']
    current_exp = mosoul_row['exp']
    
    if current_level >= 10:
        return mosoul_row
    
    required = _get_exp_required_for_level(template.grade.value, current_level)
    if required > 0 and current_exp >= required:
        # 需要升级
        new_level, new_exp, levels_gained = _calc_level_and_exp(
            template.grade.value,
            current_level,
            current_exp,
            0 # 不增加新经验，只是消耗现有经验升级
        )
        if levels_gained > 0:
            mosoul_repo.update_mosoul(mosoul_row['id'], level=new_level, exp=new_exp)
            # 更新内存中的行数据
            mosoul_row['level'] = new_level
            mosoul_row['exp'] = new_exp
            
    return mosoul_row


def mosoul_to_detail(mosoul_row: dict) -> dict:
    """将数据库魔魂行转换为详情字典"""
    # 自动检查升级
    mosoul_row = ensure_mosoul_level(mosoul_row)
    
    template = get_mosoul_template(mosoul_row['template_id'])
    if not template:
        return None
    
    level = mosoul_row['level']
    effects = template.effects
    
    # 计算魂力（基于等级和品质）
    grade_soul_power = {
        MoSoulGrade.GOD_SOUL: 5000,
        MoSoulGrade.DRAGON_SOUL: 3000,
        MoSoulGrade.HEAVEN_SOUL: 1500,
        MoSoulGrade.EARTH_SOUL: 800,
        MoSoulGrade.DARK_SOUL: 400,
        MoSoulGrade.YELLOW_SOUL: 200,
        MoSoulGrade.WASTE_SOUL: 0,
    }
    base_power = grade_soul_power.get(template.grade, 0)
    soul_power = base_power * level
    
    # 获取升级所需经验
    max_exp = _get_exp_required_for_level(template.grade.value, level)
    
    return {
        'id': mosoul_row['id'],
        'template_id': mosoul_row['template_id'],
        'name': template.name,
        'grade': template.grade.value,
        'grade_name': template.grade.chinese_name,
        'level': level,
        'exp': mosoul_row['exp'],
        'max_exp': max_exp,
        'beast_id': mosoul_row['beast_id'],
        'slot_index': mosoul_row.get('slot_index'),
        'effect_text': format_effect_text(effects, level),
        'effects': [
            {
                'attr': e['attr'],
                'attr_name': ATTR_NAMES.get(e['attr'], e['attr']),
                'flat': e.get('flat', 0) * level,
                'percent': e.get('percent', 0) * level,
            }
            for e in effects
        ],
        'soul_power': soul_power,
    }


@mosoul_bp.get('/overview')
def get_mosoul_overview():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    from interfaces.web_api.bootstrap import services

    warehouse_capacity = get_soul_container_capacity(0)
    warehouse_count = len(mosoul_repo.get_unequipped_mosouls(user_id))

    beasts = []
    all_beasts = services.player_beast_repo.get_all_by_user(user_id)
    for b in all_beasts:
        status = '战' if getattr(b, 'is_in_team', 0) == 1 else '待'
        max_slots = calc_max_mosoul_slots(getattr(b, 'level', 0) or 0)

        equipped_rows = mosoul_repo.get_mosouls_by_beast(b.id)
        equipped_details = []
        for r in equipped_rows:
            d = mosoul_to_detail(r)
            if d:
                equipped_details.append(d)

        used_slots = len(equipped_details)
        total_soul_power = sum(int(x.get('soul_power', 0) or 0) for x in equipped_details)

        status_text = ''
        if max_slots <= 0:
            status_text = '幻兽30级时开启'

        beasts.append({
            'id': b.id,
            'name': getattr(b, 'nickname', None) or getattr(b, 'name', ''),
            'realm': getattr(b, 'realm', ''),
            'level': getattr(b, 'level', 1),
            'status': status,
            'max_slots': max_slots,
            'used_slots': used_slots,
            'total_soul_power': total_soul_power,
            'status_text': status_text,
        })

    return jsonify({
        'ok': True,
        'warehouse_count': warehouse_count,
        'warehouse_capacity': warehouse_capacity,
        'beasts': beasts,
    })


@mosoul_bp.get('/warehouse')
def get_mosoul_warehouse():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    grade = (request.args.get('grade') or '').strip()
    page = int(request.args.get('page') or 1)
    page_size = int(request.args.get('pageSize') or 10)

    warehouse_capacity = get_soul_container_capacity(0)

    all_rows = mosoul_repo.get_unequipped_mosouls(user_id)
    warehouse_count = len(all_rows)

    details = []
    for r in all_rows:
        d = mosoul_to_detail(r)
        if not d:
            continue
        if grade and d.get('grade') != grade:
            continue
        details.append(d)

    total = len(details)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    page_items = details[start:end]

    return jsonify({
        'ok': True,
        'warehouse_count': warehouse_count,
        'warehouse_capacity': warehouse_capacity,
        'mosouls': page_items,
        'total': total,
        'totalPages': total_pages,
    })


@mosoul_bp.get('/player')
def get_player_mosouls():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    page = int(request.args.get('page') or 1)
    page_size = int(request.args.get('pageSize') or 10)

    all_rows = mosoul_repo.get_unequipped_mosouls(user_id)
    details = []
    for r in all_rows:
        d = mosoul_to_detail(r)
        if d:
            details.append(d)

    total = len(details)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    page_items = details[start:end]

    return jsonify({
        'ok': True,
        'mosouls': page_items,
        'total': total,
        'totalPages': total_pages,
    })


@mosoul_bp.get('/<int:mosoul_id>')
def get_mosoul_detail(mosoul_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    row = mosoul_repo.get_mosoul_by_id(mosoul_id)
    if not row or int(row.get('user_id', 0) or 0) != int(user_id):
        return jsonify({'ok': False, 'error': '魔魂不存在'})

    return jsonify({
        'ok': True,
        'mosoul': mosoul_to_detail(row),
    })


@mosoul_bp.get('/beast/<int:beast_id>')
def get_beast_mosouls(beast_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    from interfaces.web_api.bootstrap import services

    beast = services.player_beast_repo.get_by_user_and_id(user_id, beast_id)
    if not beast:
        return jsonify({'ok': False, 'error': '幻兽不存在'})

    max_slots = calc_max_mosoul_slots(getattr(beast, 'level', 0) or 0)
    equipped_rows = mosoul_repo.get_mosouls_by_beast(beast_id)
    equipped = []
    for r in equipped_rows:
        d = mosoul_to_detail(r)
        if d:
            equipped.append(d)

    used_slots = len(equipped)
    total_soul_power = sum(int(x.get('soul_power', 0) or 0) for x in equipped)

    slot_unlock_info = []
    for i in range(1, max_slots + 1):
        slot_unlock_info.append({'slot_index': i, 'unlocked': True, 'unlock_text': ''})

    return jsonify({
        'ok': True,
        'beast_name': getattr(beast, 'nickname', None) or getattr(beast, 'name', ''),
        'beast_level': beast.level,
        'mosouls': equipped,
        'used_slots': used_slots,
        'max_slots': max_slots,
        'total_soul_power': total_soul_power,
        'slot_unlock_info': slot_unlock_info,
    })


@mosoul_bp.post('/equip/<int:mosoul_id>')
def equip_mosoul(mosoul_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    data = request.get_json() or {}
    beast_id = int(data.get('beastId') or 0)
    slot_index = int(data.get('slotIndex') or 0)
    if not beast_id or not slot_index:
        return jsonify({'ok': False, 'error': '参数缺失'}), 400

    beast_row = beast_repo.get_beast_by_id(beast_id)
    if not beast_row or int(beast_row.get('user_id', 0) or 0) != int(user_id):
        return jsonify({'ok': False, 'error': '幻兽不存在'}), 404

    beast_level = int(beast_row.get('level', 1) or 1)
    max_slots = calc_max_mosoul_slots(beast_level)
    if slot_index < 1 or slot_index > max_slots:
        return jsonify({'ok': False, 'error': '槽位未解锁'}), 400

    row = mosoul_repo.get_mosoul_by_id(mosoul_id)
    if not row or int(row.get('user_id', 0) or 0) != int(user_id):
        return jsonify({'ok': False, 'error': '魔魂不存在'}), 404

    cur_beast_id = row.get('beast_id')
    if cur_beast_id is not None and int(cur_beast_id) != int(beast_id):
        return jsonify({'ok': False, 'error': '该魔魂已装备在其他幻兽上，请先卸下'}), 400

    equipped_rows = mosoul_repo.get_mosouls_by_beast(beast_id)
    for r in equipped_rows:
        if int(r.get('id', 0) or 0) == int(mosoul_id):
            continue
        if int(r.get('slot_index', 0) or 0) == int(slot_index):
            return jsonify({'ok': False, 'error': '该槽位已装备魔魂，请先取下'}), 400

    # 若是“同一只幻兽上的换槽位”，放行（避免因为历史违规装备导致无法整理槽位）
    if cur_beast_id is None:
        # 冲突检测（同名唯一、天/地/玄/黄同属性同类型互斥、龙魂百分比互斥）
        new_soul = MoSoul(
            id=int(row.get('id')),
            user_id=int(row.get('user_id')),
            template_id=int(row.get('template_id')),
            level=int(row.get('level', 1) or 1),
            exp=int(row.get('exp', 0) or 0),
            beast_id=None,
        )

        equipped_souls = []
        for r in equipped_rows:
            equipped_souls.append(
                MoSoul(
                    id=int(r.get('id')),
                    user_id=int(r.get('user_id')),
                    template_id=int(r.get('template_id')),
                    level=int(r.get('level', 1) or 1),
                    exp=int(r.get('exp', 0) or 0),
                    beast_id=int(r.get('beast_id')) if r.get('beast_id') is not None else None,
                )
            )

        from domain.entities.mosoul import BeastMoSoulSlot
        slot = BeastMoSoulSlot(
            beast_id=int(beast_id),
            beast_level=int(beast_level),
            equipped_souls=equipped_souls,
        )

        conflict = check_equip_conflict(new_soul, slot)
        if conflict.has_conflict:
            return jsonify({'ok': False, 'error': conflict.message}), 400

    mosoul_repo.equip_mosoul_with_slot(mosoul_id, beast_id, slot_index)
    return jsonify({'ok': True, 'message': '装备成功'})


@mosoul_bp.post('/unequip/<int:mosoul_id>')
def unequip_mosoul(mosoul_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    row = mosoul_repo.get_mosoul_by_id(mosoul_id)
    if not row or int(row.get('user_id', 0) or 0) != int(user_id):
        return jsonify({'ok': False, 'error': '魔魂不存在'})

    mosoul_repo.unequip_mosoul(mosoul_id)
    return jsonify({'ok': True, 'message': '卸下成功'})


@mosoul_bp.post('/consume/<int:material_mosoul_id>')
def consume_mosoul(material_mosoul_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    data = request.get_json() or {}
    target_id = int(data.get('targetMosoulId') or 0)
    if not target_id:
        return jsonify({'ok': False, 'error': '缺少目标魔魂'})

    if target_id == material_mosoul_id:
        return jsonify({'ok': False, 'error': '目标魔魂不能吞噬自身'})

    target_row = mosoul_repo.get_mosoul_by_id(target_id)
    if not target_row or int(target_row.get('user_id', 0) or 0) != int(user_id):
        return jsonify({'ok': False, 'error': '目标魔魂不存在'})

    material_row = mosoul_repo.get_mosoul_by_id(material_mosoul_id)
    if not material_row or int(material_row.get('user_id', 0) or 0) != int(user_id):
        return jsonify({'ok': False, 'error': '材料魔魂不存在'})

    if material_row.get('beast_id') is not None:
        return jsonify({'ok': False, 'error': '材料魔魂已装备，无法吞噬'})

    target_detail = mosoul_to_detail(target_row)
    material_detail = mosoul_to_detail(material_row)
    if not target_detail or not material_detail:
        return jsonify({'ok': False, 'error': '魔魂数据异常'})

    if int(target_detail.get('level', 1) or 1) >= 10:
        return jsonify({'ok': False, 'error': '目标魔魂已满级'})

    exp_gain = _get_grade_exp_provide(material_detail.get('grade'))
    old_level = int(target_row.get('level', 1) or 1)
    old_exp = int(target_row.get('exp', 0) or 0)
    new_level, new_exp, _ = _calc_level_and_exp(target_detail.get('grade'), old_level, old_exp, exp_gain)

    mosoul_repo.update_mosoul(target_id, level=new_level, exp=new_exp)
    mosoul_repo.delete_mosoul(material_mosoul_id)

    is_max = new_level >= 10
    return jsonify({
        'ok': True,
        'message': '摄魂成功',
        'old_level': old_level,
        'new_level': new_level,
        'levels_gained': max(0, new_level - old_level),
        'is_max_level': is_max,
    })


@mosoul_bp.post('/consume/batch')
def consume_mosoul_batch():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})

    data = request.get_json() or {}
    target_id = int(data.get('targetMosoulId') or 0)
    grade_filter = (data.get('grade') or '').strip()

    if not target_id:
        return jsonify({'ok': False, 'error': '缺少目标魔魂'})

    target_row = mosoul_repo.get_mosoul_by_id(target_id)
    if not target_row or int(target_row.get('user_id', 0) or 0) != int(user_id):
        return jsonify({'ok': False, 'error': '目标魔魂不存在'})

    target_detail = mosoul_to_detail(target_row)
    if not target_detail:
        return jsonify({'ok': False, 'error': '目标魔魂数据异常'})

    all_rows = mosoul_repo.get_unequipped_mosouls(user_id)

    materials = []
    for r in all_rows:
        if int(r.get('id', 0) or 0) == target_id:
            continue
        d = mosoul_to_detail(r)
        if not d:
            continue
        if grade_filter and d.get('grade') != grade_filter:
            continue
        materials.append((r, d))

    if not materials:
        return jsonify({'ok': False, 'error': '没有可吞噬的材料魔魂'})

    total_exp = sum(_get_grade_exp_provide(d.get('grade')) for (_, d) in materials)

    old_level = int(target_row.get('level', 1) or 1)
    old_exp = int(target_row.get('exp', 0) or 0)
    new_level, new_exp, _ = _calc_level_and_exp(target_detail.get('grade'), old_level, old_exp, total_exp)

    exp_used = 0
    if old_level < 10:
        needed = 0
        lvl = old_level
        exp_cur = old_exp
        remaining = total_exp
        while remaining > 0 and lvl < 10:
            required = _get_exp_required_for_level(target_detail.get('grade'), lvl)
            if required <= 0:
                break
            need = max(0, required - exp_cur)
            if remaining >= need:
                exp_used += need
                remaining -= need
                exp_cur = 0
                lvl += 1
            else:
                exp_used += remaining
                remaining = 0
                exp_cur += remaining
        if new_level < 10:
            exp_used = min(total_exp, exp_used + max(0, new_exp - old_exp))

    exp_wasted = max(0, total_exp - exp_used)

    mosoul_repo.update_mosoul(target_id, level=new_level, exp=new_exp)
    for (r, _) in materials:
        mosoul_repo.delete_mosoul(int(r.get('id')))

    return jsonify({
        'ok': True,
        'message': f'一键噬魂成功，吞噬{len(materials)}个材料魔魂',
        'consumed_count': len(materials),
        'exp_total': total_exp,
        'exp_used': exp_used,
        'exp_wasted': exp_wasted,
        'before_level': old_level,
        'after_level': new_level,
    })


# ========== 猎魂系统配置 ==========
# 猎魂师配置
HUNTER_CONFIG = {
    'amy': {'name': '艾米', 'cost': 8000, 'next': 'keke', 'unlock_rate': 50},
    'keke': {'name': '科科', 'cost': 10000, 'next': 'boer', 'unlock_rate': 35},
    'boer': {'name': '波尔', 'cost': 20000, 'next': 'wote', 'unlock_rate': 20},
    'wote': {'name': '沃特', 'cost': 40000, 'next': 'kaiwen', 'unlock_rate': 5},
    'kaiwen': {'name': '凯文', 'cost': 60000, 'next': None, 'unlock_rate': 0},
}

# 普通场魔魂概率（百分比）
NORMAL_GRADE_WEIGHTS = {
    'amy': {'waste_soul': 33.3, 'yellow_soul': 33.3, 'dark_soul': 33.4},
    'keke': {'waste_soul': 30, 'yellow_soul': 35, 'dark_soul': 35},
    'boer': {'waste_soul': 20, 'yellow_soul': 20, 'dark_soul': 20, 'earth_soul': 20},
    'wote': {'waste_soul': 8, 'yellow_soul': 30, 'dark_soul': 30, 'earth_soul': 30},
    'kaiwen': {'yellow_soul': 25, 'dark_soul': 25, 'earth_soul': 31},
}

# 高级场配置
ADVANCED_HUNTER_CONFIG = {
    'wote': {'name': '沃特', 'cost': 4, 'cost_type': 'fabao', 'next': 'kaiwen', 'unlock_rate': 10},
    'kaiwen': {'name': '凯文', 'cost': 6, 'cost_type': 'fabao', 'next': None, 'unlock_rate': 0},
}

# 高级场魔魂概率
ADVANCED_GRADE_WEIGHTS = {
    'wote': {'earth_soul': 84, 'heaven_soul': 16},
    'kaiwen': {'god_soul': 32, 'earth_soul': 32, 'heaven_soul': 35.1},
}

# 魔魂模板映射
GRADE_TEMPLATES = {
    'god_soul': [1],
    'dragon_soul': [101, 102, 103],
    'heaven_soul': [201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212],
    'earth_soul': [301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312],
    'dark_soul': [401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412],
    'yellow_soul': [501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512],
    'waste_soul': [901, 902, 903, 904, 905],
}

SOUL_CHARM_ITEM_ID = 6019
NORMAL_HEAVEN_PITY_COPPER = 2_000_000
ADV_PERSONAL_DRAGON_PITY = 5_000
ADV_GLOBAL_DRAGON_PITY = 40_000
NORMAL_HEAVEN_PITY_COUNTER_KEY = 'normal_heaven_pity'

_hunting_tables_ready = False


def _ensure_hunting_tables() -> None:
    global _hunting_tables_ready
    if _hunting_tables_ready:
        return

    execute_update(
        """
        CREATE TABLE IF NOT EXISTS mosoul_hunting_state (
            user_id BIGINT UNSIGNED PRIMARY KEY,
            field_type VARCHAR(20) NOT NULL DEFAULT 'normal',
            normal_available_npcs JSON NOT NULL DEFAULT ('["amy"]'),
            advanced_available_npcs JSON NOT NULL DEFAULT ('["wote"]'),
            soul_charm_consumed BIGINT UNSIGNED NOT NULL DEFAULT 0,
            copper_consumed BIGINT UNSIGNED NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    execute_update(
        """
        CREATE TABLE IF NOT EXISTS mosoul_global_pity (
            counter_key VARCHAR(50) PRIMARY KEY,
            count INT UNSIGNED NOT NULL DEFAULT 0,
            pity_threshold INT UNSIGNED NOT NULL DEFAULT 40000,
            soul_charm_consumed_global BIGINT UNSIGNED NOT NULL DEFAULT 0,
            copper_consumed_global BIGINT UNSIGNED NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    try:
        execute_update(
            """
            ALTER TABLE mosoul_global_pity
            ADD COLUMN copper_consumed_global BIGINT UNSIGNED NOT NULL DEFAULT 0
            """
        )
    except Exception:
        pass

    try:
        execute_update(
            """
            INSERT INTO mosoul_global_pity (counter_key, count, pity_threshold, soul_charm_consumed_global, copper_consumed_global)
            VALUES ('kevin_adv_pity', 0, 40000, 0, 0)
            ON DUPLICATE KEY UPDATE counter_key = VALUES(counter_key)
            """
        )
        execute_update(
            """
            INSERT INTO mosoul_global_pity (counter_key, count, pity_threshold, soul_charm_consumed_global, copper_consumed_global)
            VALUES (%s, 0, %s, 0, 0)
            ON DUPLICATE KEY UPDATE counter_key = VALUES(counter_key)
            """,
            (NORMAL_HEAVEN_PITY_COUNTER_KEY, NORMAL_HEAVEN_PITY_COPPER),
        )
    except Exception:
        execute_update(
            """
            INSERT INTO mosoul_global_pity (counter_key, count, pity_threshold, soul_charm_consumed_global)
            VALUES ('kevin_adv_pity', 0, 40000, 0)
            ON DUPLICATE KEY UPDATE counter_key = VALUES(counter_key)
            """
        )

    _hunting_tables_ready = True


def _get_personal_consumed(user_id: int) -> tuple[int, int]:
    _ensure_hunting_tables()
    rows = execute_query(
        "SELECT soul_charm_consumed, copper_consumed FROM mosoul_hunting_state WHERE user_id = %s",
        (user_id,),
    )
    if not rows:
        execute_update(
            """
            INSERT INTO mosoul_hunting_state (user_id, field_type, normal_available_npcs, advanced_available_npcs, soul_charm_consumed, copper_consumed)
            VALUES (%s, 'normal', '["amy"]', '["wote"]', 0, 0)
            """,
            (user_id,),
        )
        return 0, 0
    row = rows[0]
    return int(row.get('soul_charm_consumed', 0) or 0), int(row.get('copper_consumed', 0) or 0)


def _save_personal_consumed(user_id: int, soul_charm_consumed: int, copper_consumed: int) -> None:
    _ensure_hunting_tables()
    execute_update(
        """
        INSERT INTO mosoul_hunting_state (user_id, field_type, normal_available_npcs, advanced_available_npcs, soul_charm_consumed, copper_consumed)
        VALUES (%s, 'normal', '["amy"]', '["wote"]', %s, %s)
        ON DUPLICATE KEY UPDATE
            soul_charm_consumed = VALUES(soul_charm_consumed),
            copper_consumed = VALUES(copper_consumed)
        """,
        (user_id, int(soul_charm_consumed), int(copper_consumed)),
    )


def _get_global_soul_charm_consumed(counter_key: str = 'kevin_adv_pity') -> int:
    _ensure_hunting_tables()
    rows = execute_query(
        "SELECT soul_charm_consumed_global FROM mosoul_global_pity WHERE counter_key = %s",
        (counter_key,),
    )
    if not rows:
        return 0
    return int(rows[0].get('soul_charm_consumed_global', 0) or 0)


def _save_global_soul_charm_consumed(consumed: int, counter_key: str = 'kevin_adv_pity') -> None:
    _ensure_hunting_tables()
    execute_update(
        """
        INSERT INTO mosoul_global_pity (counter_key, count, pity_threshold, soul_charm_consumed_global)
        VALUES (%s, 0, 40000, %s)
        ON DUPLICATE KEY UPDATE soul_charm_consumed_global = VALUES(soul_charm_consumed_global)
        """,
        (counter_key, int(consumed)),
    )


def _get_global_copper_consumed(counter_key: str = NORMAL_HEAVEN_PITY_COUNTER_KEY) -> int:
    _ensure_hunting_tables()
    rows = execute_query(
        "SELECT copper_consumed_global FROM mosoul_global_pity WHERE counter_key = %s",
        (counter_key,),
    )
    if not rows:
        return 0
    return int(rows[0].get('copper_consumed_global', 0) or 0)


def _save_global_copper_consumed(consumed: int, counter_key: str = NORMAL_HEAVEN_PITY_COUNTER_KEY) -> None:
    _ensure_hunting_tables()
    execute_update(
        """
        INSERT INTO mosoul_global_pity (counter_key, count, pity_threshold, soul_charm_consumed_global, copper_consumed_global)
        VALUES (%s, 0, %s, 0, %s)
        ON DUPLICATE KEY UPDATE copper_consumed_global = VALUES(copper_consumed_global)
        """,
        (counter_key, NORMAL_HEAVEN_PITY_COPPER, int(consumed)),
    )


@mosoul_bp.get('/hunting')
def get_hunting_page():
    """获取猎魂页面数据"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})
    
    arena_type = request.args.get('arena', 'normal')
    
    from infrastructure.db import player_repo_mysql as player_repo
    from interfaces.web_api.bootstrap import services
    player = player_repo.get_player_by_id(user_id)
    gold = player.get('gold', 0) if player else 0
    soul_charm = services.inventory_service.get_item_count(user_id, SOUL_CHARM_ITEM_ID, include_temp=True)
    
    # 获取玩家当前解锁的猎魂师状态（从 session 获取）
    hunting_state = session.get(f'hunting_state_{arena_type}', {})
    
    if arena_type == 'normal':
        # 普通场：5个猎魂师
        hunters = []
        for hid in ['amy', 'keke', 'boer', 'wote', 'kaiwen']:
            cfg = HUNTER_CONFIG[hid]
            hunter = {
                'id': hid,
                'name': cfg['name'],
                'cost': cfg['cost'],
                'available': False,
            }
            # 艾米始终可点击
            if hid == 'amy':
                hunter['available'] = True
            # 其他猎魂师需要解锁
            elif hunting_state.get(f'{hid}_unlocked', False):
                hunter['available'] = True
            hunters.append(hunter)
    else:
        # 高级场：只有沃特和凯文
        hunters = []
        for hid in ['wote', 'kaiwen']:
            cfg = ADVANCED_HUNTER_CONFIG[hid]
            hunter = {
                'id': hid,
                'name': cfg['name'],
                'cost': cfg['cost'],
                'cost_type': cfg['cost_type'],
                'available': False,
            }
            # 沃特始终可点击
            if hid == 'wote':
                hunter['available'] = True
            elif hunting_state.get('kaiwen_unlocked', False):
                hunter['available'] = True
            hunters.append(hunter)
    
    return jsonify({
        'ok': True,
        'arena_type': arena_type,
        'hunters': hunters,
        'gold': gold,
        'soul_charm': soul_charm,
    })


@mosoul_bp.post('/hunting/hunt')
def do_hunting():
    """执行猎魂"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})
    
    data = request.get_json() or {}
    hunter_id = data.get('hunterId')
    arena_type = data.get('arenaType', 'normal')
    
    if not hunter_id:
        return jsonify({'ok': False, 'error': '请选择猎魂师'})

    warehouse_capacity = get_soul_container_capacity(0)
    warehouse_count = len(mosoul_repo.get_unequipped_mosouls(user_id))
    if warehouse_count >= warehouse_capacity:
        return jsonify({'ok': False, 'error': f'储魂器已满（{warehouse_count}/{warehouse_capacity}），无法继续猎魂'})
    
    from infrastructure.db import player_repo_mysql as player_repo
    from interfaces.web_api.bootstrap import services
    import random
    
    # 获取玩家铜钱
    player = player_repo.get_player_by_id(user_id)
    gold = player.get('gold', 0) if player else 0
    
    # 获取当前猎魂状态
    state_key = f'hunting_state_{arena_type}'
    hunting_state = session.get(state_key, {})
    
    if arena_type == 'normal':
        # === 普通场逻辑 ===
        if hunter_id not in HUNTER_CONFIG:
            return jsonify({'ok': False, 'error': '无效的猎魂师'})
        
        cfg = HUNTER_CONFIG[hunter_id]
        cost = cfg['cost']
        
        # 检查是否可点击
        if hunter_id != 'amy' and not hunting_state.get(f'{hunter_id}_unlocked', False):
            return jsonify({'ok': False, 'error': f'{cfg["name"]}尚未解锁'})
        
        # 检查铜钱
        if gold < cost:
            return jsonify({'ok': False, 'error': '铜钱不足'})
        
        # 扣除铜钱
        player_repo.update_gold(user_id, -cost)
        gold -= cost

        global_copper_consumed = _get_global_copper_consumed(NORMAL_HEAVEN_PITY_COUNTER_KEY)
        global_copper_consumed += int(cost)
        force_heaven = False
        if global_copper_consumed >= NORMAL_HEAVEN_PITY_COPPER and hunter_id in ('wote', 'kaiwen'):
            global_copper_consumed = 0
            force_heaven = True
        _save_global_copper_consumed(global_copper_consumed, NORMAL_HEAVEN_PITY_COUNTER_KEY)
        
        # 点击后清除当前猎魂师的解锁状态（除了艾米）
        if hunter_id != 'amy':
            hunting_state[f'{hunter_id}_unlocked'] = False
        
        # 尝试解锁下一个猎魂师
        next_hunter = cfg.get('next')
        next_unlocked = False
        if next_hunter and cfg['unlock_rate'] > 0:
            if random.random() * 100 < cfg['unlock_rate']:
                hunting_state[f'{next_hunter}_unlocked'] = True
                next_unlocked = True
        
        # 保存状态
        session[state_key] = hunting_state
        
        # 随机魔魂
        weights = NORMAL_GRADE_WEIGHTS.get(hunter_id, {'yellow_soul': 100})
        grades = list(weights.keys())
        probs = list(weights.values())
        chosen_grade = random.choices(grades, weights=probs, k=1)[0]

        if force_heaven:
            chosen_grade = 'heaven_soul'

        if chosen_grade == 'dragon_soul':
            chosen_grade = 'earth_soul'
        
    else:
        # === 高级场逻辑 ===
        if hunter_id not in ADVANCED_HUNTER_CONFIG:
            return jsonify({'ok': False, 'error': '高级场无此猎魂师'})
        
        cfg = ADVANCED_HUNTER_CONFIG[hunter_id]
        cost = int(cfg['cost'])
        
        # 检查是否可点击
        if hunter_id == 'kaiwen' and not hunting_state.get('kaiwen_unlocked', False):
            return jsonify({'ok': False, 'error': '凯文尚未解锁'})

        soul_charm_count = services.inventory_service.get_item_count(user_id, SOUL_CHARM_ITEM_ID, include_temp=True)
        if soul_charm_count < cost:
            return jsonify({'ok': False, 'error': '追魂法宝不足'})

        services.inventory_service.remove_item(user_id, SOUL_CHARM_ITEM_ID, cost)
        
        # 点击后清除凯文解锁状态
        if hunter_id == 'kaiwen':
            hunting_state['kaiwen_unlocked'] = False
        
        # 尝试解锁凯文
        if hunter_id == 'wote':
            if random.random() * 100 < cfg['unlock_rate']:
                hunting_state['kaiwen_unlocked'] = True
        
        session[state_key] = hunting_state

        soul_charm_consumed, copper_consumed = _get_personal_consumed(user_id)
        soul_charm_consumed += int(cost)

        global_consumed = _get_global_soul_charm_consumed('kevin_adv_pity')
        global_consumed += int(cost)

        force_dragon = False
        if soul_charm_consumed >= ADV_PERSONAL_DRAGON_PITY:
            soul_charm_consumed -= ADV_PERSONAL_DRAGON_PITY
            force_dragon = True

        if global_consumed >= ADV_GLOBAL_DRAGON_PITY:
            global_consumed -= ADV_GLOBAL_DRAGON_PITY
            force_dragon = True

        _save_personal_consumed(user_id, soul_charm_consumed, copper_consumed)
        _save_global_soul_charm_consumed(global_consumed, 'kevin_adv_pity')
        
        # 随机魔魂
        weights = ADVANCED_GRADE_WEIGHTS.get(hunter_id, {'earth_soul': 100})

        grades = list(weights.keys())
        probs = list(weights.values())
        chosen_grade = random.choices(grades, weights=probs, k=1)[0]

        if force_dragon:
            chosen_grade = 'dragon_soul'
    
    # 随机选择模板
    templates = GRADE_TEMPLATES.get(chosen_grade, [501])
    template_id = random.choice(templates)

    # 普通场兜底规则：最终模板不允许是龙魂；未触发保底时不允许是天魂
    if arena_type == 'normal':
        template = get_mosoul_template(int(template_id))
        if template and template.grade.value == 'dragon_soul':
            template_id = random.choice(GRADE_TEMPLATES.get('earth_soul', [301]))
        elif chosen_grade != 'heaven_soul' and template and template.grade.value == 'heaven_soul':
            template_id = random.choice(GRADE_TEMPLATES.get('earth_soul', [301]))
    
    # 废魂自动售卖
    if chosen_grade == 'waste_soul':
        sell_price = 5000
        player_repo.update_gold(user_id, sell_price)
        gold += sell_price
        return jsonify({
            'ok': True,
            'message': f'猎到废魂，已自动售卖获得{sell_price}铜钱',
            'mosoul': None,
            'is_waste': True,
            'sell_price': sell_price,
            'cost': cost,
            'remaining_gold': gold,
            'next_unlocked': next_unlocked if arena_type == 'normal' else hunting_state.get('kaiwen_unlocked', False),
            'next_hunter': next_hunter if arena_type == 'normal' else 'kaiwen',
        })
    
    # 创建魔魂
    mosoul_id = mosoul_repo.create_mosoul(user_id, template_id, level=1)
    
    # 获取魔魂详情
    mosoul_row = mosoul_repo.get_mosoul_by_id(mosoul_id)
    mosoul_detail = mosoul_to_detail(mosoul_row) if mosoul_row else None
    
    return jsonify({
        'ok': True,
        'message': f'猎魂成功！获得了{mosoul_detail["name"] if mosoul_detail else "魔魂"}',
        'mosoul': mosoul_detail,
        'is_waste': False,
        'cost': cost,
        'remaining_gold': gold,
        'next_unlocked': next_unlocked if arena_type == 'normal' else hunting_state.get('kaiwen_unlocked', False),
        'next_hunter': next_hunter if arena_type == 'normal' else 'kaiwen',
    })


@mosoul_bp.post('/hunting/batch-hunt')
def batch_hunting():
    """一键猎魂：自动执行10次猎魂
    
    规则：
    - 自动执行最多10次猎魂
    - 材料不足时自动停止
    - 解锁更高级猎魂师后自动切换到更高级的
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})
    
    data = request.get_json() or {}
    arena_type = data.get('arenaType', 'normal')
    max_hunts = 10
    
    from infrastructure.db import player_repo_mysql as player_repo
    from interfaces.web_api.bootstrap import services
    import random
    
    # 获取玩家铜钱
    player = player_repo.get_player_by_id(user_id)
    gold = player.get('gold', 0) if player else 0

    soul_charm = services.inventory_service.get_item_count(user_id, SOUL_CHARM_ITEM_ID, include_temp=True)

    warehouse_capacity = get_soul_container_capacity(0)
    warehouse_count = len(mosoul_repo.get_unequipped_mosouls(user_id))
    if warehouse_count >= warehouse_capacity:
        return jsonify({
            'ok': True,
            'message': f'一键猎魂完成，共猎魂0次',
            'results': [{
                'hunt_num': 1,
                'stopped': True,
                'reason': f'储魂器已满（{warehouse_count}/{warehouse_capacity}）',
            }],
            'summary': {
                'total_hunts': 0,
                'total_cost': 0,
                'total_sell': 0,
                'net_cost': 0,
                'obtained_count': 0,
                'grade_summary': {},
                'cost_type': 'copper' if arena_type == 'normal' else 'soul_charm',
            },
            'remaining_gold': gold,
            'remaining_soul_charm': soul_charm,
        })
    
    # 获取当前猎魂状态
    state_key = f'hunting_state_{arena_type}'
    hunting_state = session.get(state_key, {})
    
    # 定义猎魂师优先级（从高到低）
    if arena_type == 'normal':
        hunter_priority = ['kaiwen', 'wote', 'boer', 'keke', 'amy']
        config = HUNTER_CONFIG
        grade_weights = NORMAL_GRADE_WEIGHTS
    else:
        hunter_priority = ['kaiwen', 'wote']
        config = ADVANCED_HUNTER_CONFIG
        grade_weights = ADVANCED_GRADE_WEIGHTS
    
    results = []
    total_cost = 0
    total_sell = 0
    obtained_mosouls = []
    
    for hunt_num in range(max_hunts):
        force_heaven = False
        force_dragon = False

        if warehouse_count >= warehouse_capacity:
            results.append({
                'hunt_num': hunt_num + 1,
                'stopped': True,
                'reason': f'储魂器已满（{warehouse_count}/{warehouse_capacity}）',
            })
            break

        # 选择当前可用的最高级猎魂师
        current_hunter = None
        for hid in hunter_priority:
            if arena_type == 'normal':
                if hid == 'amy' or hunting_state.get(f'{hid}_unlocked', False):
                    current_hunter = hid
                    break
            else:
                if hid == 'wote' or hunting_state.get('kaiwen_unlocked', False):
                    current_hunter = hid
                    break
        
        if not current_hunter:
            current_hunter = 'amy' if arena_type == 'normal' else 'wote'
        
        cfg = config[current_hunter]
        
        # 计算费用
        if arena_type == 'normal':
            cost = int(cfg['cost'])
            if gold < cost:
                results.append({
                    'hunt_num': hunt_num + 1,
                    'stopped': True,
                    'reason': '铜钱不足',
                })
                break

            player_repo.update_gold(user_id, -cost)
            gold -= cost
            total_cost += cost

            global_copper_consumed = _get_global_copper_consumed(NORMAL_HEAVEN_PITY_COUNTER_KEY)
            global_copper_consumed += int(cost)
            force_heaven = False
            if global_copper_consumed >= NORMAL_HEAVEN_PITY_COPPER and current_hunter in ('wote', 'kaiwen'):
                global_copper_consumed = 0
                force_heaven = True
            _save_global_copper_consumed(global_copper_consumed, NORMAL_HEAVEN_PITY_COUNTER_KEY)
        else:
            cost = int(cfg['cost'])
            if soul_charm < cost:
                results.append({
                    'hunt_num': hunt_num + 1,
                    'stopped': True,
                    'reason': '追魂法宝不足',
                })
                break

            services.inventory_service.remove_item(user_id, SOUL_CHARM_ITEM_ID, cost)
            soul_charm -= cost
            total_cost += cost

            soul_charm_consumed, copper_consumed = _get_personal_consumed(user_id)
            soul_charm_consumed += int(cost)

            global_consumed = _get_global_soul_charm_consumed('kevin_adv_pity')
            global_consumed += int(cost)

            force_dragon = False
            if soul_charm_consumed >= ADV_PERSONAL_DRAGON_PITY:
                soul_charm_consumed -= ADV_PERSONAL_DRAGON_PITY
                force_dragon = True

            if global_consumed >= ADV_GLOBAL_DRAGON_PITY:
                global_consumed -= ADV_GLOBAL_DRAGON_PITY
                force_dragon = True

            _save_personal_consumed(user_id, soul_charm_consumed, copper_consumed)
            _save_global_soul_charm_consumed(global_consumed, 'kevin_adv_pity')
        
        # 点击后清除当前猎魂师的解锁状态（除了艾米/沃特）
        if arena_type == 'normal' and current_hunter != 'amy':
            hunting_state[f'{current_hunter}_unlocked'] = False
        elif arena_type != 'normal' and current_hunter == 'kaiwen':
            hunting_state['kaiwen_unlocked'] = False
        
        # 尝试解锁下一个猎魂师
        next_hunter = cfg.get('next')
        next_unlocked = False
        if next_hunter and cfg.get('unlock_rate', 0) > 0:
            if random.random() * 100 < cfg['unlock_rate']:
                if arena_type == 'normal':
                    hunting_state[f'{next_hunter}_unlocked'] = True
                else:
                    hunting_state['kaiwen_unlocked'] = True
                next_unlocked = True
        
        # 随机魔魂
        weights = grade_weights.get(current_hunter, {'yellow_soul': 100})

        grades = list(weights.keys())
        probs = list(weights.values())
        chosen_grade = random.choices(grades, weights=probs, k=1)[0]

        if arena_type == 'normal' and force_heaven:
            chosen_grade = 'heaven_soul'

        if arena_type == 'normal' and chosen_grade == 'dragon_soul':
            chosen_grade = 'earth_soul'

        if arena_type != 'normal' and force_dragon:
            chosen_grade = 'dragon_soul'
        
        # 随机选择模板
        templates = GRADE_TEMPLATES.get(chosen_grade, [501])
        template_id = random.choice(templates)

        # 普通场兜底规则：最终模板不允许是龙魂；未触发保底时不允许是天魂
        if arena_type == 'normal':
            template = get_mosoul_template(int(template_id))
            if template and template.grade.value == 'dragon_soul':
                template_id = random.choice(GRADE_TEMPLATES.get('earth_soul', [301]))
            elif chosen_grade != 'heaven_soul' and template and template.grade.value == 'heaven_soul':
                template_id = random.choice(GRADE_TEMPLATES.get('earth_soul', [301]))
        
        hunt_result = {
            'hunt_num': hunt_num + 1,
            'hunter': cfg['name'],
            'hunter_id': current_hunter,
            'cost': cost,
            'next_unlocked': next_unlocked,
            'next_hunter': next_hunter,
        }
        
        # 废魂自动售卖
        if chosen_grade == 'waste_soul':
            sell_price = 5000
            player_repo.update_gold(user_id, sell_price)
            gold += sell_price
            total_sell += sell_price
            hunt_result['is_waste'] = True
            hunt_result['sell_price'] = sell_price
            hunt_result['mosoul'] = None
        else:
            # 创建魔魂
            mosoul_id = mosoul_repo.create_mosoul(user_id, template_id, level=1)
            mosoul_row = mosoul_repo.get_mosoul_by_id(mosoul_id)
            mosoul_detail = mosoul_to_detail(mosoul_row) if mosoul_row else None

            warehouse_count += 1
            
            hunt_result['is_waste'] = False
            hunt_result['mosoul'] = mosoul_detail
            if mosoul_detail:
                obtained_mosouls.append(mosoul_detail)
        
        results.append(hunt_result)
    
    # 保存状态
    session[state_key] = hunting_state
    
    # 统计获得的魔魂按品质分组
    grade_summary = {}
    for m in obtained_mosouls:
        grade = m['grade_name']
        if grade not in grade_summary:
            grade_summary[grade] = 0
        grade_summary[grade] += 1
    
    return jsonify({
        'ok': True,
        'message': f'一键猎魂完成，共猎魂{len(results)}次',
        'results': results,
        'summary': {
            'total_hunts': len(results),
            'total_cost': total_cost,
            'total_sell': total_sell,
            'net_cost': (total_cost - total_sell) if arena_type == 'normal' else total_cost,
            'obtained_count': len(obtained_mosouls),
            'grade_summary': grade_summary,
            'cost_type': 'copper' if arena_type == 'normal' else 'soul_charm',
        },
        'remaining_gold': gold,
        'remaining_soul_charm': soul_charm,
    })


@mosoul_bp.post('/grant')
def grant_mosoul():
    """测试用：发放魔魂"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({'ok': False, 'error': '请先登录'})
    
    data = request.get_json() or {}
    template_id = data.get('templateId', 206)  # 默认天魔降伏
    level = data.get('level', 1)
    beast_id = data.get('beastId')  # 可选：直接装备到幻兽

    if not beast_id:
        warehouse_capacity = get_soul_container_capacity(0)
        warehouse_count = len(mosoul_repo.get_unequipped_mosouls(user_id))
        if warehouse_count >= warehouse_capacity:
            return jsonify({'ok': False, 'error': f'储魂器已满（{warehouse_count}/{warehouse_capacity}），无法发放'} )
    
    # 创建魔魂
    mosoul_id = mosoul_repo.create_mosoul(user_id, template_id, level)
    
    # 如果指定了幻兽，直接装备
    if beast_id:
        mosoul_repo.equip_mosoul(mosoul_id, beast_id)
    
    return jsonify({
        'ok': True,
        'message': '发放成功',
        'mosoulId': mosoul_id,
    })
