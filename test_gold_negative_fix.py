"""测试铜钱负数问题修复

验证 update_gold 函数在扣钱时会检查余额，防止铜钱变成负数
"""

from infrastructure.db.player_repo_mysql import update_gold
from infrastructure.db.connection import execute_query, execute_update


def test_update_gold_with_insufficient_balance():
    """测试余额不足时扣钱会失败"""
    print("=" * 60)
    print("测试铜钱负数问题修复")
    print("=" * 60)
    
    # 创建测试用户
    test_user_id = 999999
    
    # 清理测试数据
    execute_update("DELETE FROM player WHERE user_id = %s", (test_user_id,))
    
    # 创建测试玩家，初始铜钱 10000
    execute_update(
        """
        INSERT INTO player (user_id, username, gold, level)
        VALUES (%s, 'test_user', 10000, 1)
        """,
        (test_user_id,)
    )
    
    print("\n【测试1：正常扣钱】")
    print("初始铜钱: 10000")
    print("扣除: 5000")
    
    success = update_gold(test_user_id, -5000)
    
    rows = execute_query("SELECT gold FROM player WHERE user_id = %s", (test_user_id,))
    current_gold = rows[0]['gold'] if rows else 0
    
    print(f"扣钱结果: {'成功' if success else '失败'}")
    print(f"当前铜钱: {current_gold}")
    print(f"✓ 正确" if success and current_gold == 5000 else f"✗ 错误")
    
    print("\n【测试2：余额不足时扣钱】")
    print("当前铜钱: 5000")
    print("尝试扣除: 8000")
    
    success = update_gold(test_user_id, -8000)
    
    rows = execute_query("SELECT gold FROM player WHERE user_id = %s", (test_user_id,))
    current_gold = rows[0]['gold'] if rows else 0
    
    print(f"扣钱结果: {'成功' if success else '失败'}")
    print(f"当前铜钱: {current_gold}")
    print(f"✓ 正确（扣钱失败，铜钱未变）" if not success and current_gold == 5000 else f"✗ 错误（铜钱变成了 {current_gold}）")
    
    print("\n【测试3：加钱】")
    print("当前铜钱: 5000")
    print("增加: 3000")
    
    success = update_gold(test_user_id, 3000)
    
    rows = execute_query("SELECT gold FROM player WHERE user_id = %s", (test_user_id,))
    current_gold = rows[0]['gold'] if rows else 0
    
    print(f"加钱结果: {'成功' if success else '失败'}")
    print(f"当前铜钱: {current_gold}")
    print(f"✓ 正确" if success and current_gold == 8000 else f"✗ 错误")
    
    print("\n【测试4：恰好扣完】")
    print("当前铜钱: 8000")
    print("扣除: 8000")
    
    success = update_gold(test_user_id, -8000)
    
    rows = execute_query("SELECT gold FROM player WHERE user_id = %s", (test_user_id,))
    current_gold = rows[0]['gold'] if rows else 0
    
    print(f"扣钱结果: {'成功' if success else '失败'}")
    print(f"当前铜钱: {current_gold}")
    print(f"✓ 正确" if success and current_gold == 0 else f"✗ 错误")
    
    print("\n【测试5：铜钱为0时扣钱】")
    print("当前铜钱: 0")
    print("尝试扣除: 1")
    
    success = update_gold(test_user_id, -1)
    
    rows = execute_query("SELECT gold FROM player WHERE user_id = %s", (test_user_id,))
    current_gold = rows[0]['gold'] if rows else 0
    
    print(f"扣钱结果: {'成功' if success else '失败'}")
    print(f"当前铜钱: {current_gold}")
    print(f"✓ 正确（扣钱失败，铜钱保持为0）" if not success and current_gold == 0 else f"✗ 错误（铜钱变成了 {current_gold}）")
    
    # 清理测试数据
    execute_update("DELETE FROM player WHERE user_id = %s", (test_user_id,))
    
    print("\n" + "=" * 60)
    print("✓ 所有测试完成")
    print("=" * 60)
    print("\n修复说明：")
    print("- update_gold 函数现在会在扣钱时检查余额")
    print("- 如果余额不足，扣钱操作会失败并返回 False")
    print("- 这样可以防止铜钱变成负数")
    print("- 一键猎魂会检查返回值，扣钱失败时会停止")


if __name__ == "__main__":
    test_update_gold_with_insufficient_balance()
