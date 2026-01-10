"""自动为31个测试玩家报名猛虎战场。

运行方式：
    python tests/battle_filed/tiger_filed/signup_31_test_players.py

功能：
    - 为 create_31_test_players.py 创建的31个玩家（user_id 2000-2030）报名猛虎战场
    - 清空这些玩家当日的旧报名记录后重新报名
    - 验证所有玩家都有出战幻兽且等级在20-39范围内

前置条件：
    - 需要先运行 create_information/create_31_test_players.py 创建测试玩家
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query, execute_update

# 测试玩家ID范围（与 create_31_test_players.py 保持一致）
START_USER_ID = 2000
END_USER_ID = 2030
NUM_PLAYERS = 31

# 战场类型
BATTLEFIELD_TYPE = "tiger"
BATTLEFIELD_NAME = "猛虎战场"
MIN_LEVEL = 20
MAX_LEVEL = 39


def validate_test_players():
    """验证测试玩家是否存在且满足条件"""
    print("验证测试玩家...")
    
    # 查询玩家信息
    players = execute_query(
        """
        SELECT p.user_id, p.nickname, p.level,
               (SELECT COUNT(*) FROM player_beast WHERE user_id = p.user_id AND is_in_team = 1) as team_beast_count
        FROM player p
        WHERE p.user_id BETWEEN %s AND %s
        ORDER BY p.user_id
        """,
        (START_USER_ID, END_USER_ID)
    )
    
    if len(players) < NUM_PLAYERS:
        print(f"❌ 错误：找到 {len(players)} 个玩家，需要 {NUM_PLAYERS} 个")
        print("   请先运行: python tests/battle_filed/tiger_filed/create_information/create_31_test_players.py")
        return None
    
    # 检查等级和出战幻兽
    valid_players = []
    invalid_players = []
    
    for p in players:
        user_id = p['user_id']
        level = p['level']
        beast_count = p['team_beast_count']
        
        if MIN_LEVEL <= level <= MAX_LEVEL and beast_count > 0:
            valid_players.append(p)
        else:
            reasons = []
            if not (MIN_LEVEL <= level <= MAX_LEVEL):
                reasons.append(f"等级{level}不在{MIN_LEVEL}-{MAX_LEVEL}范围")
            if beast_count == 0:
                reasons.append("没有出战幻兽")
            invalid_players.append((p, reasons))
    
    if invalid_players:
        print(f"⚠️  警告：{len(invalid_players)} 个玩家不满足条件：")
        for p, reasons in invalid_players[:5]:  # 只显示前5个
            print(f"   - user_id={p['user_id']}, {p['nickname']}: {', '.join(reasons)}")
        if len(invalid_players) > 5:
            print(f"   ... 还有 {len(invalid_players) - 5} 个")
    
    print(f"✅ 找到 {len(valid_players)} 个有效玩家")
    return valid_players


def clear_today_signups():
    """清空测试玩家当日的报名记录"""
    print(f"清空测试玩家当日的{BATTLEFIELD_NAME}报名记录...")
    
    result = execute_update(
        """
        DELETE FROM battlefield_signup 
        WHERE battlefield_type = %s 
          AND signup_date = CURDATE() 
          AND user_id BETWEEN %s AND %s
        """,
        (BATTLEFIELD_TYPE, START_USER_ID, END_USER_ID)
    )
    
    print(f"  已清空 {result} 条旧报名记录")


def signup_players(players):
    """为玩家报名战场"""
    print(f"为 {len(players)} 个玩家报名{BATTLEFIELD_NAME}...")
    
    success_count = 0
    for p in players:
        user_id = p['user_id']
        try:
            execute_update(
                """
                INSERT INTO battlefield_signup (user_id, battlefield_type, signup_date)
                VALUES (%s, %s, CURDATE())
                ON DUPLICATE KEY UPDATE signup_time = NOW()
                """,
                (user_id, BATTLEFIELD_TYPE)
            )
            success_count += 1
        except Exception as e:
            print(f"  ❌ user_id={user_id} 报名失败: {e}")
    
    print(f"✅ 成功报名 {success_count}/{len(players)} 个玩家")
    return success_count


def verify_signups():
    """验证报名结果"""
    print("验证报名结果...")
    
    rows = execute_query(
        """
        SELECT s.user_id, p.nickname, p.level, s.signup_time
        FROM battlefield_signup s
        JOIN player p ON s.user_id = p.user_id
        WHERE s.battlefield_type = %s 
          AND s.signup_date = CURDATE()
          AND s.user_id BETWEEN %s AND %s
        ORDER BY s.user_id
        """,
        (BATTLEFIELD_TYPE, START_USER_ID, END_USER_ID)
    )
    
    print(f"  当日{BATTLEFIELD_NAME}已报名玩家数: {len(rows)}")
    
    # 显示部分报名信息
    if rows:
        print("  报名玩家列表（前10个）：")
        for row in rows[:10]:
            print(f"    - user_id={row['user_id']}, {row['nickname']}, Lv.{row['level']}")
        if len(rows) > 10:
            print(f"    ... 还有 {len(rows) - 10} 个")
    
    return len(rows)


def main():
    """主函数"""
    print("=" * 60)
    print(f"自动报名{BATTLEFIELD_NAME}（31个测试玩家）")
    print("=" * 60)
    print()
    
    try:
        # 1. 验证测试玩家
        players = validate_test_players()
        if not players:
            sys.exit(1)
        print()
        
        # 2. 清空当日旧报名
        clear_today_signups()
        print()
        
        # 3. 报名
        success_count = signup_players(players)
        print()
        
        # 4. 验证报名结果
        final_count = verify_signups()
        print()
        
        # 5. 总结
        print("=" * 60)
        if final_count >= NUM_PLAYERS:
            print(f"✅ 报名完成！共 {final_count} 个玩家已报名{BATTLEFIELD_NAME}")
            print()
            print("下一步可以：")
            print("  1. 运行战场淘汰赛：")
            print("     python scripts/run_daily_battlefield.py")
            print("  2. 或运行完整测试：")
            print("     python -m pytest tests/battle_filed/tiger_filed/test_battlefield_signup.py -vv")
        else:
            print(f"⚠️  报名不完整，只有 {final_count}/{NUM_PLAYERS} 个玩家报名成功")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 运行失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

