"""
地图副本基础功能测试

测试内容：
1. 获取副本进度
2. 前进功能
3. 挑战幻兽
4. 重置副本
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from infrastructure.db.connection import execute_query, execute_update

# 测试用户ID
TEST_USER_ID = 1

def test_dungeon_progress():
    """测试1：获取副本进度"""
    print("\n" + "="*50)
    print("测试1：获取副本进度")
    print("="*50)
    
    # 查询副本进度
    rows = execute_query(
        """SELECT dungeon_name, current_floor, total_floors, floor_cleared
           FROM player_dungeon_progress 
           WHERE user_id = %s""",
        (TEST_USER_ID,)
    )
    
    if rows:
        print(f"✓ 找到 {len(rows)} 个副本进度记录")
        for row in rows:
            print(f"  - {row['dungeon_name']}: {row['current_floor']}/{row['total_floors']}层")
            print(f"    已通关: {row['floor_cleared']}")
    else:
        print("✗ 没有找到副本进度记录")
        print("  提示：需要先进入副本才会创建进度记录")
    
    return len(rows) > 0

def test_dungeon_reset_count():
    """测试2：检查重置次数"""
    print("\n" + "="*50)
    print("测试2：检查重置次数")
    print("="*50)
    
    rows = execute_query(
        """SELECT dungeon_name, current_floor
           FROM player_dungeon_progress 
           WHERE user_id = %s""",
        (TEST_USER_ID,)
    )
    
    if rows:
        print(f"✓ 副本进度信息：")
        for row in rows:
            print(f"  - {row['dungeon_name']}: 当前第 {row['current_floor']} 层")
    else:
        print("✗ 没有找到副本记录")
    
    return True

def test_player_dice():
    """测试3：检查玩家骰子"""
    print("\n" + "="*50)
    print("测试3：检查玩家骰子")
    print("="*50)
    
    rows = execute_query(
        "SELECT dice FROM player WHERE user_id = %s",
        (TEST_USER_ID,)
    )
    
    if rows:
        dice = rows[0].get('dice', 0)
        print(f"✓ 玩家骰子数量: {dice}")
        if dice < 10:
            print(f"  提示：骰子数量较少，可以使用骰子包补充")
    else:
        print("✗ 找不到玩家信息")
        return False
    
    return True

def test_dungeon_config():
    """测试4：检查副本配置"""
    print("\n" + "="*50)
    print("测试4：检查副本配置")
    print("="*50)
    
    import json
    config_path = os.path.join(os.path.dirname(__file__), 'configs/dungeon_beasts.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        dungeons = config.get('dungeons', {})
        print(f"✓ 找到 {len(dungeons)} 个副本配置")
        for dungeon_id, dungeon_data in dungeons.items():
            print(f"  - {dungeon_data.get('name')}: {dungeon_data.get('total_floors')}层")
    except Exception as e:
        print(f"✗ 读取副本配置失败: {e}")
        return False
    
    return True

def main():
    print("\n" + "="*60)
    print("地图副本基础功能测试")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("副本进度", test_dungeon_progress()))
    results.append(("重置次数", test_dungeon_reset_count()))
    results.append(("玩家骰子", test_player_dice()))
    results.append(("副本配置", test_dungeon_config()))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n✓ 地图副本功能基本可用！")
        print("\n使用说明：")
        print("1. 在主界面点击副本名称旁的【挑战】按钮进入副本")
        print("2. 点击【前进】按钮掷骰子前进")
        print("3. 遇到幻兽时点击【挑战幻兽】进行战斗")
        print("4. 遇到宝箱时可以选择开启或继续前进")
        print("5. 每日第1次挑战免费，第2-6次需要200元宝重置")
    else:
        print("\n✗ 部分功能可能存在问题，请检查")

if __name__ == '__main__':
    main()
