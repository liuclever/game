# interfaces/routes/ranking_routes.py
"""排行榜路由"""

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


@ranking_bp.get("/list")
def get_ranking_list():
    """获取排行榜"""
    user_id = get_current_user_id()
    ranking_type = request.args.get('type', 'level')
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)
    
    offset = (page - 1) * size
    rows = []
    total = 0
    my_rank = None
    
    if ranking_type == 'level':
        sql = """
            SELECT user_id as userId, nickname, level, exp
            FROM player
            ORDER BY level DESC, exp DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query("SELECT COUNT(*) as total FROM player")
        total = total_rows[0]['total'] if total_rows else 0
        
        if user_id:
            rank_rows = execute_query(
                """SELECT COUNT(*) + 1 as `rank` FROM player p1
                   WHERE p1.level > (SELECT level FROM player WHERE user_id = %s)
                   OR (p1.level = (SELECT level FROM player WHERE user_id = %s) 
                       AND p1.exp > (SELECT exp FROM player WHERE user_id = %s))""",
                (user_id, user_id, user_id)
            )
            my_rank = rank_rows[0]['rank'] if rank_rows else None
    
    elif ranking_type == 'power':
        sql = """
            SELECT p.user_id as userId, p.nickname, p.level,
                   COALESCE(SUM(b.combat_power), 0) as power
            FROM player p
            LEFT JOIN player_beast b ON p.user_id = b.user_id AND b.is_in_team = 1
            GROUP BY p.user_id, p.nickname, p.level
            ORDER BY power DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query("SELECT COUNT(*) as total FROM player")
        total = total_rows[0]['total'] if total_rows else 0
    
    elif ranking_type == 'arena':
        filter_rank = request.args.get('rank')
        if not filter_rank and user_id:
            level_rows = execute_query("SELECT level FROM player WHERE user_id = %s", (user_id,))
            level_val = level_rows[0]['level'] if level_rows else 1
            filter_rank, _ = get_player_rank(level_val)

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
        
        total = total_rows[0]['total'] if total_rows else 0
    
    elif ranking_type == 'tower':
        sql = """
            SELECT p.user_id as userId, p.nickname, p.level, t.max_floor_record as maxFloor
            FROM player p
            JOIN tower_state t ON p.user_id = t.user_id AND t.tower_type = 'tongtian'
            ORDER BY t.max_floor_record DESC
            LIMIT %s OFFSET %s
        """
        rows = execute_query(sql, (size, offset))
        total_rows = execute_query(
            "SELECT COUNT(*) as total FROM tower_state WHERE tower_type = 'tongtian'"
        )
        total = total_rows[0]['total'] if total_rows else 0
    
    return jsonify({
        "ok": True,
        "type": ranking_type,
        "list": rows,
        "total": total,
        "page": page,
        "size": size,
        "myRank": my_rank,
    })
