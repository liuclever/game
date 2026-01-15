from flask import Blueprint, request, jsonify, session
from datetime import datetime
from interfaces.web_api.bootstrap import services

alliance_bp = Blueprint('alliance', __name__, url_prefix='/api/alliance')

def get_current_user_id() -> int:
    return session.get('user_id', 0)

@alliance_bp.post('/create')
def create_alliance():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    
    if not name:
        return jsonify({"ok": False, "error": "请输入联盟名称"}), 400
    
    result = services.alliance_service.create_alliance(user_id, name)
    return jsonify(result)


@alliance_bp.get('/list')
def list_alliances():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    keyword = (request.args.get('keyword') or '').strip() or None
    try:
        page = int(request.args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    try:
        size = int(request.args.get('size', 10))
    except (TypeError, ValueError):
        size = 10

    result = services.alliance_service.list_alliances(user_id, keyword=keyword, page=page, size=size)
    status = 200 if result.get('ok') else 400
    return jsonify(result), status


@alliance_bp.post('/join')
def join_alliance():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    alliance_id = data.get('alliance_id')
    result = services.alliance_service.join_alliance(user_id, alliance_id)
    status = 200 if result.get('ok') else 400
    return jsonify(result), status

@alliance_bp.get('/my')
def get_my_alliance():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    result = services.alliance_service.get_my_alliance(user_id)
    # 处理 entity 到 dict 的转换（如果是 object 的话）
    if result["ok"]:
        alliance = result["alliance"]
        member_info = result["member_info"]
        return jsonify({
            "ok": True,
            "alliance": {
                "id": alliance.id,
                "name": alliance.name,
                "leader_id": alliance.leader_id,
                "level": alliance.level,
                "exp": alliance.exp,
                "funds": alliance.funds,
                "crystals": alliance.crystals,
                "prosperity": alliance.prosperity,
                "notice": alliance.notice,
            },
            "member_info": {
                "role": member_info.role,
                "contribution": member_info.contribution,
            },
            "member_count": result["member_count"],
            "member_capacity": result.get("member_capacity"),
            "fire_ore_claimed_today": bool(result.get("fire_ore_claimed_today", False)),
        })
    
    return jsonify(result)

@alliance_bp.get('/warehouse/donation-info')
def get_donation_info():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_donation_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/warehouse/donate')
def donate_resources():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    donations = data.get("donations") or {}
    result = services.alliance_service.donate_resources(user_id, donations)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/notice')
def get_alliance_notice():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_alliance_notice(user_id)
    return jsonify(result)

@alliance_bp.post('/notice')
def update_alliance_notice():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    notice = data.get("notice", "")

    result = services.alliance_service.update_alliance_notice(user_id, notice)
    return jsonify(result)

@alliance_bp.post('/rename')
def rename_alliance():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    new_name = data.get("name", "")

    result = services.alliance_service.rename_alliance(user_id, new_name)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/members')
def get_alliance_members():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    sort = request.args.get('sort', 'role')
    result = services.alliance_service.get_alliance_members_info(user_id, sort)
    return jsonify(result)

@alliance_bp.post('/members/role')
def update_member_role():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    target_user_id = data.get("target_user_id")
    role = data.get("role")

    if not target_user_id:
        return jsonify({"ok": False, "error": "缺少成员ID"}), 400

    result = services.alliance_service.update_member_role(user_id, int(target_user_id), int(role))
    return jsonify(result)

@alliance_bp.post('/members/kick')
def kick_member():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    target_user_id = data.get("target_user_id")
    if not target_user_id:
        return jsonify({"ok": False, "error": "缺少成员ID"}), 400

    result = services.alliance_service.kick_member(user_id, int(target_user_id))
    return jsonify(result)

@alliance_bp.post('/quit')
def quit_alliance():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.quit_alliance(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/talent')
def get_alliance_talent():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_alliance_talent_info(user_id)
    return jsonify(result)

@alliance_bp.post('/talent/learn')
def learn_alliance_talent():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    talent_key = (data.get("talent_key") or "").strip()
    if not talent_key:
        return jsonify({"ok": False, "error": "缺少天赋类型"}), 400

    result = services.alliance_service.learn_alliance_talent(user_id, talent_key)
    return jsonify(result)

@alliance_bp.post('/talent/research')
def research_alliance_talent():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    talent_key = (data.get("talent_key") or "").strip()
    if not talent_key:
        return jsonify({"ok": False, "error": "缺少天赋类型"}), 400

    result = services.alliance_service.research_alliance_talent(user_id, talent_key)
    return jsonify(result)

@alliance_bp.get('/beast-storage')
def get_beast_storage():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_beast_storage_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/beast-storage/store')
def store_beast_to_alliance():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    beast_id = data.get("beastId")
    try:
        beast_id = int(beast_id)
    except (TypeError, ValueError):
        beast_id = None

    result = services.alliance_service.store_beast_in_alliance_storage(user_id, beast_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/beast-storage/retrieve')
def retrieve_beast_from_alliance():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    storage_id = data.get("storageId")
    try:
        storage_id = int(storage_id)
    except (TypeError, ValueError):
        storage_id = None

    result = services.alliance_service.retrieve_beast_from_alliance_storage(user_id, storage_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/item-storage')
def get_item_storage():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_item_storage_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/item-storage/deposit')
def deposit_item_to_storage():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    item_id = data.get("itemId")
    quantity = data.get("quantity")
    result = services.alliance_service.deposit_item_to_storage(user_id, item_id, quantity)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/item-storage/withdraw')
def withdraw_item_from_storage():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    storage_id = data.get("storageId")
    quantity = data.get("quantity")
    result = services.alliance_service.withdraw_item_from_storage(user_id, storage_id, quantity)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/training-ground')
def get_training_ground():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_training_ground_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/training-ground/rooms')
def create_training_room():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    title = data.get('title')
    try:
        duration_hours = int(data.get("duration_hours", 2) or 2)
    except (TypeError, ValueError):
        duration_hours = 2
    
    result = services.alliance_service.create_training_room(user_id, title, duration_hours)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/training-ground/rooms/join')
def join_training_room():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    room_id = data.get('roomId')
    try:
        room_id = int(room_id)
    except (TypeError, ValueError):
        room_id = None
    result = services.alliance_service.join_training_room(user_id, room_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/training-ground/end')
def end_training():
    """手动结束修行"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    room_id = data.get('roomId')
    try:
        room_id = int(room_id)
    except (TypeError, ValueError):
        room_id = None
    if not room_id:
        return jsonify({"ok": False, "error": "缺少房间ID"}), 400

    result = services.alliance_service.end_training(user_id, room_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/training-ground/claim')
def claim_training_reward():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    participant_id = data.get('participantId')
    try:
        participant_id = int(participant_id)
    except (TypeError, ValueError):
        participant_id = None
    result = services.alliance_service.claim_training_reward(user_id, participant_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/fire-ore/claim')
def claim_fire_ore():
    """领取火能原石（消耗5贡献）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.claim_fire_ore(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/competition')
def get_competition_info():
    """获取联盟争霸赛信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    try:
        result = services.competition_service.get_competition_info(user_id)
        status = 200 if result.get("ok") else 400
        return jsonify(result), status
    except Exception as e:
        # 记录错误但不中断服务
        import traceback
        print(f"获取联盟争霸赛信息失败: {e}")
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": f"获取争霸赛信息失败：{str(e)}"}), 500

@alliance_bp.post('/competition/register')
def register_competition():
    """联盟报名争霸赛"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    team_keys = data.get("team_keys", [])
    
    result = services.competition_service.register_alliance(user_id, team_keys)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/competition/signup')
def signup_competition():
    """成员签到"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    result = services.competition_service.signup_member(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/competition/team-ranking')
def get_team_ranking():
    """获取战队排行榜"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    zone = request.args.get('zone', 'calf_tiger')
    stage = request.args.get('stage', 'all')
    
    result = services.competition_service.get_team_rankings(zone, stage)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/competition/elite-ranking')
def get_elite_ranking():
    """获取精英排行榜"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    result = services.competition_service.get_elite_rankings(page, page_size)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/competition/alliance-ranking')
def get_alliance_ranking():
    """获取联盟积分排行"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    result = services.competition_service.get_alliance_prestige_rankings(user_id, page, page_size)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/competition/past-records')
def get_past_records():
    """获取往届战绩"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    session_key = request.args.get('session')
    
    result = services.competition_service.get_past_records(user_id, session_key)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/war/signup')
def signup_for_war():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.signup_for_war(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/war/target-signup')
def target_signup():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    target_id = data.get("target_id")
    army = data.get("army")
    try:
        target_id = int(target_id)
    except (TypeError, ValueError):
        target_id = None

    if not target_id:
        return jsonify({"ok": False, "error": "缺少或非法的 target_id"}), 400

    result = services.alliance_service.signup_target(user_id, target_id, army)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/barracks')
def get_alliance_barracks():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_alliance_barracks(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/war/info')
def get_war_info():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_war_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.get('/war/honor')
def get_war_honor_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_war_honor_status(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.post('/war/honor/exchange')
def exchange_war_honor():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    effect_key = (data.get("effectKey") or "").strip()

    result = services.alliance_service.exchange_war_honor(user_id, effect_key)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.post('/war/checkin')
def war_checkin():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.war_checkin(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/war/status')
def get_war_status():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_war_status(user_id)
    return jsonify(result)

@alliance_bp.get('/war/battle-records')
def get_war_battle_records():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    limit = request.args.get('limit', 50)
    result = services.alliance_service.get_war_battle_records(user_id, limit)
    return jsonify(result)

@alliance_bp.post('/war/honor/exchange-item')
def exchange_war_honor_item():
    """战功兑换物品（2战功=1焚火晶，4战功=1金袋）"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    data = request.get_json() or {}
    exchange_type = data.get("exchange_type")
    if not exchange_type:
        return jsonify({"ok": False, "error": "缺少兑换类型"}), 400

    result = services.alliance_service.exchange_war_honor_item(user_id, exchange_type)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/war/top3')
def get_top3_alliances():
    """获取盟战排行榜前三名（用于首页显示，无需登录）"""
    result = services.alliance_service.get_top3_alliances()
    return jsonify(result)

@alliance_bp.get('/war/ranking')
def get_war_ranking():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    try:
        page = int(request.args.get("page", 1))
    except (TypeError, ValueError):
        page = 1

    try:
        size = int(request.args.get("size", 10))
    except (TypeError, ValueError):
        size = 10

    size = max(1, min(50, size))

    try:
        result = services.alliance_service.get_war_ranking(user_id, page, size)
        status = 200 if result.get("ok") else 400
        return jsonify(result), status
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"排行榜加载失败: {str(e)}"}), 500


@alliance_bp.get('/war/live-feed')
def get_war_live_feed():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_war_live_feed(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.get('/war/targets')
def list_war_targets():
    """获取盟战土地列表及其占领联盟信息"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.list_war_lands()
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.get('/war/land/<int:land_id>')
def get_war_land_detail(land_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_land_detail(land_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.get('/war/battle-overview/<int:land_id>')
def get_battle_overview(land_id: int):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_battle_service.get_land_battle_overview(land_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.get('/war/round-duels')
def get_round_duels():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    round_id = request.args.get("round_id")
    battle_id = request.args.get("battle_id")
    round_no = request.args.get("round_no")

    try:
        round_id_int = int(round_id) if round_id is not None else None
    except (TypeError, ValueError):
        round_id_int = None

    try:
        battle_id_int = int(battle_id) if battle_id is not None else None
    except (TypeError, ValueError):
        battle_id_int = None

    try:
        round_no_int = int(round_no) if round_no is not None else None
    except (TypeError, ValueError):
        round_no_int = None

    result = services.alliance_battle_service.get_round_duels(
        round_id=round_id_int,
        battle_id=battle_id_int,
        round_no=round_no_int,
    )
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.post('/war/lock-and-pair/<int:land_id>')
def lock_and_pair_land(land_id: int):
    """配对联盟并创建对战（管理接口）
    
    将已确认报名的联盟进行配对，创建对战记录。
    需要至少2个联盟报名才能配对。
    
    时间检查：只在对战时间内（周三/周六 20:00-22:00）才能配对。
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    # 检查是否在对战时间内
    now = datetime.utcnow()
    is_war, phase, status = services.alliance_service._is_war_time(now)
    if not is_war or status != "battle":
        return jsonify({
            "ok": False,
            "error": f"当前不在对战时间内（对战时间：周三/周六 20:00-22:00），当前状态：{status}"
        }), 400
    
    result = services.alliance_battle_service.lock_and_pair_land(land_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.post('/war/advance-round/<int:battle_id>')
def advance_battle_round(battle_id: int):
    """推进对战回合（管理接口）
    
    执行当前回合的所有决斗，并推进到下一回合或结束战斗。
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    result = services.alliance_battle_service.advance_round(battle_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


@alliance_bp.post('/war/run-battle/<int:land_id>')
def run_land_battle(land_id: int):
    """执行土地对战完整流程（管理接口）
    
    自动执行：
    1. 配对联盟
    2. 执行所有对战的所有回合直到结束
    3. 最终胜利者自动占领土地
    
    时间检查：只在对战时间内（周三/周六 20:00-22:00）才能执行。
    允许通过环境变量 ALLIANCE_WAR_ALLOW_TIME_BYPASS=true 跳过时间检查（测试用）。
    """
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    # 检查是否在对战时间内（允许通过环境变量跳过）
    import os
    allow_bypass = os.getenv("ALLIANCE_WAR_ALLOW_TIME_BYPASS", "").lower() in ("1", "true", "yes")
    if not allow_bypass:
        now = datetime.utcnow()
        is_war, phase, status = services.alliance_service._is_war_time(now)
        if not is_war or status != "battle":
            return jsonify({
                "ok": False,
                "error": f"当前不在对战时间内（对战时间：周三/周六 20:00-22:00），当前状态：{status}。测试时可设置环境变量 ALLIANCE_WAR_ALLOW_TIME_BYPASS=true 跳过"
            }), 400
    
    # 1. 配对联盟
    pair_result = services.alliance_battle_service.lock_and_pair_land(land_id)
    if not pair_result.get("ok"):
        return jsonify(pair_result), 400
    
    battles = pair_result.get("battles", [])
    if not battles:
        return jsonify({
            "ok": True,
            "message": "没有可配对的对战",
            "battles": []
        }), 200
    
    # 2. 执行每场对战的所有回合
    battle_results = []
    for battle_info in battles:
        battle_id = battle_info["battle_id"]
        left_alliance_id = battle_info["left_alliance_id"]
        right_alliance_id = battle_info["right_alliance_id"]
        
        rounds_executed = 0
        battle_finished = False
        
        # 循环推进回合直到战斗结束
        while not battle_finished:
            advance_result = services.alliance_battle_service.advance_round(battle_id)
            if not advance_result.get("ok"):
                battle_results.append({
                    "battle_id": battle_id,
                    "left_alliance_id": left_alliance_id,
                    "right_alliance_id": right_alliance_id,
                    "status": "error",
                    "error": advance_result.get("error"),
                    "rounds_executed": rounds_executed
                })
                break
            
            rounds_executed += 1
            round_info = advance_result.get("round", {})
            
            if advance_result.get("battle_finished"):
                battle_finished = True
                battle_results.append({
                    "battle_id": battle_id,
                    "left_alliance_id": left_alliance_id,
                    "right_alliance_id": right_alliance_id,
                    "status": "finished",
                    "rounds_executed": rounds_executed,
                    "final_round": round_info
                })
    
    return jsonify({
        "ok": True,
        "message": f"成功执行 {len(battles)} 场对战",
        "pair_result": pair_result,
        "battle_results": battle_results
    }), 200


@alliance_bp.get('/chat/messages')
def get_chat_messages():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    result = services.alliance_service.get_chat_messages(user_id)
    return jsonify(result)

@alliance_bp.post('/chat/send')
def send_chat_message():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401
    
    data = request.get_json() or {}
    content = data.get("content", "").strip()
    
    result = services.alliance_service.send_chat_message(user_id, content)
    return jsonify(result)

@alliance_bp.get('/activities')
def get_alliance_activities():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    limit = request.args.get('limit')
    result = services.alliance_service.get_alliance_activities(user_id, limit)
    return jsonify(result)

@alliance_bp.get('/buildings')
def get_alliance_buildings():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_alliance_buildings_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/furnace/upgrade-info')
def get_furnace_upgrade_info():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_furnace_upgrade_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/council/upgrade')
def upgrade_council_hall():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.upgrade_council_hall(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/furnace/upgrade')
def upgrade_furnace():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.upgrade_furnace(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/talent/upgrade-info')
def get_talent_pool_upgrade_info():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_talent_pool_upgrade_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/talent/upgrade')
def upgrade_talent_pool():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.upgrade_talent_pool(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/beast/upgrade-info')
def get_beast_room_upgrade_info():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_beast_room_upgrade_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/beast/upgrade')
def upgrade_beast_room():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.upgrade_beast_room(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.get('/item-storage/upgrade-info')
def get_item_storage_upgrade_info():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.get_item_storage_upgrade_info(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status

@alliance_bp.post('/item-storage/upgrade')
def upgrade_item_storage():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"ok": False, "error": "请先登录"}), 401

    result = services.alliance_service.upgrade_item_storage(user_id)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status
