from pathlib import Path

path = Path(r"D:\project\plublic-work\December\game\interfaces\routes\arena_routes.py")
text = path.read_text(encoding="utf-8")

marker = '''            return jsonify({
                "ok": True,
                "win": False,
                "message": f"挑战失败！{champion_nickname}成功守擂，当前连胜{new_wins}场！",
                "battleId": battle_id,
            })'''

idx = text.index(marker)
end = idx + len(marker)

before = text[:end]

NEW = '''

@arena_bp.get("/battle/<int:battle_id>")
def get_arena_battle_detail(battle_id: int):
    """获取擂台战斗详情（用于详细战报页面）"""
    log = ARENA_BATTLE_REPO.get_by_id(battle_id)
    if not log:
        return jsonify({"ok": False, "error": "战报不存在"}), 404
    return jsonify({"ok": True, "battle": log.to_dict()})


@arena_bp.get("/dynamics")
def get_arena_dynamics():
    """获取擂台动态（全服 / 个人）。"""
    user_id = get_current_user_id()
    dynamic_type = request.args.get("type", "arena")  # arena | personal
    arena_type = request.args.get("arena_type", None)
    limit = int(request.args.get("limit", 20))

    if dynamic_type == "personal" and user_id:
        logs = ARENA_BATTLE_REPO.get_user_battles(user_id, limit)
    else:
        logs = ARENA_BATTLE_REPO.get_recent_battles(arena_type=arena_type, limit=limit)

    dynamics = []
    for log in logs:
        time_str = log.created_at.strftime("%Y年%m月%d日 %H:%M") if log.created_at else ""
        type_name = "普通场" if log.arena_type == "normal" else "黄金场"

        # 个人动态中，如果当前玩家是擂主，则把 ta 放在前面展示
        if dynamic_type == "personal" and user_id == log.champion_id:
            player_name = log.champion_name
            player_id = log.champion_id
            opponent_name = log.challenger_name
            opponent_id = log.challenger_id
            if log.is_challenger_win:
                action_text = f"在{type_name}被挑战失败"
            else:
                action_text = f"在{type_name}成功守擂"
        else:
            # 默认视角：挑战者在前
            player_name = log.challenger_name
            player_id = log.challenger_id
            opponent_name = log.champion_name
            opponent_id = log.champion_id
            action_text = f"在{type_name}{'战胜' if log.is_challenger_win else '惜败'}"

        dynamics.append({
            "id": log.id,
            "time": time_str,
            "player": player_name,
            "playerId": player_id,
            "opponent": opponent_name,
            "opponentId": opponent_id,
            "action": action_text,
            "extra": "",
            "hasDetail": True,
        })

    return jsonify({"ok": True, "dynamics": dynamics})
'''

path.write_text(before + NEW, encoding="utf-8")
