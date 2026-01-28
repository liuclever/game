"""修复铜钱为负数的账号"""
import sys
sys.path.insert(0, '.')

from infrastructure.db.player_repo_mysql import execute_query, execute_update

def fix_negative_gold():
    """将所有负数铜钱的账号重置为0"""
    
    # 查询所有铜钱为负数的玩家
    sql = "SELECT user_id, username, gold FROM player WHERE gold < 0"
    players = execute_query(sql)
    
    if not players:
        print("没有发现铜钱为负数的账号")
        return
    
    print(f"发现 {len(players)} 个铜钱为负数的账号：")
    print("-" * 60)
    for p in players:
        print(f"用户ID: {p['user_id']}, 用户名: {p.get('username', 'N/A')}, 铜钱: {p['gold']}")
    print("-" * 60)
    
    # 询问是否修复
    confirm = input("\n是否将这些账号的铜钱重置为0？(y/n): ")
    if confirm.lower() != 'y':
        print("已取消操作")
        return
    
    # 修复
    update_sql = "UPDATE player SET gold = 0 WHERE gold < 0"
    affected = execute_update(update_sql)
    
    print(f"\n修复完成！共修复了 {affected} 个账号")

if __name__ == '__main__':
    fix_negative_gold()
