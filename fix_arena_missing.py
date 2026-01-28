"""修复擂台不存在的问题"""
import sys
sys.path.insert(0, '.')

from infrastructure.db.player_repo_mysql import execute_query, execute_update

def check_and_fix_arena():
    """检查并修复擂台数据"""
    
    # 检查擂台表是否有数据
    sql = "SELECT COUNT(*) as count FROM arena"
    result = execute_query(sql)
    count = result[0]['count'] if result else 0
    
    print(f"当前擂台表中有 {count} 条记录")
    
    if count == 0:
        print("\n擂台表为空，开始初始化...")
        
        # 初始化各等级阶段的擂台（普通场和黄金场）
        ranks = ['黄阶', '玄阶', '地阶', '天阶', '飞马', '天龙', '战神']
        types = ['normal', 'gold']
        
        insert_sql = """
            INSERT IGNORE INTO arena (rank_name, arena_type, consecutive_wins, prize_pool) 
            VALUES (%s, %s, 0, 0)
        """
        
        total = 0
        for rank in ranks:
            for arena_type in types:
                affected = execute_update(insert_sql, (rank, arena_type))
                if affected > 0:
                    print(f"  ✓ 创建擂台：{rank} - {arena_type}")
                    total += 1
        
        print(f"\n初始化完成！共创建了 {total} 个擂台")
    else:
        print("\n擂台数据正常")
        
        # 显示所有擂台
        arenas = execute_query("SELECT rank_name, arena_type, champion_nickname, consecutive_wins FROM arena ORDER BY id")
        print("\n当前擂台列表：")
        print("-" * 70)
        for arena in arenas:
            champion = arena['champion_nickname'] or '空置'
            wins = arena['consecutive_wins']
            print(f"{arena['rank_name']:6s} - {arena['arena_type']:6s} | 擂主: {champion:10s} | 连胜: {wins}")
        print("-" * 70)

if __name__ == '__main__':
    check_and_fix_arena()
