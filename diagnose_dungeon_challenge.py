"""诊断地图副本挑战功能问题

运行方式：
    python diagnose_dungeon_challenge.py

功能：
    - 检查玩家是否有出战幻兽
    - 检查副本配置是否正确
    - 检查副本进度表是否存在
    - 提供修复建议
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from infrastructure.db.connection import execute_query, execute_update


def check_player_team_beasts(user_id: int):
    """检查玩家是否有出战幻兽"""
    print(f"\n检查玩家 {user_id} 的出战幻兽...")
    
    beasts = execute_query(
        """
        SELECT id, name, level, is_in_team, realm
        FROM player_beasts
        WHERE user_id = %s AND is_in_team = 1
        ORDER BY id
        """,
        (user_id,)
    )
    
    if not beasts:
        print("❌ 玩家没有出战幻兽！")
        print("\n修复建议：")
        print("1. 进入游戏的【幻兽】页面")
        print("2. 点击任意幻兽")
        print("3. 点击【出战】按钮")
        print("4. 至少需要1只出战幻兽才能挑战副本")
        return False
    
    print(f"✅ 找到 {len(beasts)} 只出战幻兽：")
    for beast in beasts:
        print(f"   - {beast['name']} (等级{beast['level']}, {beast['realm']}境)")
    return True


def check_dungeon_progress(user_id: int):
    """检查副本进度表"""
    print(f"\n检查玩家 {user_id} 的副本进度...")
    
    progress = execute_query(
        """
        SELECT dungeon_name, current_floor, floor_cleared, dice, loot_claimed
        FROM player_dungeon_progress
        WHERE user_id = %s
        ORDER BY dungeon_name
        """,
        (user_id,)
    )
    
    if not progress:
        print("⚠️  玩家没有副本进度记录")
        print("\n这是正常的，首次进入副本时会自动创建进度")
        return True
    
    print(f"✅ 找到 {len(progress)} 个副本进度：")
    for p in progress:
        status = "已通关" if p['floor_cleared'] else "未通关"
        loot = "已领取" if p['loot_claimed'] else "未领取"
        print(f"   - {p['dungeon_name']}: 第{p['current_floor']}层 ({status}, 战利品{loot}, 骰子×{p['dice']})")
    return True


def check_dungeon_config():
    """检查副本配置"""
    print("\n检查副本配置...")
    
    import json
    config_path = os.path.join(
        os.path.dirname(__file__),
        "configs",
        "dungeons.json"
    )
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        dungeons = config.get("dungeons", [])
        if not dungeons:
            print("❌ 副本配置为空！")
            return False
        
        print(f"✅ 找到 {len(dungeons)} 个副本配置")
        for dungeon in dungeons[:3]:  # 只显示前3个
            print(f"   - {dungeon.get('name')}: {dungeon.get('total_floors')}层")
        
        return True
    except Exception as e:
        print(f"❌ 读取副本配置失败: {e}")
        return False


def check_player_energy(user_id: int):
    """检查玩家活力值"""
    print(f"\n检查玩家 {user_id} 的活力值...")
    
    player = execute_query(
        "SELECT energy, max_energy FROM players WHERE id = %s",
        (user_id,)
    )
    
    if not player:
        print("❌ 玩家不存在！")
        return False
    
    player = player[0]
    energy = player['energy'] or 0
    max_energy = player['max_energy'] or 190
    
    print(f"✅ 当前活力: {energy}/{max_energy}")
    
    if energy < 15:
        print("⚠️  活力不足15点，无法开启战利品")
        print("   但可以免费挑战幻兽（不消耗活力）")
    
    return True


def check_player_dice(user_id: int, dungeon_name: str = "森林入口"):
    """检查玩家骰子数量"""
    print(f"\n检查玩家 {user_id} 的骰子...")
    
    progress = execute_query(
        """
        SELECT dice FROM player_dungeon_progress
        WHERE user_id = %s AND dungeon_name = %s
        """,
        (user_id, dungeon_name)
    )
    
    if not progress:
        print(f"⚠️  玩家没有【{dungeon_name}】的进度记录")
        print("   首次进入副本时会自动创建进度并赠送骰子")
        return True
    
    dice = progress[0]['dice'] or 0
    print(f"✅ 【{dungeon_name}】骰子数量: {dice}")
    
    if dice <= 0:
        print("⚠️  骰子不足，无法前进")
        print("\n获取骰子的方法：")
        print("1. 在副本页面点击【补充】按钮")
        print("2. 使用骰子包（物品ID: 6010）")
        print("3. 每个骰子包可获得10个骰子")
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("地图副本挑战功能诊断工具")
    print("=" * 60)
    
    # 获取用户ID
    user_id_input = input("\n请输入要检查的玩家ID（直接回车使用默认ID 1）: ").strip()
    user_id = int(user_id_input) if user_id_input else 1
    
    print(f"\n开始诊断玩家 {user_id} 的副本挑战功能...")
    
    # 执行检查
    checks = [
        ("出战幻兽", lambda: check_player_team_beasts(user_id)),
        ("副本进度", lambda: check_dungeon_progress(user_id)),
        ("副本配置", check_dungeon_config),
        ("活力值", lambda: check_player_energy(user_id)),
        ("骰子数量", lambda: check_player_dice(user_id)),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n❌ 检查 {check_name} 时出错: {e}")
            results.append((check_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("诊断总结")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{check_name}: {status}")
    
    if all_passed:
        print("\n✅ 所有检查通过！副本挑战功能应该可以正常使用。")
        print("\n如果仍然无法挑战，请检查：")
        print("1. 浏览器控制台是否有JavaScript错误")
        print("2. 网络请求是否正常（F12 -> Network标签）")
        print("3. 后端服务是否正常运行")
    else:
        print("\n❌ 发现问题，请根据上述建议进行修复。")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n\n发生错误: {e}")
        import traceback
        traceback.print_exc()
