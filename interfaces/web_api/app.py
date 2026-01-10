# interfaces/web_api/app.py
"""
Flask 应用主入口
只负责：1. 初始化Flask  2. 注册路由蓝图
业务逻辑在 application/services 中
路由定义在 interfaces/routes 中
"""

import sys
from pathlib import Path

# 将项目根目录添加到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, request, jsonify, session

# 创建Flask应用
app = Flask(__name__)
app.secret_key = 'game_tower_secret_key_2024'

# ===== 注册路由蓝图 =====
from interfaces.routes.auth_routes import auth_bp
from interfaces.routes.player_routes import player_bp
from interfaces.routes.tower_routes import tower_bp
from interfaces.routes.arena_routes import arena_bp
from interfaces.routes.king_routes import king_bp
from interfaces.routes.ranking_routes import ranking_bp
from interfaces.routes.map_routes import map_bp
from interfaces.routes.shop_routes import shop_bp
from interfaces.routes.inventory_routes import inventory_bp
from interfaces.routes.battlefield_routes import battlefield_bp
from interfaces.routes.bone_routes import bone_bp
from interfaces.routes.spirit_routes import spirit_bp
from interfaces.routes.beast_routes import beast_bp
from interfaces.routes.mosoul_routes import mosoul_bp
from interfaces.routes.dev_routes import dev_bp
from interfaces.routes.dungeon_routes import dungeon_bp
from interfaces.routes.alliance_routes import alliance_bp
from interfaces.routes.task_routes import task_bp
from interfaces.routes.manor_routes import manor_bp
from interfaces.routes.refine_pot_routes import refine_pot_bp
from interfaces.routes.month_card_routes import month_card_bp
from interfaces.routes.exchange_routes import exchange_bp
from interfaces.routes.immortalize_routes import immortalize_bp
from interfaces.routes.cultivation_routes import cultivation_bp
from interfaces.routes.home_gift_routes import gifts_bp
from interfaces.routes.pay_routes import pay_bp
from interfaces.routes.vip_routes import vip_bp
from interfaces.routes.vip_test_routes import vip_test_bp
from interfaces.routes.arena_streak_routes import arena_streak_bp

app.register_blueprint(auth_bp)
app.register_blueprint(player_bp)
app.register_blueprint(tower_bp)
app.register_blueprint(arena_bp)
app.register_blueprint(king_bp)
app.register_blueprint(ranking_bp)
app.register_blueprint(map_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(battlefield_bp)
app.register_blueprint(bone_bp)
app.register_blueprint(spirit_bp)
app.register_blueprint(beast_bp)
app.register_blueprint(mosoul_bp)
app.register_blueprint(dev_bp)
app.register_blueprint(dungeon_bp)
app.register_blueprint(alliance_bp)
app.register_blueprint(task_bp)
app.register_blueprint(manor_bp)
app.register_blueprint(refine_pot_bp)
app.register_blueprint(month_card_bp)
app.register_blueprint(exchange_bp)
app.register_blueprint(immortalize_bp)
app.register_blueprint(cultivation_bp)
app.register_blueprint(gifts_bp)
app.register_blueprint(pay_bp)
app.register_blueprint(vip_bp)
app.register_blueprint(vip_test_bp)
app.register_blueprint(arena_streak_bp)


# ===== 以下为旧接口，暂时保留兼容 =====
from interfaces.web_api.bootstrap import services
from domain.entities.player import Player
from domain.rules.battle_power_rules import calc_player_battle_power
from application.services.signin_service import SigninError
from application.services.inventory_service import InventoryError
from application.services.beast_service import BeastError
from application.services.bone_service import BoneError
from application.services.capture_service import CaptureError


def get_current_user_id() -> int:
    return session.get('user_id', 0)


def player_to_dict(player: Player) -> dict:
    battle_power = calc_player_battle_power(player)
    rank_name = player.get_rank_name()
    summoner_title = player.get_summoner_title()
    star, pin = player.get_summoner_star_and_pin()
    
    # 获取VIP等级对应的活力上限
    from interfaces.routes.player_routes import _get_vip_energy_max
    max_energy = _get_vip_energy_max(player.vip_level)

    return {
        "id": player.id,
        "username": player.username,
        "nickname": player.nickname,
        "level": player.level,
        "vip_level": player.vip_level,
        "max_energy": max_energy,
        # 等级称号：x星x品召唤师（用于前端展示）
        "level_text": summoner_title,
        "summoner_title": summoner_title,
        "level_star": star,
        "level_pin": pin,
        # 阶位（黄阶/玄阶...）仍保留，便于后续系统使用
        "rank_name": rank_name,
        "exp": player.exp,
        "next_exp": player.exp_to_next_level(),
        "gold": player.gold,
        "energy": player.energy,
        "prestige": player.prestige,
        "spirit_stone": player.spirit_stone,
        "battle_power": battle_power,
        "power": battle_power,
        "last_signin_date": (
            player.last_signin_date.isoformat() if player.last_signin_date else None
        ),
    }


@app.post("/api/battle")
def battle():
    data = request.get_json() or {}
    player_id = int(data.get("user_id", 1))
    monster_id = int(data.get("monster_id", 1))

    outcome = services.battle_service.start_battle(player_id=player_id, monster_id=monster_id)

    return jsonify({
        "win": outcome.record.is_victory(),
        "exp_gain": outcome.player.exp,
        "gold_gain": outcome.player.gold,
        "map_id": outcome.map_id,
        "drops": [
            {"item_id": d.item_id, "name": d.item_name, "quantity": d.quantity}
            for d in outcome.drops
        ],
        "user": {
            "id": outcome.player.id,
            "level": outcome.player.level,
            "exp": outcome.player.exp,
            "gold": outcome.player.gold,
            "energy": outcome.player.energy,
        }
    })


@app.get("/api/user/me")
def get_me():
    player = services.player_repo_inmemory.get_by_id(1)
    if player is None:
        return jsonify({"error": "player_not_found"}), 404
    return jsonify(player_to_dict(player))


@app.post("/api/signin")
def signin():
    """每日签到"""
    from interfaces.routes.auth_routes import get_current_user_id
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        result = services.signin_service.do_signin(player_id=user_id)
        
        # 构建消息
        message = f"签到成功！获得铜钱：{result['gold_reward']}"
        if result['is_doubled']:
            message += f"（连续签到{result['consecutive_days']}天，奖励翻倍）"
        else:
            message += f"（连续签到{result['consecutive_days']}天）"
        message += f"\n颁发者：{result['sponsor']}"
        
        return jsonify({
            "ok": True,
            "message": message,
            "gold_reward": result['gold_reward'],
            "base_gold": result['base_gold'],
            "consecutive_days": result['consecutive_days'],
            "is_doubled": result['is_doubled'],
            "sponsor": result['sponsor'],
            "user": player_to_dict(result['player'])
        })
    except SigninError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.get("/api/signin/info")
def get_signin_info():
    """获取签到信息"""
    from interfaces.routes.auth_routes import get_current_user_id
    from datetime import date
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        player = services.player_repo.get_by_id(user_id)
        if not player:
            return jsonify({"ok": False, "error": "玩家不存在"}), 404
        
        today = date.today()
        has_signed = player.last_signin_date == today
        
        # 获取本月签到天数（简化：使用连续签到天数）
        signin_days = []
        if player.last_signin_date:
            # 简化：只显示今天是否签到
            if has_signed:
                signin_days.append(today.day)
        
        return jsonify({
            "ok": True,
            "hasSigned": has_signed,
            "consecutiveDays": player.consecutive_signin_days or 0,
            "currentMonth": f"{today.month}",
            "currentYear": today.year,
            "signinDays": signin_days
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/api/signin/reward/<int:days>")
def get_signin_reward_info(days):
    """获取签到累计奖励信息"""
    from interfaces.routes.auth_routes import get_current_user_id
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    if days not in [7, 15, 30]:
        return jsonify({"ok": False, "error": "无效的天数"}), 400
    
    try:
        player = services.player_repo.get_by_id(user_id)
        if not player:
            return jsonify({"ok": False, "error": "玩家不存在"}), 404
        
        # 检查是否已领取
        claimed_rewards = getattr(player, 'signin_rewards_claimed', []) or []
        claimed = days in claimed_rewards
        
        return jsonify({
            "ok": True,
            "consecutiveDays": player.consecutive_signin_days,
            "claimed": claimed,
            "canClaim": player.consecutive_signin_days >= days and not claimed
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.post("/api/signin/reward/<int:days>/claim")
def claim_signin_reward(days):
    """领取签到累计奖励"""
    from interfaces.routes.auth_routes import get_current_user_id
    from infrastructure.db.connection import execute_update, execute_query
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    if days not in [7, 15, 30]:
        return jsonify({"ok": False, "error": "无效的天数"}), 400
    
    try:
        player = services.player_repo.get_by_id(user_id)
        if not player:
            return jsonify({"ok": False, "error": "玩家不存在"}), 404
        
        # 检查累计天数
        if player.consecutive_signin_days < days:
            return jsonify({"ok": False, "error": f"需要累计签到{days}天"}), 400
        
        # 检查是否已领取
        rows = execute_query(
            "SELECT signin_rewards_claimed FROM player WHERE user_id = %s",
            (user_id,)
        )
        
        if rows:
            claimed_str = rows[0].get('signin_rewards_claimed', '') or ''
            claimed_list = [int(x) for x in claimed_str.split(',') if x.strip().isdigit()]
            
            if days in claimed_list:
                return jsonify({"ok": False, "error": "已领取过该奖励"}), 400
            
            claimed_list.append(days)
            new_claimed_str = ','.join(map(str, claimed_list))
        else:
            new_claimed_str = str(days)
        
        # 定义奖励配置（使用实际的物品ID）
        item_name_to_id = {
            "化仙丹": 6015,
            "随机结晶": 5001,  # 需要确认
            "战灵-土灵": 7001,  # 需要确认
            "骰子包": 6010,
            "捕捉球": 4002,
            "迷踪符": 6018,  # 使用传送符代替
            "招财神符": 6007,  # 需要确认
            "灵力水晶": 5002,  # 需要确认
            "炼魂丹": 6028,
            "强力捕捉球": 6011,
            "镇妖符": 6001,
            "神·逆鳞碎片": 5003,  # 需要确认
            "追魂法宝": 7002,  # 需要确认
            "重生丹": 6017,
            "火灵灵石": 5004,  # 需要确认
            "补签卡": 6019  # 需要确认
        }
        
        rewards_config = {
            7: {
                "copper": 0,
                "items": [
                    ("化仙丹", 1),
                    ("随机结晶", 1),
                    ("战灵-土灵", 1),
                    ("骰子包", 2),
                    ("捕捉球", 3),
                    ("迷踪符", 3)
                ]
            },
            15: {
                "copper": 0,
                "items": [
                    ("招财神符", 1),
                    ("灵力水晶", 1),
                    ("战灵-土灵", 2),
                    ("炼魂丹", 1),
                    ("强力捕捉球", 1),
                    ("镇妖符", 3)
                ]
            },
            30: {
                "copper": 800000,
                "items": [
                    ("神·逆鳞碎片", 15),
                    ("追魂法宝", 2),
                    ("重生丹", 1),
                    ("火灵灵石", 1),
                    ("灵力水晶", 1),
                    ("炼魂丹", 3),
                    ("骰子包", 2),
                    ("强力捕捉球", 2),
                    ("捕捉球", 6),
                    ("补签卡", 1)
                ]
            }
        }
        
        reward = rewards_config[days]
        
        # 更新铜钱和已领取记录
        if reward['copper'] > 0:
            execute_update(
                "UPDATE player SET copper = copper + %s, signin_rewards_claimed = %s WHERE user_id = %s",
                (reward['copper'], new_claimed_str, user_id)
            )
        else:
            execute_update(
                "UPDATE player SET signin_rewards_claimed = %s WHERE user_id = %s",
                (new_claimed_str, user_id)
            )
        
        # 发放物品到背包
        items_text = []
        for item_name, quantity in reward['items']:
            item_id = item_name_to_id.get(item_name)
            if item_id:
                try:
                    services.inventory_service.add_item(user_id, item_id, quantity)
                    items_text.append(f"{item_name}×{quantity}")
                except Exception as e:
                    print(f"发放物品失败 {item_name}: {e}")
                    items_text.append(f"{item_name}×{quantity}")
            else:
                items_text.append(f"{item_name}×{quantity}")
        
        message_parts = []
        if reward['copper'] > 0:
            message_parts.append(f"铜钱×{reward['copper']}")
        message_parts.extend(items_text)
        
        return jsonify({
            "ok": True,
            "message": f"领取成功！获得：{', '.join(message_parts)}"
        })
    except Exception as e:
        import traceback
        print(f"领取奖励失败: {e}")
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/api/signin/makeup/info")
def get_makeup_info():
    """获取补签信息"""
    from interfaces.routes.auth_routes import get_current_user_id
    from datetime import date
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        today = date.today()
        
        # 简化：返回基本信息
        return jsonify({
            "ok": True,
            "availableMakeups": 0,
            "maxMakeups": 3,
            "currentCards": 0,
            "missedDays": [],  # 未签到的日期
            "currentMonth": f"{today.month}",
            "currentYear": today.year
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.get("/api/maps")
def list_maps():
    player = services.player_repo_inmemory.get_by_id(1)
    if player is None:
        return jsonify({"error": "player_not_found"}), 404

    available_maps = services.map_service.list_maps_for_player(player)
    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "min_level": m.min_level,
            "max_level": m.max_level,
        }
        for m in available_maps
    ])


@app.get("/api/maps/<int:map_id>/monsters")
def list_monsters(map_id: int):
    monsters = services.map_service.list_monsters_in_map(map_id)
    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "level": m.level,
            "base_exp": m.base_exp,
            "base_gold": m.base_gold,
        }
        for m in monsters
    ])


# ===== 背包接口 =====
@app.get("/api/inventory")
def get_inventory():
    items = services.inventory_service.get_inventory(user_id=1)
    return jsonify([
        {
            "id": item.inv_item.id,
            "item_id": item.item_info.id,
            "name": item.item_info.name,
            "type": item.item_info.type,
            "quantity": item.inv_item.quantity,
            "description": item.item_info.description,
            "is_temporary": item.inv_item.is_temporary,
        }
        for item in items
    ])


@app.get("/api/inventory/bag-info")
def get_bag_info():
    info = services.inventory_service.get_bag_info(user_id=1)
    return jsonify(info)


@app.post("/api/inventory/add")
def add_inventory_item():
    data = request.get_json() or {}
    item_id = int(data.get("item_id", 0))
    quantity = int(data.get("quantity", 1))

    if item_id == 0:
        return jsonify({"ok": False, "error": "item_id required"}), 400

    try:
        inv_item, is_temp = services.inventory_service.add_item(user_id=1, item_id=item_id, quantity=quantity)
        return jsonify({
            "ok": True,
            "item": {
                "id": inv_item.id,
                "item_id": inv_item.item_id,
                "quantity": inv_item.quantity,
                "is_temporary": is_temp,
            }
        })
    except InventoryError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ===== 幻兽接口 =====
@app.get("/api/beasts")
def get_beasts():
    beasts = services.beast_service.get_beasts(user_id=1)
    return jsonify([b.to_dict() for b in beasts])


@app.post("/api/beasts/add")
def add_beast():
    data = request.get_json() or {}
    template_id = int(data.get("template_id", 0))
    nickname = data.get("nickname", "")

    if template_id == 0:
        return jsonify({"ok": False, "error": "template_id required"}), 400

    try:
        beast = services.beast_service.add_beast(user_id=1, template_id=template_id, nickname=nickname)
        template = services.beast_template_repo.get_by_id(beast.template_id)
        from application.services.beast_service import BeastWithInfo
        info = BeastWithInfo(beast=beast, template=template)
        return jsonify({"ok": True, "beast": info.to_dict()})
    except BeastError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.post("/api/beasts/<int:beast_id>/set-main")
def set_main_beast(beast_id: int):
    try:
        beast = services.beast_service.set_main_beast(user_id=1, beast_id=beast_id)
        template = services.beast_template_repo.get_by_id(beast.template_id)
        from application.services.beast_service import BeastWithInfo
        info = BeastWithInfo(beast=beast, template=template)
        return jsonify({"ok": True, "beast": info.to_dict()})
    except BeastError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.post("/api/beasts/<int:beast_id>/add-exp")
def add_exp_to_beast(beast_id: int):
    data = request.get_json() or {}
    try:
        exp = int(data.get("exp", 0))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "exp 必须是整数"}), 400

    try:
        from application.services.beast_service import BeastWithInfo
        info = services.beast_service.add_exp_to_beast(user_id=1, beast_id=beast_id, exp=exp)
        return jsonify({"ok": True, "beast": info.to_dict()})
    except BeastError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.get("/api/beast-templates")
def get_beast_templates():
    templates = services.beast_template_repo.get_all()
    return jsonify([
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "base_hp": t.base_hp,
            "base_attack": t.base_attack,
            "base_defense": t.base_defense,
            "base_speed": t.base_speed,
        }
        for t in templates.values()
    ])


# ===== 战骨接口（临时版本，用于测试穿戴/卸下） =====
@app.get("/api/bones")
def get_bones():
    bones = services.bone_service.get_bones(user_id=1)
    return jsonify([b.to_dict() for b in bones])


@app.post("/api/bones/add")
def add_bone():
    data = request.get_json() or {}
    template_id = int(data.get("template_id", 0))
    stage = int(data.get("stage", 1))
    level = int(data.get("level", 1))

    if template_id == 0:
        return jsonify({"ok": False, "error": "template_id required"}), 400

    try:
        info = services.bone_service.create_bone(user_id=1, template_id=template_id, stage=stage, level=level)
        return jsonify({"ok": True, "bone": info.to_dict()})
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.post("/api/beasts/<int:beast_id>/equip-bone")
def equip_bone(beast_id: int):
    data = request.get_json() or {}
    bone_id = int(data.get("bone_id", 0))

    if bone_id == 0:
        return jsonify({"ok": False, "error": "bone_id required"}), 400

    try:
        info = services.bone_service.equip_bone(user_id=1, beast_id=beast_id, bone_id=bone_id)
        return jsonify({"ok": True, "bone": info.to_dict()})
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.post("/api/bones/<int:bone_id>/unequip")
def unequip_bone(bone_id: int):
    try:
        info = services.bone_service.unequip_bone(user_id=1, bone_id=bone_id)
        return jsonify({"ok": True, "bone": info.to_dict()})
    except BoneError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ===== 捕捉接口 =====
@app.post("/api/capture")
def capture():
    data = request.get_json() or {}
    map_id = int(data.get("map_id", 0))
    use_strong_ball = bool(data.get("use_strong_ball", False))

    if map_id == 0:
        return jsonify({"ok": False, "error": "map_id required"}), 400

    try:
        result = services.capture_service.attempt_capture(
            user_id=1,
            map_id=map_id,
            use_strong_ball=use_strong_ball,
        )

        response = {
            "ok": result.success,
            "message": result.message,
        }

        if result.success and result.beast:
            template = services.beast_template_repo.get_by_id(result.beast.template_id)
            from application.services.beast_service import BeastWithInfo
            info = BeastWithInfo(beast=result.beast, template=template)
            response["beast"] = info.to_dict()

        return jsonify(response)
    except CaptureError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ===== 传送符兼容路由 =====
@app.get("/api/player/teleport-count")
def get_teleport_count():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    from infrastructure.db.connection import execute_query
    rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
        (user_id, 6018),
    )
    count = rows[0].get('quantity', 0) if rows else 0
    return jsonify({"ok": True, "count": count})


# ===== 启动后台调度器（每日 00:05 自动开赛） =====
import os
# 仅在主进程启动调度器，避免多 worker 重复触发
if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
    from infrastructure.scheduler import start_scheduler
    start_scheduler()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
