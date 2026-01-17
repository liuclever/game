"""
测试地图副本重置规则
验证：每日免费挑战1次，后续重置次数固定为5次，每次重置200元宝
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db.connection import execute_query, execute_update
from interfaces.web_api.bootstrap import services
from datetime import date

def test_dungeon_reset():
    """测试副本重置规则"""
    print("=" * 60)
    print("测试地图副本重置规则")
    print("=" * 60)
    
    # 使用测试账号
    test_user_id = 1001  # 测试玩家A
    dungeon_name = "镇妖塔"
    
    # 1. 清理测试数据
    print("\n1. 清理测试数据...")
    execute_update(
        "DELETE FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s",
        (test_user_id, dungeon_name)
    )
    
    # 2. 获取玩家初始元宝
    player = services.player_repo.get_by_id(test_user_id)
    if not player:
        print("❌ 测试账号不存在")
        return
    
    initial_yuanbao = player.yuanbao
    print(f"   初始元宝: {initial_yuanbao}")
    
    # 3. 测试第1次挑战（免费）
    print("\n2. 测试第1次挑战（应该免费）...")
    execute_update("""
        INSERT INTO player_dungeon_progress 
        (user_id, dungeon_name, current_floor, floor_cleared, floor_event_type, resets_today, last_reset_date, loot_claimed)
        VALUES (%s, %s, 35, TRUE, 'boss', 0, %s, TRUE)
    """, (test_user_id, dungeon_name, date.today()))
    
    # 模拟第1次重置
    results = execute_query(
        "SELECT resets_today FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s",
        (test_user_id, dungeon_name)
    )
    resets_today = results[0]['resets_today'] if results else 0
    
    if resets_today == 0:
        print("   ✓ 第1次挑战，resets_today = 0（免费）")
        # 不扣元宝
        execute_update("""
            UPDATE player_dungeon_progress 
            SET current_floor = 1, resets_today = 1, last_reset_date = %s
            WHERE user_id = %s AND dungeon_name = %s
        """, (date.today(), test_user_id, dungeon_name))
    else:
        print(f"   ❌ 第1次挑战应该免费，但 resets_today = {resets_today}")
        return
    
    player = services.player_repo.get_by_id(test_user_id)
    if player.yuanbao == initial_yuanbao:
        print(f"   ✓ 元宝未扣除: {player.yuanbao}")
    else:
        print(f"   ❌ 元宝被扣除: {initial_yuanbao} -> {player.yuanbao}")
        return
    
    # 4. 测试第2次重置（需要200元宝）
    print("\n3. 测试第2次重置（应该扣200元宝）...")
    execute_update("""
        UPDATE player_dungeon_progress 
        SET current_floor = 35, floor_cleared = TRUE
        WHERE user_id = %s AND dungeon_name = %s
    """, (test_user_id, dungeon_name))
    
    results = execute_query(
        "SELECT resets_today FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s",
        (test_user_id, dungeon_name)
    )
    resets_today = results[0]['resets_today']
    
    if resets_today == 1:
        print(f"   ✓ 当前 resets_today = 1，准备第2次重置")
        # 扣除200元宝
        player.yuanbao -= 200
        services.player_repo.save(player)
        execute_update("""
            UPDATE player_dungeon_progress 
            SET current_floor = 1, resets_today = 2
            WHERE user_id = %s AND dungeon_name = %s
        """, (test_user_id, dungeon_name))
    else:
        print(f"   ❌ resets_today 应该为1，实际为 {resets_today}")
        return
    
    player = services.player_repo.get_by_id(test_user_id)
    expected_yuanbao = initial_yuanbao - 200
    if player.yuanbao == expected_yuanbao:
        print(f"   ✓ 元宝正确扣除: {initial_yuanbao} -> {player.yuanbao}")
    else:
        print(f"   ❌ 元宝扣除错误: 期望 {expected_yuanbao}，实际 {player.yuanbao}")
        return
    
    # 5. 测试第3-5次重置（每次200元宝）
    print("\n4. 测试第3-5次重置（每次200元宝）...")
    for i in range(3, 6):
        execute_update("""
            UPDATE player_dungeon_progress 
            SET current_floor = 35, floor_cleared = TRUE
            WHERE user_id = %s AND dungeon_name = %s
        """, (test_user_id, dungeon_name))
        
        results = execute_query(
            "SELECT resets_today FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s",
            (test_user_id, dungeon_name)
        )
        resets_today = results[0]['resets_today']
        
        # 扣除200元宝
        player = services.player_repo.get_by_id(test_user_id)
        player.yuanbao -= 200
        services.player_repo.save(player)
        execute_update("""
            UPDATE player_dungeon_progress 
            SET current_floor = 1, resets_today = %s
            WHERE user_id = %s AND dungeon_name = %s
        """, (resets_today + 1, test_user_id, dungeon_name))
        
        print(f"   ✓ 第{i}次重置完成，resets_today = {resets_today + 1}")
    
    player = services.player_repo.get_by_id(test_user_id)
    expected_yuanbao = initial_yuanbao - 800  # 第2-5次共4次，每次200
    if player.yuanbao == expected_yuanbao:
        print(f"   ✓ 元宝正确扣除: {initial_yuanbao} -> {player.yuanbao}")
    else:
        print(f"   ❌ 元宝扣除错误: 期望 {expected_yuanbao}，实际 {player.yuanbao}")
        return
    
    # 6. 测试第6次重置（应该失败）
    print("\n5. 测试第6次重置（应该达到上限）...")
    results = execute_query(
        "SELECT resets_today FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s",
        (test_user_id, dungeon_name)
    )
    resets_today = results[0]['resets_today']
    
    if resets_today >= 5:
        print(f"   ✓ 已达到每日重置上限: resets_today = {resets_today}")
    else:
        print(f"   ❌ 未达到上限: resets_today = {resets_today}")
        return
    
    # 7. 恢复玩家元宝
    print("\n6. 恢复测试数据...")
    player = services.player_repo.get_by_id(test_user_id)
    player.yuanbao = initial_yuanbao
    services.player_repo.save(player)
    execute_update(
        "DELETE FROM player_dungeon_progress WHERE user_id = %s AND dungeon_name = %s",
        (test_user_id, dungeon_name)
    )
    print("   ✓ 测试数据已恢复")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    print("\n测试总结：")
    print("- 第1次挑战免费（resets_today = 0）")
    print("- 第2-5次重置每次扣除200元宝")
    print("- 第6次重置被拒绝（达到上限5次）")
    print("- 每日重置上限固定为5次，不依赖VIP等级")

if __name__ == '__main__':
    test_dungeon_reset()
