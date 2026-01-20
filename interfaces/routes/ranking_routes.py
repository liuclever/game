# interfaces/routes/ranking_routes.py
"""排行榜路由"""

from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, session
from infrastructure.db.connection import execute_query

ranking_bp = Blueprint('ranking', __name__, url_prefix='/api/ranking')


def get_current_user_id() -> int:
    return session.get('user_id', 0)


# 等级阶段配置
LEVEL_RANKS = [
    (1, 19, '见习', False),
    (20, 29, '黄阶', True),
    (30, 39, '玄阶', True),
    (40, 49, '地阶', True),
    (50, 59, '天阶', True),
    (60, 69, '飞马', True),
    (70, 79, '天龙', True),
    (80, 100, '战神', True),
]


def get_player_rank(level):
    for min_lv, max_lv, rank_name, can_arena in LEVEL_RANKS:
        if min_lv <= level <= max_lv:
            return rank_name, can_arena
    return '见习', False


def _normalize_rank_name(name: str) -> str:
    """兼容前端展示名/历史名（修复：北斗/战神）。"""
    s = str(name or "").strip()
    if s == "北斗":
        return "战神"
    return s


@ranking_bp.get("/list")
def get_ranking_list():
    """获取排行榜"""
    user_id = get_current_user_id()
    ranking_type = request.args.get('type', 'level')
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)

    # 仅允许这四类排行（按需求收敛功能，避免接口被滥用）
    allow_types = {'level', 'power', 'arena', 'vip'}
    if ranking_type not in allow_types:
        ranking_type = 'level'

    # 二级筛选参数（用于“战力段位筛选/竞技擂台参与者战力排行”“擂台英豪榜周/总&赛区/全部”）
    filter_rank = request.args.get("rank")  # 段位/赛区名：黄阶/玄阶/地阶/天阶/飞马/天龙/战神
    arena_scope = request.args.get("scope", "zone")  # zone|all
    arena_time = request.args.get("time", "total")  # week|total
    power_scope = request.args.get("power_scope", "total")  # total|arena
    
    offset = (page - 1) * size
    rows = []
    total = 0
    my_rank = None
    arena_rank_name = ""
    arena_zones = [
        {"name": rank_name, "min_level": min_lv, "max_level": max_lv}
        for (min_lv, max_lv, rank_name, can_arena) in LEVEL_RANKS
        if can_arena
    ]
    
    if ranking_type == 'level':
        sql = """
            SELECT user_id as userId, nickname, level, prestige, vip_level as vipLevel
            FROM player
            ORDER BY level DESC, prestige DESC, exp DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query("SELECT COUNT(*) as total FROM player")
        total = total_rows[0]['total'] if total_rows else 0
        
        if user_id:
            rank_rows = execute_query(
                """
                SELECT COUNT(*) + 1 as `rank`
                FROM player p1
                WHERE p1.level > (SELECT level FROM player WHERE user_id = %s)
                   OR (
                        p1.level = (SELECT level FROM player WHERE user_id = %s)
                        AND COALESCE(p1.prestige, 0) > (SELECT COALESCE(prestige, 0) FROM player WHERE user_id = %s)
                      )
                """,
                (user_id, user_id, user_id),
            )
            my_rank = rank_rows[0]['rank'] if rank_rows else None
    
    elif ranking_type == 'power':
        # 战力：取出战队伍的总战力（与游戏内“出战战力”概念一致）
        tier = None
        if filter_rank:
            filter_rank = _normalize_rank_name(filter_rank)
            # rank -> level range
            for (min_lv, max_lv, rank_name, can_arena) in LEVEL_RANKS:
                if str(rank_name) == str(filter_rank):
                    tier = (int(min_lv), int(max_lv))
                    break

            # 如果传了 rank 但不认识：不要回落到“总排行”，直接返回空（避免出现“我在所有段位都有排名”的错觉）
            if tier is None:
                return jsonify({
                    "ok": True,
                    "rankings": [],
                    "total": 0,
                    "totalPages": 1,
                    "page": page,
                    "myRank": 0,
                    "arenaZones": arena_zones,
                    "arenaRankName": "",
                })

        # 竞技擂台参与者：只统计参加过擂台战斗（arena_battle_log 有记录）的玩家
        where_parts = []
        params = []
        if tier:
            where_parts.append("p.level BETWEEN %s AND %s")
            params.extend([tier[0], tier[1]])
        if str(power_scope) == "arena":
            where_parts.append(
                """p.user_id IN (
                    SELECT challenger_id FROM arena_battle_log
                    UNION
                    SELECT champion_id FROM arena_battle_log
                )"""
            )

        where_sql = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
        sql = f"""
            SELECT p.user_id as userId, p.nickname, p.level, p.vip_level as vipLevel,
                   COALESCE(SUM(b.combat_power), 0) as power
            FROM player p
            LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
            {where_sql}
            GROUP BY p.user_id, p.nickname, p.level, p.vip_level
            ORDER BY power DESC, p.level DESC
            LIMIT %s OFFSET %s
        """
        params.extend([size, offset])
        rows = execute_query(sql, tuple(params))

        if where_parts:
            count_sql = f"SELECT COUNT(*) as total FROM player p {where_sql}"
            total_rows = execute_query(count_sql, tuple(params[:-2]))
        else:
            total_rows = execute_query("SELECT COUNT(*) as total FROM player")
        total = total_rows[0]['total'] if total_rows else 0

        if user_id:
            my_power_rows = execute_query(
                "SELECT COALESCE(SUM(combat_power), 0) as power FROM player_beast WHERE user_id = %s AND is_in_team = 1",
                (user_id,),
            )
            my_power = int(my_power_rows[0].get("power", 0) or 0) if my_power_rows else 0

            if tier or str(power_scope) == "arena":
                rank_rows = execute_query(
                    f"""
                    SELECT COUNT(*) + 1 as `rank` FROM (
                      SELECT p.user_id, COALESCE(SUM(b.combat_power), 0) as power
                      FROM player p
                      LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
                      {where_sql}
                      GROUP BY p.user_id
                    ) t
                    WHERE t.power > %s
                    """,
                    tuple(list(params[:-2]) + [my_power]),
                )
            else:
                rank_rows = execute_query(
                    """
                    SELECT COUNT(*) + 1 as `rank` FROM (
                      SELECT p.user_id, COALESCE(SUM(b.combat_power), 0) as power
                      FROM player p
                      LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
                      GROUP BY p.user_id
                    ) t
                    WHERE t.power > %s
                    """,
                    (my_power,),
                )
            my_rank = rank_rows[0]['rank'] if rank_rows else None
    
    elif ranking_type == 'arena':
        # 擂台英豪榜：总榜/周榜都从 arena_battle_log 查询，区别只是时间范围
        # - 总英豪榜：所有历史记录
        # - 周英豪榜：近7天记录
        if not filter_rank and user_id:
            level_rows = execute_query("SELECT level FROM player WHERE user_id = %s", (user_id,))
            level_val = level_rows[0]['level'] if level_rows else 1
            filter_rank, _ = get_player_rank(level_val)

        if not filter_rank:
            rows = []
            total = 0
        else:
            arena_rank_name = str(filter_rank)
            params = []
            where_parts = []
            
            # 赛区筛选（黄阶条件）
            where_parts.append("l.rank_name = %s")
            params.append(filter_rank)
            
            # 周榜加时间限制
            if str(arena_time) == "week":
                since = datetime.now() - timedelta(days=7)
                where_parts.append("l.created_at >= %s")
                params.append(since)

            where_sql = "WHERE " + " AND ".join(where_parts)

            sql = f"""
                SELECT l.champion_id as userId, p.nickname, p.level, p.vip_level as vipLevel,
                       SUM(CASE WHEN l.is_challenger_win = 0 THEN 1 ELSE 0 END) as successCount,
                       %s as rankName
                FROM arena_battle_log l
                JOIN player p ON l.champion_id = p.user_id
                {where_sql}
                GROUP BY l.champion_id, p.nickname, p.level, p.vip_level
                ORDER BY successCount DESC
                LIMIT %s OFFSET %s
            """
            params_for_list = [filter_rank] + params + [size, offset]
            rows = execute_query(sql, tuple(params_for_list))

            # total（注意：COUNT DISTINCT champion_id）
            count_sql = f"SELECT COUNT(DISTINCT l.champion_id) as total FROM arena_battle_log l {where_sql}"
            total_rows = execute_query(count_sql, tuple(params))
            total = total_rows[0]['total'] if total_rows else 0

            if user_id:
                # 我的守擂成功次数（同条件）
                my_where = list(where_parts)
                my_params = list(params)
                my_where.append("l.champion_id = %s")
                my_params.append(user_id)
                my_where_sql = "WHERE " + " AND ".join(my_where)
                my_cnt_rows = execute_query(
                    f"SELECT SUM(CASE WHEN l.is_challenger_win = 0 THEN 1 ELSE 0 END) as cnt FROM arena_battle_log l {my_where_sql}",
                    tuple(my_params),
                )
                my_cnt = int(my_cnt_rows[0].get("cnt", 0) or 0) if my_cnt_rows else 0
                if my_cnt <= 0:
                    my_rank = None
                else:
                    rank_rows = execute_query(
                        f"""
                        SELECT COUNT(*) + 1 as `rank` FROM (
                          SELECT l.champion_id, SUM(CASE WHEN l.is_challenger_win = 0 THEN 1 ELSE 0 END) as successCount
                          FROM arena_battle_log l
                          {where_sql}
                          GROUP BY l.champion_id
                        ) t
                        WHERE t.successCount > %s
                        """,
                        tuple(list(params) + [my_cnt]),
                    )
                    my_rank = rank_rows[0]['rank'] if rank_rows else None

    elif ranking_type == 'vip':
        # VIP排行：只显示VIP玩家（vip_level > 0）
        sql = """
            SELECT user_id as userId, nickname, vip_level as vipLevel, level
            FROM player
            WHERE vip_level > 0
            ORDER BY vip_level DESC, level DESC, exp DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query("SELECT COUNT(*) as total FROM player WHERE vip_level > 0")
        total = total_rows[0]['total'] if total_rows else 0

        if user_id:
            my_rows = execute_query("SELECT vip_level, level, exp FROM player WHERE user_id = %s", (user_id,))
            if my_rows:
                my_vip = int(my_rows[0].get("vip_level", 0) or 0)
                my_lv = int(my_rows[0].get("level", 0) or 0)
                my_exp = int(my_rows[0].get("exp", 0) or 0)
                # 如果不是VIP，不上榜
                if my_vip <= 0:
                    my_rank = None
                else:
                    rank_rows = execute_query(
                        """
                        SELECT COUNT(*) + 1 as `rank`
                        FROM player p1
                        WHERE p1.vip_level > 0 AND (
                            p1.vip_level > %s
                            OR (p1.vip_level = %s AND p1.level > %s)
                            OR (p1.vip_level = %s AND p1.level = %s AND p1.exp > %s)
                        )
                        """,
                        (my_vip, my_vip, my_lv, my_vip, my_lv, my_exp),
                    )
                    my_rank = rank_rows[0]['rank'] if rank_rows else None

    # 补充 rank 字段（用于前端展示）
    rankings = []
    for idx, r in enumerate(rows or []):
        obj = dict(r)
        obj["rank"] = int(offset + idx + 1)
        rankings.append(obj)

    # totalPages
    try:
        total_pages = int((int(total) + int(size) - 1) / int(size)) if int(size) > 0 else 1
    except Exception:
        total_pages = 1
    total_pages = max(1, total_pages)
    
    return jsonify({
        "ok": True,
        "type": ranking_type,
        # 兼容旧字段 + 对齐前端字段
        "list": rankings,
        "rankings": rankings,
        "total": total,
        "totalPages": total_pages,
        "page": page,
        "size": size,
        "myRank": my_rank,
        "arenaRankName": arena_rank_name,
        "arenaZones": arena_zones,
    })
