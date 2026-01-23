"""测试连胜竞技场挑战没有出战幻兽的对手"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update

def test_no_beast_opponent():
    """测试挑战没有出战幻兽的对手"""
    
    print("=" * 80)
    print("测试连胜竞技场挑战没有出战幻兽的对手")
    print("=" * 80)
    print()
    
    # 1. 查找有出战幻兽的玩家
    print("【1. 查找测试玩家】")
    
    players_with_beasts = execute_query("""
        SELECT p.user_id, p.nickname, p.level, COUNT(pb.id) as beast_count
        FROM player p
        LEFT JOIN player_beast pb ON p.user_id = pb.user_id AND pb.is_in_team = 1
        WHERE p.level >= 30
        GROUP BY p.user_id
        HAVING beast_count > 0
        LIMIT 1
    """)
    
    if not players_with_beasts:
        print("✗ 未找到有出战幻兽的玩家")
        return
    
    attacker = players_with_beasts[0]
    print(f"挑战者：{attacker['nickname']} (ID: {attacker['user_id']}, 等级: {attacker['level']}, 幻兽数: {attacker['beast_count']})")
    print()
    
    # 2. 查找没有出战幻兽的玩家
    print("【2. 查找没有出战幻兽的对手】")
    
    players_without_beasts = execute_query("""
        SELECT p.user_id, p.nickname, p.level, COUNT(pb.id) as beast_count
        FROM player p
        LEFT JOIN player_beast pb ON p.user_id = pb.user_id AND pb.is_in_team = 1
        WHERE p.level >= 30 AND p.user_id != %s
        GROUP BY p.user_id
        HAVING beast_count = 0
        LIMIT 1
    """, (attacker['user_id'],))
    
    if not players_without_beasts:
        print("✗ 未找到没有出战幻兽的玩家")
        print("提示：可以手动创建一个测试账号，不设置出战幻兽")
        return
    
    defender = players_without_beasts[0]
    print(f"对手：{defender['nickname']} (ID: {defender['user_id']}, 等级: {defender['level']}, 幻兽数: {defender['beast_count']})")
    print()
    
    # 3. 显示预期行为
    print("【3. 预期行为】")
    print()
    print("修改前：")
    print("  - 返回错误：'对方没有出战幻兽，无法切磋'")
    print("  - 无法进行战斗")
    print("  - 浪费玩家的时间")
    print()
    print("修改后：")
    print("  - 允许挑战")
    print("  - 对手视为弃权，挑战者自动获胜")
    print("  - 消耗活力（100或15点）")
    print("  - 连胜次数+1")
    print("  - 战斗记录显示：'对手没有出战幻兽，不战而胜'")
    print()
    
    # 4. 显示测试步骤
    print("【4. 手动测试步骤】")
    print()
    print(f"1. 登录挑战者账号（ID: {attacker['user_id']}）")
    print("2. 进入连胜竞技场")
    print("3. 刷新对手列表，直到出现没有出战幻兽的对手")
    print(f"4. 挑战对手（ID: {defender['user_id']}）")
    print("5. 观察结果：")
    print("   - 应该显示：'对手没有出战幻兽，自动获胜！当前连胜X次'")
    print("   - 连胜次数应该+1")
    print("   - 活力应该减少（100或15点）")
    print()
    
    # 5. 显示数据库验证
    print("【5. 数据库验证】")
    print()
    print("验证连胜记录：")
    print(f"  SELECT current_streak, max_streak_today, total_battles_today")
    print(f"  FROM arena_streak")
    print(f"  WHERE user_id = {attacker['user_id']} AND record_date = CURDATE();")
    print()
    print("验证活力消耗：")
    print(f"  SELECT energy FROM player WHERE user_id = {attacker['user_id']};")
    print()
    
    print("=" * 80)
    print("测试说明完成")
    print("=" * 80)
    print()
    
    # 6. 显示代码改动
    print("【6. 代码改动说明】")
    print()
    print("文件：interfaces/routes/arena_streak_routes.py")
    print()
    print("修改前：")
    print("  if not defender_beasts:")
    print("      return jsonify({'ok': False, 'error': '对方没有出战幻兽，无法切磋'})")
    print()
    print("修改后：")
    print("  if not defender_beasts:")
    print("      # 对手没有幻兽，挑战者自动获胜")
    print("      # 扣除活力、增加连胜、返回胜利结果")
    print()
    print("=" * 80)


if __name__ == "__main__":
    test_no_beast_opponent()
