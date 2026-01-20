"""检查召唤之王挑战赛报名状态"""
from infrastructure.db.connection import execute_query, execute_update

def check_registration_status():
    """检查所有玩家的报名状态"""
    print("=== 召唤之王挑战赛报名状态检查 ===\n")
    
    # 查询所有玩家的排名和报名状态
    rows = execute_query("""
        SELECT 
            k.user_id,
            p.nickname,
            k.area_index,
            k.rank_position,
            k.is_registered,
            k.today_challenges,
            k.win_streak,
            k.total_wins,
            k.total_losses
        FROM king_challenge_rank k
        JOIN player p ON k.user_id = p.user_id
        ORDER BY k.area_index, k.rank_position
        LIMIT 20
    """)
    
    if not rows:
        print("没有找到任何挑战赛记录")
        return
    
    print(f"找到 {len(rows)} 条记录:\n")
    
    area_1_players = [r for r in rows if r['area_index'] == 1]
    area_2_players = [r for r in rows if r['area_index'] == 2]
    
    print("【1赛区】")
    for r in area_1_players:
        reg_status = "✓已报名" if r['is_registered'] else "✗未报名"
        print(f"  排名{r['rank_position']:2d} | {r['nickname']:10s} | {reg_status} | "
              f"今日{r['today_challenges']}/15 | 连胜{r['win_streak']} | "
              f"战绩{r['total_wins']}胜{r['total_losses']}负")
    
    print("\n【2赛区】")
    for r in area_2_players:
        reg_status = "✓已报名" if r['is_registered'] else "✗未报名"
        print(f"  排名{r['rank_position']:2d} | {r['nickname']:10s} | {reg_status} | "
              f"今日{r['today_challenges']}/15 | 连胜{r['win_streak']} | "
              f"战绩{r['total_wins']}胜{r['total_losses']}负")
    
    # 统计
    total_registered = sum(1 for r in rows if r['is_registered'])
    print(f"\n总计: {len(rows)} 人参赛，{total_registered} 人已报名，{len(rows) - total_registered} 人未报名")

def check_player_beasts():
    """检查玩家的出战幻兽情况"""
    print("\n=== 玩家出战幻兽检查 ===\n")
    
    # 先获取挑战赛玩家ID
    player_ids = execute_query("""
        SELECT user_id FROM king_challenge_rank LIMIT 10
    """)
    
    if not player_ids:
        print("没有找到挑战赛玩家")
        return
    
    ids = [str(p['user_id']) for p in player_ids]
    ids_str = ','.join(ids)
    
    rows = execute_query(f"""
        SELECT 
            p.user_id,
            p.nickname,
            COUNT(pb.id) as beast_count
        FROM player p
        LEFT JOIN player_beast pb ON p.user_id = pb.user_id AND pb.is_in_team = 1
        WHERE p.user_id IN ({ids_str})
        GROUP BY p.user_id, p.nickname
        ORDER BY beast_count
    """)
    
    if not rows:
        print("没有找到玩家数据")
        return
    
    print(f"找到 {len(rows)} 个玩家:\n")
    
    for r in rows:
        beast_status = f"{r['beast_count']} 只幻兽" if r['beast_count'] > 0 else "⚠ 无出战幻兽"
        print(f"  {r['nickname']:10s} | {beast_status}")
    
    no_beast_count = sum(1 for r in rows if r['beast_count'] == 0)
    print(f"\n总计: {len(rows)} 人，{no_beast_count} 人没有出战幻兽")

def set_all_registered():
    """将所有玩家设置为已报名（测试用）"""
    print("\n=== 设置所有玩家为已报名 ===\n")
    
    result = execute_update("""
        UPDATE king_challenge_rank 
        SET is_registered = 1
    """)
    
    print(f"✓ 已将所有玩家设置为已报名")
    
    # 验证
    rows = execute_query("""
        SELECT COUNT(*) as total, 
               SUM(is_registered) as registered
        FROM king_challenge_rank
    """)
    
    if rows:
        print(f"  总人数: {rows[0]['total']}")
        print(f"  已报名: {rows[0]['registered']}")

def reset_all_registration():
    """重置所有玩家的报名状态（测试用）"""
    print("\n=== 重置所有玩家报名状态 ===\n")
    
    result = execute_update("""
        UPDATE king_challenge_rank 
        SET is_registered = 0
    """)
    
    print(f"✓ 已重置所有玩家的报名状态")
    
    # 验证
    rows = execute_query("""
        SELECT COUNT(*) as total, 
               SUM(is_registered) as registered
        FROM king_challenge_rank
    """)
    
    if rows:
        print(f"  总人数: {rows[0]['total']}")
        print(f"  已报名: {rows[0]['registered'] or 0}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "set-all":
            set_all_registered()
        elif command == "reset-all":
            reset_all_registration()
        else:
            print(f"未知命令: {command}")
            print("可用命令: set-all, reset-all")
    else:
        check_registration_status()
        check_player_beasts()
        
        print("\n提示:")
        print("  python check_king_registration.py set-all    # 设置所有人已报名")
        print("  python check_king_registration.py reset-all  # 重置所有人报名状态")
