# interfaces/web_api/app.py
from flask import Flask, request, jsonify, session
from domain.rules.battle_power_rules import calc_player_battle_power

from domain.entities.player import Player
from infrastructure.memory.player_repo_inmemory import InMemoryPlayerRepo
from infrastructure.config.monster_repo_from_config import ConfigMonsterRepo
from application.services.battle_service import BattleService
from application.services.signin_service import SigninService, SigninError

from infrastructure.config.map_repo_from_config import ConfigMapRepo
from application.services.map_service import MapService

from infrastructure.config.item_repo_from_config import ConfigItemRepo
from infrastructure.db.inventory_repo_mysql import MySQLInventoryRepo
from application.services.inventory_service import InventoryService, InventoryError

from infrastructure.config.beast_template_repo_from_config import ConfigBeastTemplateRepo
from infrastructure.memory.beast_repo_inmemory import InMemoryBeastRepo
from application.services.beast_service import BeastService, BeastError

from application.services.drop_service import DropService
from application.services.capture_service import CaptureService, CaptureError

from infrastructure.db.tower_state_repo_mysql import MySQLTowerStateRepo
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.config.tower_config_repo import ConfigTowerRepo
from application.services.tower_service import TowerBattleService, TowerError, PlayerBeast

from infrastructure.db.player_repo_mysql import MySQLPlayerRepo, MySQLZhenyaoRepo
from application.services.zhenyao_service import ZhenyaoService, ZhenyaoError
from application.services.auth_service import AuthService, AuthError

app = Flask(__name__)
app.secret_key = 'game_tower_secret_key_2024'  # Session密钥


@app.before_request
def _app_old_down():
    return jsonify({
        "ok": False,
        "error": "app_old 已下线，请使用 interfaces.web_api.app (app.py) 提供的 /api 接口",
    }), 410


def get_current_user_id() -> int:
    """获取当前登录用户ID，未登录返回0"""
    return session.get('user_id', 0)

# ===== 用户仍然暂时用内存仓库 =====
player_repo_inmemory = InMemoryPlayerRepo({1: Player(id=1, username="hero", level=5, exp=0, gold=0, energy=100)})

# ===== 地图 & 怪物从配置读取 =====
map_repo = ConfigMapRepo()
monster_repo = ConfigMonsterRepo()

# ===== 背包系统（使用MySQL） =====
item_repo = ConfigItemRepo()
inventory_repo = MySQLInventoryRepo()
inventory_service = InventoryService(item_repo=item_repo, inventory_repo=inventory_repo)

# ===== 幻兽系统 =====
beast_template_repo = ConfigBeastTemplateRepo()
beast_repo = InMemoryBeastRepo()
beast_service = BeastService(template_repo=beast_template_repo, beast_repo=beast_repo)

# ===== 掉落 & 捕捉系统 =====
drop_service = DropService(item_repo=item_repo, inventory_service=inventory_service)
capture_service = CaptureService(inventory_service=inventory_service, beast_service=beast_service)

# ===== 战斗系统（依赖掉落服务） =====
battle_service = BattleService(player_repo=player_repo_inmemory, monster_repo=monster_repo, drop_service=drop_service)
signin_service = SigninService(player_repo=player_repo_inmemory)
map_service = MapService(map_repo=map_repo, monster_repo=monster_repo)

# ===== 闯塔系统（使用MySQL） =====
tower_state_repo = MySQLTowerStateRepo()
tower_config_repo = ConfigTowerRepo()
player_beast_repo = MySQLPlayerBeastRepo()
tower_service = TowerBattleService(
    state_repo=tower_state_repo,
    config_repo=tower_config_repo,
    inventory_service=inventory_service,
)

# ===== 镇妖系统 =====
player_repo = MySQLPlayerRepo()
zhenyao_repo = MySQLZhenyaoRepo()
zhenyao_service = ZhenyaoService(
    player_repo=player_repo,
    zhenyao_repo=zhenyao_repo,
    tower_state_repo=tower_state_repo,
)

# ===== 登录注册系统 =====
auth_service = AuthService(player_repo=player_repo)


# ===== 登录注册接口 =====
@app.post("/api/auth/login")
def login():
    """登录"""
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    
    result = auth_service.login(username, password)
    
    if result.success:
        session['user_id'] = result.user_id
        session['nickname'] = result.nickname
        return jsonify({
            "ok": True,
            "user_id": result.user_id,
            "nickname": result.nickname,
            "level": result.level,
            "rank_name": result.rank_name,
        })
    else:
        return jsonify({"ok": False, "error": result.error})


@app.post("/api/auth/register")
def register():
    """注册"""
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    nickname = data.get("nickname", "")
    
    result = auth_service.register(username, password, nickname)
    
    if result.success:
        session['user_id'] = result.user_id
        session['nickname'] = result.nickname
        return jsonify({
            "ok": True,
            "user_id": result.user_id,
            "nickname": result.nickname,
            "level": result.level,
            "rank_name": result.rank_name,
        })
    else:
        return jsonify({"ok": False, "error": result.error})


@app.post("/api/auth/logout")
def logout():
    """登出"""
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/auth/status")
def auth_status():
    """获取登录状态"""
    user_id = get_current_user_id()
    if user_id:
        player = player_repo.get_by_id(user_id)
        if player:
            # 计算战力（简化：基于等级和幻兽）
            beasts = player_beast_repo.get_team_beasts(user_id)
            battle_power = sum(b.combat_power for b in beasts) if beasts else 0
            
            return jsonify({
                "ok": True,
                "logged_in": True,
                "user_id": user_id,
                "nickname": player.nickname,
                "level": player.level,
                "rank_name": player.get_rank_name(),
                "gold": player.gold,
                "exp": player.exp,
                "battle_power": battle_power,
                "prestige": 0,      # 预留
                "energy": 100,      # 预留
                "spirit_stone": 5,  # 预留
                "yuanbao": 0,       # 预留
            })
    return jsonify({"ok": True, "logged_in": False})


# ===== 工具函数：把 Player 转成 dict =====
def player_to_dict(player: Player) -> dict:
    return {
        "id": player.id,
        "username": player.username,
        "level": player.level,
        "exp": player.exp,
        "gold": player.gold,
        "energy": player.energy,
        "prestige": player.prestige,           
        "spirit_stone": player.spirit_stone,
        "battle_power": calc_player_battle_power(player), 
        "last_signin_date": (
            player.last_signin_date.isoformat() if player.last_signin_date else None
        ),
    }
@app.post("/api/battle")
def battle():
    data = request.get_json() or {}
    player_id = int(data.get("user_id", 1))
    monster_id = int(data.get("monster_id", 1))

    outcome = battle_service.start_battle(player_id=player_id, monster_id=monster_id)

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

# ===== 新接口 1：查看个人信息 =====
@app.get("/api/user/me")
def get_me():
    # 先写死 player_id = 1，之后接入登录再改
    player = player_repo_inmemory.get_by_id(1)
    if player is None:
        return jsonify({"error": "player_not_found"}), 404
    return jsonify(player_to_dict(player))


# ===== 新接口 2：每日签到 =====
@app.post("/api/signin")
def signin():
    try:
        player = signin_service.do_signin(player_id=1)
        return jsonify({
            "ok": True,
            "user": player_to_dict(player)
        })
    except SigninError as e:
        # 重复签到等情况
        return jsonify({
            "ok": False,
            "error": str(e),
        }), 400


@app.post("/api/cultivate")
def cultivate():
    data = request.get_json() or {}
    hours = int(data.get("hours", 2))  # 允许 2 / 4 / 8

    try:
        outcome = cultivation_service.do_cultivate(player_id=1, hours=hours)
        r = outcome.result
        return jsonify({
            "ok": True,
            "reward": {
                "hours": r.hours,
                "exp": r.exp_gain,
                "prestige": r.prestige_gain,
                "spirit_stone": r.spirit_stone_gain,
                "energy_cost": r.energy_cost,
            },
            "user": player_to_dict(outcome.player),
        })
    except CultivationError as e:
        return jsonify({
            "ok": False,
            "error": str(e),
        }), 400


# ===== 新接口：地图列表（按玩家等级过滤） =====
@app.get("/api/maps")
def list_maps():
    player = player_repo_inmemory.get_by_id(1)
    if player is None:
        return jsonify({"error": "player_not_found"}), 404

    available_maps = map_service.list_maps_for_player(player)
    # 也可以顺便返回全部地图 + 是否解锁标记，这里先简单版
    return jsonify([
        {
            "id": m.id,
            "name": m.name,
            "min_level": m.min_level,
            "max_level": m.max_level,
        }
        for m in available_maps
    ])


# ===== 新接口：某地图里的怪物列表 =====
@app.get("/api/maps/<int:map_id>/monsters")
def list_monsters(map_id: int):
    monsters = map_service.list_monsters_in_map(map_id)
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
    """获取玩家背包"""
    items = inventory_service.get_inventory(user_id=1)
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
    """获取背包信息（等级、容量等）"""
    info = inventory_service.get_bag_info(user_id=1)
    return jsonify(info)


@app.post("/api/inventory/add")
def add_inventory_item():
    """添加物品到背包（测试用）"""
    data = request.get_json() or {}
    item_id = int(data.get("item_id", 0))
    quantity = int(data.get("quantity", 1))

    if item_id == 0:
        return jsonify({"ok": False, "error": "item_id required"}), 400

    try:
        inv_item, is_temp = inventory_service.add_item(user_id=1, item_id=item_id, quantity=quantity)
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
    """获取玩家所有幻兽"""
    beasts = beast_service.get_beasts(user_id=1)
    return jsonify([b.to_dict() for b in beasts])


@app.post("/api/beasts/add")
def add_beast():
    """添加幻兽（测试用）"""
    data = request.get_json() or {}
    template_id = int(data.get("template_id", 0))
    nickname = data.get("nickname", "")

    if template_id == 0:
        return jsonify({"ok": False, "error": "template_id required"}), 400

    try:
        beast = beast_service.add_beast(user_id=1, template_id=template_id, nickname=nickname)
        template = beast_template_repo.get_by_id(beast.template_id)
        from application.services.beast_service import BeastWithInfo
        info = BeastWithInfo(beast=beast, template=template)
        return jsonify({"ok": True, "beast": info.to_dict()})
    except BeastError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.post("/api/beasts/<int:beast_id>/set-main")
def set_main_beast(beast_id: int):
    """设置出战幻兽"""
    try:
        beast = beast_service.set_main_beast(user_id=1, beast_id=beast_id)
        template = beast_template_repo.get_by_id(beast.template_id)
        from application.services.beast_service import BeastWithInfo
        info = BeastWithInfo(beast=beast, template=template)
        return jsonify({"ok": True, "beast": info.to_dict()})
    except BeastError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.get("/api/beast-templates")
def get_beast_templates():
    """获取所有幻兽模板（图鉴用）"""
    templates = beast_template_repo.get_all()
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


# ===== 捕捉接口 =====
@app.post("/api/capture")
def capture():
    """尝试捕捉幻兽"""
    data = request.get_json() or {}
    map_id = int(data.get("map_id", 0))
    use_strong_ball = bool(data.get("use_strong_ball", False))

    if map_id == 0:
        return jsonify({"ok": False, "error": "map_id required"}), 400

    try:
        result = capture_service.attempt_capture(
            user_id=1,
            map_id=map_id,
            use_strong_ball=use_strong_ball,
        )

        response = {
            "ok": result.success,
            "message": result.message,
        }

        if result.success and result.beast:
            template = beast_template_repo.get_by_id(result.beast.template_id)
            from application.services.beast_service import BeastWithInfo
            info = BeastWithInfo(beast=result.beast, template=template)
            response["beast"] = info.to_dict()

        return jsonify(response)
    except CaptureError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


# ===== 闯塔接口 =====
@app.get("/api/tower/info")
def get_tower_info():
    """获取闯塔信息"""
    tower_type = request.args.get("type", "tongtian")
    info = tower_service.get_tower_info(user_id=1, tower_type=tower_type)
    return jsonify(info)


@app.get("/api/tower/guardian/<int:floor>")
def get_tower_guardian(floor: int):
    """获取某层守塔幻兽信息"""
    tower_type = request.args.get("type", "tongtian")
    guardians = tower_service.get_floor_guardians(tower_type, floor)
    return jsonify({"floor": floor, "guardians": guardians})


@app.post("/api/tower/challenge")
def tower_challenge():
    """手动挑战一层"""
    data = request.get_json() or {}
    tower_type = data.get("tower_type", "tongtian")
    use_buff = data.get("use_buff", True)
    
    # 获取玩家战斗队幻兽（临时模拟数据）
    # TODO: 后续从玩家幻兽系统获取
    player_beasts = [
        PlayerBeast(id=1, name="圣灵蚁", realm="神界", level=84, hp=54737, attack=28375, defense=5339, speed=2024),
        PlayerBeast(id=2, name="神·朱雀", realm="天界", level=84, hp=48000, attack=25000, defense=6000, speed=1800),
        PlayerBeast(id=3, name="霸王龙VI(绝版)", realm="天界", level=84, hp=52000, attack=30000, defense=5500, speed=1600),
        PlayerBeast(id=4, name="神·青龙", realm="天界", level=84, hp=50000, attack=27000, defense=7000, speed=2200),
    ]
    
    try:
        battle = tower_service.challenge_floor(
            user_id=1,
            tower_type=tower_type,
            player_beasts=player_beasts,
            use_buff=use_buff,
        )
        return jsonify({
            "ok": True,
            "battle": battle.to_dict(),
            "state": tower_service.get_tower_info(user_id=1, tower_type=tower_type),
        })
    except TowerError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.post("/api/tower/auto")
def tower_auto_challenge():
    """自动闯塔"""
    data = request.get_json() or {}
    tower_type = data.get("tower_type", "tongtian")
    use_buff = data.get("use_buff", True)
    
    # 从MySQL获取玩家战斗队幻兽
    beast_data_list = player_beast_repo.get_team_beasts(user_id=1)
    player_beasts = [
        PlayerBeast(
            id=b.id,
            name=b.name,
            realm=b.realm,
            level=b.level,
            hp=b.hp,
            attack=b.physical_attack,
            defense=b.physical_defense,
            speed=b.speed,
            nature=b.nature,
            physical_attack=b.physical_attack,
            magic_attack=b.magic_attack,
            physical_defense=b.physical_defense,
            magic_defense=b.magic_defense,
        )
        for b in beast_data_list
    ]
    
    try:
        result = tower_service.auto_challenge(
            user_id=1,
            tower_type=tower_type,
            player_beasts=player_beasts,
            use_buff=use_buff,
        )
        return jsonify({
            "ok": True,
            "result": result.to_dict(),
            "state": tower_service.get_tower_info(user_id=1, tower_type=tower_type),
        })
    except TowerError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.get("/api/tower/battle/<int:battle_index>")
def get_tower_battle_detail(battle_index: int):
    """获取战报详情（临时：从最近的自动闯塔结果获取）"""
    # TODO: 后续实现战报存储
    return jsonify({"error": "战报详情功能待实现"}), 501


@app.post("/api/tower/reset")
def tower_reset():
    """退出闯塔，重置层数，发放累积奖励"""
    data = request.get_json() or {}
    tower_type = data.get("tower_type", "tongtian")
    pending_rewards = data.get("pending_rewards", None)
    
    result = tower_service.reset_tower(
        user_id=1, 
        tower_type=tower_type,
        pending_rewards=pending_rewards
    )
    return jsonify({"ok": True, "state": result})


@app.get("/api/tower/guardian/<tower_type>/<int:floor>")
def get_guardian_detail(tower_type: str, floor: int):
    """获取守塔幻兽详情"""
    guardians = tower_service.config_repo.get_guardians_for_floor(tower_type, floor)
    if not guardians:
        return jsonify({"ok": False, "error": "未找到守塔幻兽"}), 404
    
    guardian = guardians[0]
    combat_power = int((guardian.hp + guardian.physical_attack + guardian.magic_attack + 
                        guardian.physical_defense + guardian.magic_defense + guardian.speed) / 10)
    
    return jsonify({
        "ok": True,
        "guardian": {
            "name": guardian.name,
            "description": guardian.description,
            "level": guardian.level,
            "nature": guardian.nature,
            "hp": guardian.hp,
            "physical_attack": guardian.physical_attack,
            "magic_attack": guardian.magic_attack,
            "physical_defense": guardian.physical_defense,
            "magic_defense": guardian.magic_defense,
            "speed": guardian.speed,
            "combat_power": combat_power,
        }
    })


@app.get("/api/tower/player-beast/<int:beast_id>")
def get_player_beast_detail(beast_id: int):
    """获取玩家幻兽详情（从MySQL读取）"""
    beast_data = player_beast_repo.get_by_id(beast_id)
    if not beast_data:
        return jsonify({"ok": False, "error": "未找到幻兽"}), 404
    
    return jsonify({"ok": True, "beast": beast_data.to_dict()})


# ===== 镇妖接口 =====
@app.get("/api/zhenyao/info")
def get_zhenyao_info():
    """获取镇妖信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    info = zhenyao_service.get_zhenyao_info(user_id=user_id)
    return jsonify({
        "ok": info.can_zhenyao,
        "can_zhenyao": info.can_zhenyao,
        "player_level": info.player_level,
        "rank_name": info.rank_name,
        "zhenyao_range": info.zhenyao_range,
        "tower_max_floor": info.tower_max_floor,
        "trial_count": len(info.trial_floors),
        "hell_count": len(info.hell_floors),
        "error": info.error_msg,
    })


@app.get("/api/zhenyao/floors")
def get_zhenyao_floors():
    """获取镇妖层数列表"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    floor_type = request.args.get("type", "trial")  # trial 或 hell
    result = zhenyao_service.get_floor_list(user_id=user_id, floor_type=floor_type)
    return jsonify(result)


@app.post("/api/zhenyao/occupy")
def occupy_zhenyao_floor():
    """占领某层"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    floor = int(data.get("floor", 0))
    
    if floor <= 0:
        return jsonify({"ok": False, "error": "无效的层数"}), 400
    
    result = zhenyao_service.occupy_floor(user_id=user_id, floor=floor)
    return jsonify(result)


@app.post("/api/zhenyao/challenge")
def challenge_zhenyao_floor():
    """挑战某层（抢夺）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    floor = int(data.get("floor", 0))
    
    if floor <= 0:
        return jsonify({"ok": False, "error": "无效的层数"}), 400
    
    result = zhenyao_service.challenge_floor(user_id=user_id, floor=floor)
    return jsonify(result)


@app.get("/api/zhenyao/dynamics")
def get_zhenyao_dynamics():
    """获取镇妖动态列表"""
    user_id = get_current_user_id()
    dynamic_type = request.args.get("type", "all")  # all 或 personal
    limit = int(request.args.get("limit", 20))
    
    dynamics = zhenyao_service.get_dynamics(
        user_id=user_id,
        dynamic_type=dynamic_type,
        limit=limit
    )
    return jsonify({"ok": True, "dynamics": dynamics})


@app.get("/api/zhenyao/battle/<int:battle_id>")
def get_zhenyao_battle(battle_id: int):
    """获取镇妖战斗详情"""
    log = zhenyao_service.get_battle_log(battle_id)
    if not log:
        return jsonify({"ok": False, "error": "战斗记录不存在"}), 404
    
    return jsonify({"ok": True, "battle": log})


@app.get("/api/player/info")
def get_player_info():
    """获取玩家基础信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    player = player_repo.get_by_id(user_id=user_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    return jsonify({
        "ok": True,
        "player": {
            "user_id": player.user_id,
            "nickname": player.nickname,
            "level": player.level,
            "rank_name": player.get_rank_name(),
            "exp": player.exp,
            "gold": player.gold,
        }
    })


@app.get("/api/player/profile")
def get_player_profile():
    """获取其他玩家的个人信息页"""
    target_id = request.args.get("id", type=int)
    if not target_id:
        return jsonify({"ok": False, "error": "缺少玩家ID"}), 400
    
    player = player_repo.get_by_id(user_id=target_id)
    if not player:
        return jsonify({"ok": False, "error": "玩家不存在"}), 404
    
    # 获取玩家幻兽
    beasts = player_beast_repo.get_team_beasts(target_id)
    beasts_data = []
    for b in beasts:
        beasts_data.append({
            "id": b.id,
            "name": b.name,
            "realm": b.realm,
            "level": b.level,
            "combat_power": b.combat_power,
        })
    
    # 获取玩家动态（镇妖战斗记录）
    from infrastructure.db.zhenyao_battle_repo_mysql import MySQLZhenyaoBattleRepo
    battle_repo = MySQLZhenyaoBattleRepo()
    logs = battle_repo.get_user_battles(target_id, limit=10)
    dynamics = []
    for log in logs:
        time_str = log.created_at.strftime("%m-%d %H:%M") if log.created_at else ""
        if log.is_success:
            text = f"聚魂阵无人镇守，抢夺{log.floor}层聚魂阵成功！"
        else:
            text = f"挑战{log.defender_name}的第{log.floor}层失败！"
        dynamics.append({
            "time": time_str,
            "text": text,
        })
    
    return jsonify({
        "ok": True,
        "player": {
            "user_id": player.user_id,
            "nickname": player.nickname,
            "level": player.level,
            "rank_name": player.get_rank_name(),
            "exp": player.exp,
            "gold": player.gold,
            "gender": "男",
            "charm_level": 1,
            "charm": 0,
            "prestige": 0,
            "energy": 100,
            "spirit_stone": 5,
            "wins": 0,
            "battles": 0,
            "arena_rank": 1,
            "arena_position": 1,
            "status": "落龙镇",
            "status_detail": "修行中",
            "mount": "破天飞剑",
            "alliance": "暗河",
            "alliance_title": "风起云涌",
            "alliance_level": 10,
            "title": "飞龙之王",
        },
        "beasts": beasts_data,
        "dynamics": dynamics,
    })


# ===== 修行系统 API =====

def _deprecated_api():
    return jsonify({
        "ok": False,
        "error": "app_old 已下线，请使用 interfaces.web_api.app (app.py) 提供的 /api 接口",
    }), 410


@app.get("/api/cultivation/status")
def get_cultivation_status():
    """获取修行状态"""
    return _deprecated_api()


@app.get("/api/cultivation/options")
def get_cultivation_options():
    """获取修行选项"""
    return _deprecated_api()


@app.post("/api/cultivation/start")
def start_cultivation():
    """开始修行"""
    return _deprecated_api()


@app.post("/api/cultivation/harvest")
def harvest_cultivation():
    """领取修行奖励"""
    return _deprecated_api()


@app.post("/api/cultivation/stop")
def stop_cultivation():
    """终止修行"""
    return _deprecated_api()


@app.post("/api/player/levelup")
def player_levelup():
    """晋级"""
    return _deprecated_api()


# ===== 地图系统 API =====
@app.get("/api/map/info")
def get_map_info():
    """获取地图信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    # 直接从数据库查询位置信息
    from infrastructure.db.connection import execute_query
    rows = execute_query("SELECT level, location FROM player WHERE user_id = %s", (user_id,))
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    row = rows[0]
    return jsonify({
        "ok": True,
        "current_location": row.get('location') or '落龙镇',
        "level": row.get('level', 1),
    })


@app.post("/api/map/move")
def map_move():
    """移动到相邻城市（免费）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    city = data.get("city", "")
    
    # 简化处理，直接更新位置
    # 实际应该验证是否是相邻城市
    from infrastructure.db.connection import execute_update
    execute_update("UPDATE player SET location = %s WHERE user_id = %s", (city, user_id))
    
    return jsonify({"ok": True, "message": f"已移动到{city}"})


@app.post("/api/map/teleport")
def map_teleport():
    """传送到城市（消耗传送符）"""
    return jsonify({
        "ok": False,
        "error": "该接口已废弃，请使用 /api/map/teleport（新地图路由，会真实消耗传送符）",
    }), 410


@app.get("/api/player/teleport-count")
def get_teleport_count():
    """获取传送符数量"""
    return jsonify({
        "ok": False,
        "error": "该接口已废弃，请使用 /api/map/teleport-count",
    }), 410


# ===== 鼓舞系统 API =====
INSPIRE_DURATION_SECONDS = 30 * 60  # 30分钟
INSPIRE_PILL_ITEM_ID = 8001  # 鼓舞丹物品ID

@app.get("/api/tower/inspire/status")
def get_inspire_status():
    """获取鼓舞状态"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    from infrastructure.db.connection import execute_query
    from datetime import datetime
    
    # 查询鼓舞状态
    rows = execute_query(
        "SELECT inspire_expire_time FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    active = False
    remaining_seconds = 0
    
    if rows and rows[0].get('inspire_expire_time'):
        expire_time = rows[0]['inspire_expire_time']
        if isinstance(expire_time, datetime):
            now = datetime.now()
            if expire_time > now:
                active = True
                remaining_seconds = int((expire_time - now).total_seconds())
    
    # 查询鼓舞丹数量
    pill_count = 0
    inv_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, INSPIRE_PILL_ITEM_ID)
    )
    if inv_rows:
        pill_count = inv_rows[0].get('quantity', 0)
    
    return jsonify({
        "ok": True,
        "active": active,
        "remaining_seconds": remaining_seconds,
        "inspire_pill_count": pill_count,
    })


@app.post("/api/tower/inspire/use")
def use_inspire_pill():
    """使用鼓舞丹"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    from infrastructure.db.connection import execute_query, execute_update
    from datetime import datetime, timedelta
    
    # 检查是否已有鼓舞效果
    rows = execute_query(
        "SELECT inspire_expire_time FROM player WHERE user_id = %s",
        (user_id,)
    )
    
    if rows and rows[0].get('inspire_expire_time'):
        expire_time = rows[0]['inspire_expire_time']
        if isinstance(expire_time, datetime) and expire_time > datetime.now():
            return jsonify({"ok": False, "error": "鼓舞效果正在生效中，无法叠加使用！"})
    
    # 检查鼓舞丹数量
    inv_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s",
        (user_id, INSPIRE_PILL_ITEM_ID)
    )
    
    if not inv_rows or inv_rows[0].get('quantity', 0) <= 0:
        return jsonify({"ok": False, "error": "鼓舞丹不足！"})
    
    # 消耗鼓舞丹
    execute_update(
        "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = %s",
        (user_id, INSPIRE_PILL_ITEM_ID)
    )
    
    # 设置鼓舞过期时间
    expire_time = datetime.now() + timedelta(seconds=INSPIRE_DURATION_SECONDS)
    execute_update(
        "UPDATE player SET inspire_expire_time = %s WHERE user_id = %s",
        (expire_time, user_id)
    )
    
    return jsonify({
        "ok": True,
        "message": "使用鼓舞丹成功！战力提升10%，持续30分钟。"
    })


# ===== 擂台系统 API =====
# 等级阶段配置
LEVEL_RANKS = [
    (1, 19, '见习', False),   # 1-19级见习，不能参与擂台
    (20, 29, '黄阶', True),
    (30, 39, '玄阶', True),
    (40, 49, '地阶', True),
    (50, 59, '天阶', True),
    (60, 69, '飞马', True),
    (70, 79, '天龙', True),
    (80, 100, '战神', True),
]

# 擂台消耗物品ID
ARENA_BALL_NORMAL = 4002  # 普通场消耗捕捉球
ARENA_BALL_GOLD = 4003    # 黄金场消耗强力捕捉球
ARENA_MAX_WINS = 10       # 连胜10场自动下台

def get_player_rank(level):
    """根据等级获取阶段名称和是否能参与擂台"""
    for min_lv, max_lv, rank_name, can_arena in LEVEL_RANKS:
        if min_lv <= level <= max_lv:
            return rank_name, can_arena
    return '见习', False

def get_arena_ball_id(arena_type):
    """获取擂台消耗的球ID"""
    return ARENA_BALL_GOLD if arena_type == 'gold' else ARENA_BALL_NORMAL

def get_arena_ball_name(arena_type):
    """获取擂台消耗的球名称"""
    return '强力捕捉球' if arena_type == 'gold' else '捕捉球'

@app.get("/api/arena/info")
def get_arena_info():
    """获取擂台信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    arena_type = request.args.get('type', 'normal')  # normal普通场, gold黄金场
    
    # 获取玩家等级和昵称
    from infrastructure.db.connection import execute_query
    rows = execute_query(
        "SELECT level, nickname FROM player WHERE user_id = %s", 
        (user_id,)
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    player_level = rows[0].get('level', 1)
    player_nickname = rows[0].get('nickname', '未知')
    rank_name, can_arena = get_player_rank(player_level)
    
    if not can_arena:
        return jsonify({
            "ok": True,
            "canArena": False,
            "message": "20级以上才能参与擂台",
            "playerLevel": player_level,
            "rankName": rank_name,
        })
    
    # 从数据库获取擂台信息
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    
    if not arena_rows:
        # 擂台不存在，返回空擂台状态
        arena = {
            "champion": None,
            "championNickname": None,
            "consecutiveWins": 0,
            "prizePool": 0,
            "isChampion": False,
            "isEmpty": True,
        }
    else:
        arena_data = arena_rows[0]
        is_champion = arena_data.get('champion_user_id') == user_id
        arena = {
            "champion": arena_data.get('champion_nickname'),
            "championUserId": arena_data.get('champion_user_id'),
            "consecutiveWins": arena_data.get('consecutive_wins', 0),
            "prizePool": arena_data.get('prize_pool', 0),
            "isChampion": is_champion,
            "isEmpty": arena_data.get('champion_user_id') is None,
        }
    
    # 获取玩家拥有的球数量
    ball_id = get_arena_ball_id(arena_type)
    ball_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
        (user_id, ball_id)
    )
    ball_count = ball_rows[0].get('quantity', 0) if ball_rows else 0
    
    return jsonify({
        "ok": True,
        "canArena": True,
        "playerLevel": player_level,
        "playerNickname": player_nickname,
        "rankName": rank_name,
        "arenaName": f"{rank_name}擂台",
        "arenaType": arena_type,
        "arenaTypeName": "黄金场" if arena_type == "gold" else "普通场",
        "ballName": get_arena_ball_name(arena_type),
        "ballCount": ball_count,
        "arena": arena,
    })


@app.post("/api/arena/occupy")
def occupy_arena():
    """占领空擂台"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    arena_type = data.get('type', 'normal')
    
    from infrastructure.db.connection import execute_query, execute_update
    
    # 获取玩家信息
    rows = execute_query(
        "SELECT level, nickname FROM player WHERE user_id = %s", 
        (user_id,)
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    player_level = rows[0].get('level', 1)
    player_nickname = rows[0].get('nickname', '未知')
    rank_name, can_arena = get_player_rank(player_level)
    
    if not can_arena:
        return jsonify({"ok": False, "error": "等级不足，无法参与擂台"})
    
    # 检查擂台是否空置
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    if not arena_rows:
        return jsonify({"ok": False, "error": "擂台不存在"})
    
    arena_data = arena_rows[0]
    if arena_data.get('champion_user_id') is not None:
        return jsonify({"ok": False, "error": "擂台已有擂主，请选择挑战"})
    
    # 检查并消耗球
    ball_id = get_arena_ball_id(arena_type)
    ball_name = get_arena_ball_name(arena_type)
    ball_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
        (user_id, ball_id)
    )
    if not ball_rows or ball_rows[0].get('quantity', 0) < 1:
        return jsonify({"ok": False, "error": f"{ball_name}不足"})
    
    # 消耗球
    execute_update(
        "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
        (user_id, ball_id)
    )
    
    # 占领擂台，奖池+1
    execute_update(
        """UPDATE arena SET 
           champion_user_id = %s, 
           champion_nickname = %s, 
           consecutive_wins = 0, 
           prize_pool = prize_pool + 1,
           last_battle_time = NOW()
           WHERE rank_name = %s AND arena_type = %s""",
        (user_id, player_nickname, rank_name, arena_type)
    )
    
    return jsonify({
        "ok": True,
        "message": f"成功占领{rank_name}擂台（{'黄金场' if arena_type == 'gold' else '普通场'}）！"
    })


@app.post("/api/arena/challenge")
def challenge_arena():
    """挑战擂台"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    arena_type = data.get('type', 'normal')
    
    from infrastructure.db.connection import execute_query, execute_update
    import random
    
    # 获取玩家信息
    rows = execute_query(
        "SELECT level, nickname FROM player WHERE user_id = %s", 
        (user_id,)
    )
    if not rows:
        return jsonify({"ok": False, "error": "玩家不存在"})
    
    player_level = rows[0].get('level', 1)
    player_nickname = rows[0].get('nickname', '未知')
    rank_name, can_arena = get_player_rank(player_level)
    
    if not can_arena:
        return jsonify({"ok": False, "error": "等级不足，无法参与擂台"})
    
    # 检查擂台状态
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    if not arena_rows:
        return jsonify({"ok": False, "error": "擂台不存在"})
    
    arena_data = arena_rows[0]
    champion_user_id = arena_data.get('champion_user_id')
    
    if champion_user_id is None:
        return jsonify({"ok": False, "error": "擂台空置，请选择占领"})
    
    if champion_user_id == user_id:
        return jsonify({"ok": False, "error": "你已经是擂主了"})
    
    # 检查并消耗球
    ball_id = get_arena_ball_id(arena_type)
    ball_name = get_arena_ball_name(arena_type)
    ball_rows = execute_query(
        "SELECT quantity FROM player_inventory WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
        (user_id, ball_id)
    )
    if not ball_rows or ball_rows[0].get('quantity', 0) < 1:
        return jsonify({"ok": False, "error": f"{ball_name}不足"})
    
    # 消耗球
    execute_update(
        "UPDATE player_inventory SET quantity = quantity - 1 WHERE user_id = %s AND item_id = %s AND is_temporary = 0",
        (user_id, ball_id)
    )
    
    # 奖池+1
    execute_update(
        "UPDATE arena SET prize_pool = prize_pool + 1 WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    
    # 模拟战斗结果（后续可改为真实战斗逻辑）
    challenger_wins = random.random() < 0.5  # 50%胜率
    
    # 重新获取擂台信息（包含更新后的奖池）
    arena_rows = execute_query(
        "SELECT * FROM arena WHERE rank_name = %s AND arena_type = %s",
        (rank_name, arena_type)
    )
    arena_data = arena_rows[0]
    prize_pool = arena_data.get('prize_pool', 0)
    champion_nickname = arena_data.get('champion_nickname', '未知')
    consecutive_wins = arena_data.get('consecutive_wins', 0)
    
    if challenger_wins:
        # 挑战者获胜：获得奖池所有球，成为新擂主
        if prize_pool > 0:
            # 给挑战者添加球
            execute_update(
                """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
                   VALUES (%s, %s, %s, 0)
                   ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
                (user_id, ball_id, prize_pool, prize_pool)
            )
        
        # 更新擂台：新擂主，奖池清零，连胜归零
        execute_update(
            """UPDATE arena SET 
               champion_user_id = %s, 
               champion_nickname = %s, 
               consecutive_wins = 0, 
               prize_pool = 0,
               last_battle_time = NOW()
               WHERE rank_name = %s AND arena_type = %s""",
            (user_id, player_nickname, rank_name, arena_type)
        )
        
        return jsonify({
            "ok": True,
            "win": True,
            "message": f"恭喜！你击败了{champion_nickname}，获得奖池{prize_pool}个{ball_name}，成为新擂主！"
        })
    else:
        # 擂主获胜：连胜+1
        new_consecutive_wins = consecutive_wins + 1
        
        if new_consecutive_wins >= ARENA_MAX_WINS:
            # 连胜10场，擂主拿走奖池，自动下台
            if prize_pool > 0:
                execute_update(
                    """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
                       VALUES (%s, %s, %s, 0)
                       ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
                    (champion_user_id, ball_id, prize_pool, prize_pool)
                )
            # 记录守擂成功次数 +1（达成10连胜）
            execute_update(
                """INSERT INTO arena_stats (user_id, rank_name, success_count)
                    VALUES (%s, %s, 1)
                    ON DUPLICATE KEY UPDATE success_count = success_count + 1""",
                (champion_user_id, rank_name)
            )
            
            # 擂台清空
            execute_update(
                """UPDATE arena SET 
                   champion_user_id = NULL, 
                   champion_nickname = NULL, 
                   consecutive_wins = 0, 
                   prize_pool = 0,
                   last_battle_time = NOW()
                   WHERE rank_name = %s AND arena_type = %s""",
                (rank_name, arena_type)
            )
            
            return jsonify({
                "ok": True,
                "win": False,
                "message": f"挑战失败！{champion_nickname}连胜{ARENA_MAX_WINS}场，获得奖池{prize_pool}个{ball_name}后光荣下台！"
            })
        else:
            # 正常连胜
            execute_update(
                """UPDATE arena SET 
                   consecutive_wins = %s,
                   last_battle_time = NOW()
                   WHERE rank_name = %s AND arena_type = %s""",
                (new_consecutive_wins, rank_name, arena_type)
            )
            
            return jsonify({
                "ok": True,
                "win": False,
                "message": f"挑战失败！{champion_nickname}成功防守，连胜{new_consecutive_wins}场！"
            })


@app.get("/api/arena/dynamics")
def get_arena_dynamics():
    """获取擂台动态"""
    dynamic_type = request.args.get('type', 'arena')
    
    # 模拟数据（后续可从数据库读取战斗记录）
    dynamics = [
        {"time": "2025年12月5日 11:00", "player": "勇士", "action": "占领了黄阶擂台普通场", "opponent": "", "extra": "", "hasDetail": False},
    ]
    
    return jsonify({
        "ok": True,
        "dynamics": dynamics,
    })


# ===== 召唤之王挑战赛 =====
KING_DAILY_MAX_CHALLENGES = 15  # 每日最大挑战次数

def ensure_king_rank(user_id):
    """确保玩家有挑战赛排名记录，没有则初始化"""
    from infrastructure.db.connection import execute_query, execute_update
    
    # 检查是否已有排名
    rows = execute_query("SELECT * FROM king_challenge_rank WHERE user_id = %s", (user_id,))
    if rows:
        return rows[0]
    
    # 计算赛区
    total_rows = execute_query("SELECT COUNT(*) AS total FROM player")
    total = total_rows[0].get('total', 0) if total_rows else 0
    
    idx_rows = execute_query("SELECT COUNT(*) AS idx FROM player WHERE user_id <= %s", (user_id,))
    my_index = idx_rows[0].get('idx', 1) if idx_rows else 1
    
    half = (total + 1) // 2
    area_index = 1 if my_index <= half else 2
    
    # 在该赛区获取当前最大排名，新玩家排在最后
    max_rank_rows = execute_query(
        "SELECT COALESCE(MAX(rank_position), 0) AS max_rank FROM king_challenge_rank WHERE area_index = %s",
        (area_index,)
    )
    new_rank = (max_rank_rows[0].get('max_rank', 0) if max_rank_rows else 0) + 1
    
    # 插入新记录
    execute_update(
        """INSERT INTO king_challenge_rank (user_id, area_index, rank_position, today_challenges, last_challenge_date)
           VALUES (%s, %s, %s, 0, CURDATE())""",
        (user_id, area_index, new_rank)
    )
    
    return {
        'user_id': user_id,
        'area_index': area_index,
        'rank_position': new_rank,
        'win_streak': 0,
        'total_wins': 0,
        'total_losses': 0,
        'today_challenges': 0
    }


@app.get("/api/king/info")
def get_king_info():
    """返回召唤之王挑战赛信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})

    from infrastructure.db.connection import execute_query
    
    # 确保玩家有排名记录
    my_rank_info = ensure_king_rank(user_id)
    area_index = my_rank_info['area_index']
    my_rank = my_rank_info['rank_position']
    win_streak = my_rank_info['win_streak']
    
    # 检查今日挑战次数（跨天重置）
    today_challenges = my_rank_info['today_challenges']
    last_date = my_rank_info.get('last_challenge_date')
    from datetime import date
    if last_date and str(last_date) != str(date.today()):
        today_challenges = 0
    
    area_name = '一赛区' if area_index == 1 else '二赛区'
    
    # 获取可挑战的3个玩家（排名比我高的玩家，即排名数字比我小的）
    challengers = []
    if my_rank > 1:
        # 获取排名比我高的最多3个玩家
        challenger_rows = execute_query(
            """SELECT k.user_id, k.rank_position, p.nickname 
               FROM king_challenge_rank k 
               JOIN player p ON k.user_id = p.user_id
               WHERE k.area_index = %s AND k.rank_position < %s
               ORDER BY k.rank_position DESC
               LIMIT 3""",
            (area_index, my_rank)
        )
        for row in challenger_rows:
            challengers.append({
                "userId": row['user_id'],
                "nickname": row['nickname'],
                "rank": row['rank_position']
            })
    
    # 获取全服玩家总数
    total_rows = execute_query("SELECT COUNT(*) AS total FROM player")
    total_players = total_rows[0].get('total', 0) if total_rows else 0

    return jsonify({
        "ok": True,
        "phase": "pre",
        "totalPlayers": total_players,
        "areaIndex": area_index,
        "areaName": area_name,
        "myRank": my_rank,
        "winStreak": win_streak,
        "todayChallenges": today_challenges,
        "todayMax": KING_DAILY_MAX_CHALLENGES,
        "challengers": challengers,
    })


@app.post("/api/king/challenge")
def king_challenge():
    """发起挑战"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    data = request.get_json() or {}
    target_user_id = data.get('targetUserId')
    if not target_user_id:
        return jsonify({"ok": False, "error": "请选择挑战对象"})
    
    from infrastructure.db.connection import execute_query, execute_update
    from datetime import date
    import random
    
    # 获取我的排名信息
    my_rank_info = ensure_king_rank(user_id)
    my_area = my_rank_info['area_index']
    my_rank = my_rank_info['rank_position']
    
    # 检查今日挑战次数
    today_challenges = my_rank_info['today_challenges']
    last_date = my_rank_info.get('last_challenge_date')
    if last_date and str(last_date) != str(date.today()):
        today_challenges = 0
    
    if today_challenges >= KING_DAILY_MAX_CHALLENGES:
        return jsonify({"ok": False, "error": "今日挑战次数已用完"})
    
    # 获取目标玩家信息
    target_rows = execute_query(
        "SELECT k.*, p.nickname FROM king_challenge_rank k JOIN player p ON k.user_id = p.user_id WHERE k.user_id = %s",
        (target_user_id,)
    )
    if not target_rows:
        return jsonify({"ok": False, "error": "对手不存在"})
    
    target_info = target_rows[0]
    target_rank = target_info['rank_position']
    target_nickname = target_info['nickname']
    target_area = target_info['area_index']
    
    # 验证是否同赛区
    if target_area != my_area:
        return jsonify({"ok": False, "error": "只能挑战同赛区的玩家"})
    
    # 验证排名（只能挑战排名比自己高的）
    if target_rank >= my_rank:
        return jsonify({"ok": False, "error": "只能挑战排名比自己高的玩家"})
    
    # 模拟战斗结果（随机50%胜率，后续可接入真实战斗）
    challenger_wins = random.choice([True, False])
    
    # 预选赛奖励：胜利2万铜钱，失败2千铜钱
    KING_WIN_REWARD = 20000
    KING_LOSE_REWARD = 2000
    reward = KING_WIN_REWARD if challenger_wins else KING_LOSE_REWARD
    
    # 发放铜钱奖励
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (reward, user_id)
    )
    
    # 更新今日挑战次数
    execute_update(
        """UPDATE king_challenge_rank 
           SET today_challenges = %s, last_challenge_date = CURDATE()
           WHERE user_id = %s""",
        (today_challenges + 1, user_id)
    )
    
    if challenger_wins:
        # 挑战者获胜：交换排名
        execute_update(
            "UPDATE king_challenge_rank SET rank_position = %s, win_streak = win_streak + 1, total_wins = total_wins + 1 WHERE user_id = %s",
            (target_rank, user_id)
        )
        execute_update(
            "UPDATE king_challenge_rank SET rank_position = %s, win_streak = 0, total_losses = total_losses + 1 WHERE user_id = %s",
            (my_rank, target_user_id)
        )
        
        return jsonify({
            "ok": True,
            "win": True,
            "message": f"恭喜！你击败了{target_nickname}，排名上升至第{target_rank}名！获得{KING_WIN_REWARD}铜钱",
            "newRank": target_rank,
            "reward": KING_WIN_REWARD
        })
    else:
        # 挑战者失败：排名不变，连胜清零
        execute_update(
            "UPDATE king_challenge_rank SET win_streak = 0, total_losses = total_losses + 1 WHERE user_id = %s",
            (user_id,)
        )
        execute_update(
            "UPDATE king_challenge_rank SET win_streak = win_streak + 1, total_wins = total_wins + 1 WHERE user_id = %s",
            (target_user_id,)
        )
        
        return jsonify({
            "ok": True,
            "win": False,
            "message": f"挑战失败！{target_nickname}成功防守，排名保持第{my_rank}名。获得{KING_LOSE_REWARD}铜钱",
            "newRank": my_rank,
            "reward": KING_LOSE_REWARD
        })


# 正赛奖励配置（排名区间 -> 奖励内容）
# 物品ID: 5001=强力草, 5002=追魂法宝, 5003=技能书口袋
KING_FINAL_REWARDS = {
    "champion": {
        "name": "冠军", "min": 1, "max": 1, "gold": 450000,
        "items": [{"id": 5001, "name": "强力草", "qty": 10}, {"id": 5002, "name": "追魂法宝", "qty": 12}, {"id": 5003, "name": "技能书口袋", "qty": 2}]
    },
    "runner_up": {
        "name": "亚军", "min": 2, "max": 2, "gold": 400000,
        "items": [{"id": 5001, "name": "强力草", "qty": 10}, {"id": 5002, "name": "追魂法宝", "qty": 10}, {"id": 5003, "name": "技能书口袋", "qty": 1}]
    },
    "top4": {
        "name": "四强", "min": 3, "max": 4, "gold": 350000,
        "items": [{"id": 5001, "name": "强力草", "qty": 10}, {"id": 5002, "name": "追魂法宝", "qty": 8}]
    },
    "top8": {
        "name": "八强", "min": 5, "max": 8, "gold": 300000,
        "items": [{"id": 5001, "name": "强力草", "qty": 7}, {"id": 5002, "name": "追魂法宝", "qty": 6}]
    },
    "top16": {
        "name": "十六强", "min": 9, "max": 16, "gold": 250000,
        "items": [{"id": 5001, "name": "强力草", "qty": 5}, {"id": 5002, "name": "追魂法宝", "qty": 4}]
    },
    "top32": {
        "name": "三十二强", "min": 17, "max": 32, "gold": 200000,
        "items": [{"id": 5001, "name": "强力草", "qty": 3}, {"id": 5002, "name": "追魂法宝", "qty": 2}]
    },
}


@app.get("/api/king/reward_info")
def get_king_reward_info():
    """获取正赛奖励信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    from infrastructure.db.connection import execute_query
    
    # 获取玩家排名
    rank_rows = execute_query(
        "SELECT rank_position, area_index FROM king_challenge_rank WHERE user_id = %s",
        (user_id,)
    )
    if not rank_rows:
        return jsonify({"ok": True, "myRank": 0, "rewardTier": None, "canClaim": False})
    
    my_rank = rank_rows[0]['rank_position']
    
    # 确定奖励档位
    reward_tier = None
    for key, cfg in KING_FINAL_REWARDS.items():
        if cfg['min'] <= my_rank <= cfg['max']:
            reward_tier = {
                "key": key,
                "name": cfg['name'],
                "gold": cfg['gold'],
            }
            break
    
    # 检查是否已领取
    claimed_rows = execute_query(
        "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = 1",
        (user_id,)
    )
    already_claimed = len(claimed_rows) > 0
    
    return jsonify({
        "ok": True,
        "myRank": my_rank,
        "rewardTier": reward_tier,
        "canClaim": reward_tier is not None and not already_claimed,
        "alreadyClaimed": already_claimed,
        "allRewards": [{"key": k, **v} for k, v in KING_FINAL_REWARDS.items()]
    })


@app.post("/api/king/claim_reward")
def claim_king_reward():
    """领取正赛奖励"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"})
    
    from infrastructure.db.connection import execute_query, execute_update
    
    # 获取玩家排名
    rank_rows = execute_query(
        "SELECT rank_position FROM king_challenge_rank WHERE user_id = %s",
        (user_id,)
    )
    if not rank_rows:
        return jsonify({"ok": False, "error": "你还没有参加挑战赛"})
    
    my_rank = rank_rows[0]['rank_position']
    
    # 确定奖励档位
    reward_cfg = None
    for key, cfg in KING_FINAL_REWARDS.items():
        if cfg['min'] <= my_rank <= cfg['max']:
            reward_cfg = cfg
            break
    
    if not reward_cfg:
        return jsonify({"ok": False, "error": "你的排名不在奖励范围内"})
    
    # 检查是否已领取
    claimed_rows = execute_query(
        "SELECT * FROM king_reward_claimed WHERE user_id = %s AND season = 1",
        (user_id,)
    )
    if claimed_rows:
        return jsonify({"ok": False, "error": "你已经领取过本赛季奖励了"})
    
    # 发放铜钱奖励
    execute_update(
        "UPDATE player SET gold = gold + %s WHERE user_id = %s",
        (reward_cfg['gold'], user_id)
    )
    
    # 发放物品奖励
    items_msg = []
    for item in reward_cfg.get('items', []):
        execute_update(
            """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary)
               VALUES (%s, %s, %s, 0)
               ON DUPLICATE KEY UPDATE quantity = quantity + %s""",
            (user_id, item['id'], item['qty'], item['qty'])
        )
        items_msg.append(f"{item['name']}x{item['qty']}")
    
    # 记录已领取
    execute_update(
        "INSERT INTO king_reward_claimed (user_id, season, reward_tier, claimed_at) VALUES (%s, 1, %s, NOW())",
        (user_id, reward_cfg['name'])
    )
    
    # 构建奖励消息
    msg = f"恭喜获得{reward_cfg['name']}奖励！铜钱+{reward_cfg['gold']}"
    if items_msg:
        msg += "，" + "、".join(items_msg)
    
    return jsonify({
        "ok": True,
        "message": msg,
        "gold": reward_cfg['gold'],
        "items": reward_cfg.get('items', [])
    })


# ===== 排行榜 API =====
@app.get("/api/ranking/list")
def get_ranking_list():
    """获取排行榜"""
    user_id = get_current_user_id()
    ranking_type = request.args.get('type', 'level')
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    
    from infrastructure.db.connection import execute_query
    
    # 计算偏移量
    offset = (page - 1) * size
    
    # 根据类型查询不同的排行
    if ranking_type == 'level':
        # 等级排行（按等级和声望排序）
        sql = """
            SELECT user_id as userId, nickname, level, prestige 
            FROM player 
            ORDER BY level DESC, prestige DESC 
            LIMIT %s OFFSET %s
        """
        count_sql = "SELECT COUNT(*) as total FROM player"
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query(count_sql)
        
    elif ranking_type == 'power':
        # 战力排行（简化：按等级排序）
        sql = """
            SELECT user_id as userId, nickname, level, level * 1000 as power 
            FROM player 
            ORDER BY level DESC 
            LIMIT %s OFFSET %s
        """
        count_sql = "SELECT COUNT(*) as total FROM player"
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query(count_sql)
        
    elif ranking_type == 'arena':
        # 擂台排行（按守擂成功次数，达成10连胜的次数）
        filter_rank = request.args.get('rank')
        # 默认按当前玩家等级阶段筛选
        if not filter_rank and user_id:
            level_rows = execute_query("SELECT level FROM player WHERE user_id = %s", (user_id,))
            level_val = level_rows[0]['level'] if level_rows else 1
            filter_rank, _can = get_player_rank(level_val)

        if filter_rank:
            sql = """
                SELECT s.user_id as userId, p.nickname, p.level, SUM(s.success_count) as successCount, %s as rankName
                FROM arena_stats s
                JOIN player p ON s.user_id = p.user_id
                WHERE s.rank_name = %s
                GROUP BY s.user_id, p.nickname, p.level
                ORDER BY successCount DESC
                LIMIT %s OFFSET %s
            """
            rows = execute_query(sql, (filter_rank, filter_rank, size, offset))
            total_rows = execute_query("SELECT COUNT(DISTINCT user_id) as total FROM arena_stats WHERE rank_name = %s", (filter_rank,))
        else:
            sql = """
                SELECT s.user_id as userId, p.nickname, p.level, SUM(s.success_count) as successCount, '全部擂台' as rankName
                FROM arena_stats s
                JOIN player p ON s.user_id = p.user_id
                GROUP BY s.user_id, p.nickname, p.level
                ORDER BY successCount DESC
                LIMIT %s OFFSET %s
            """
            rows = execute_query(sql, (size, offset))
            total_rows = execute_query("SELECT COUNT(DISTINCT user_id) as total FROM arena_stats")
        
    elif ranking_type == 'tower':
        # 通天塔排行
        sql = """
            SELECT t.user_id as userId, p.nickname, p.level, t.max_floor_record as towerFloor
            FROM tower_state t
            JOIN player p ON t.user_id = p.user_id
            WHERE t.tower_type = 'tongtian'
            ORDER BY t.max_floor_record DESC
            LIMIT %s OFFSET %s
        """
        count_sql = "SELECT COUNT(*) as total FROM tower_state WHERE tower_type = 'tongtian'"
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query(count_sql)
        
    else:
        # 默认等级排行
        sql = """
            SELECT user_id as userId, nickname, level, prestige 
            FROM player 
            ORDER BY level DESC, prestige DESC 
            LIMIT %s OFFSET %s
        """
        count_sql = "SELECT COUNT(*) as total FROM player"
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query(count_sql)
    
    # 计算总页数
    total = total_rows[0].get('total', 0) if total_rows else 0
    total_pages = (total + size - 1) // size if total > 0 else 1
    
    # 构建排名列表
    rankings = []
    for i, row in enumerate(rows):
        rankings.append({
            "rank": offset + i + 1,
            "userId": row.get('userId'),
            "nickname": row.get('nickname', '未知'),
            "level": row.get('level', 1),
            "prestige": row.get('prestige', 0),
            "power": row.get('power', 0),
            "arenaWins": row.get('arenaWins', 0),
            "successCount": row.get('successCount', 0),
            "rankName": row.get('rankName'),
            "towerFloor": row.get('towerFloor', 0),
        })
    
    # 获取当前用户的排名
    my_rank = 0
    if user_id:
        if ranking_type == 'level':
            rank_sql = """
                SELECT COUNT(*) + 1 as rank FROM player 
                WHERE level > (SELECT level FROM player WHERE user_id = %s)
                OR (level = (SELECT level FROM player WHERE user_id = %s) 
                    AND prestige > (SELECT prestige FROM player WHERE user_id = %s))
            """
            rank_rows = execute_query(rank_sql, (user_id, user_id, user_id))
            my_rank = rank_rows[0].get('rank', 0) if rank_rows else 0
        elif ranking_type == 'arena':
            # 计算我的守擂成功次数
            filter_rank = request.args.get('rank')
            if not filter_rank:
                lr = execute_query("SELECT level FROM player WHERE user_id = %s", (user_id,))
                lvl = lr[0]['level'] if lr else 1
                filter_rank, _can = get_player_rank(lvl)
            if filter_rank:
                my_sc_rows = execute_query("SELECT SUM(success_count) as sc FROM arena_stats WHERE user_id = %s AND rank_name = %s", (user_id, filter_rank))
                my_sc = my_sc_rows[0]['sc'] if (my_sc_rows and my_sc_rows[0]['sc'] is not None) else 0
                if my_sc > 0:
                    rank_rows = execute_query(
                        """
                        SELECT COUNT(*) + 1 as rank FROM (
                            SELECT user_id, SUM(success_count) as sc FROM arena_stats WHERE rank_name = %s GROUP BY user_id
                        ) t WHERE t.sc > %s
                        """,
                        (filter_rank, my_sc)
                    )
                    my_rank = rank_rows[0]['rank'] if rank_rows else 0
                else:
                    my_rank = 0
            else:
                my_sc_rows = execute_query("SELECT SUM(success_count) as sc FROM arena_stats WHERE user_id = %s", (user_id,))
                my_sc = my_sc_rows[0]['sc'] if (my_sc_rows and my_sc_rows[0]['sc'] is not None) else 0
                if my_sc > 0:
                    rank_rows = execute_query(
                        """
                        SELECT COUNT(*) + 1 as rank FROM (
                            SELECT user_id, SUM(success_count) as sc FROM arena_stats GROUP BY user_id
                        ) t WHERE t.sc > %s
                        """,
                        (my_sc,)
                    )
                    my_rank = rank_rows[0]['rank'] if rank_rows else 0
                else:
                    my_rank = 0
    
    resp = {
        "ok": True,
        "myRank": my_rank,
        "rankings": rankings,
        "totalPages": total_pages,
        "currentPage": page,
    }
    if ranking_type == 'arena':
        # 返回当前筛选的阶段名（用于页面显示“天龙擂台|全部擂台”）
        resp["arenaRankName"] = filter_rank if 'filter_rank' in locals() and filter_rank else None
    return jsonify(resp)


if __name__ == "__main__":
    app.run(debug=True)
