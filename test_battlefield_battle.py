"""测试战场战斗逻辑"""
import sys
sys.path.insert(0, '.')

from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.db.battlefield_repo_mysql import MySQLBattlefieldBattleRepo
from application.services.battlefield_service import BattlefieldService
from application.services.beast_pvp_service import BeastPvpService

def test_battlefield_battle():
    """测试战场战斗功能"""
    print("=" * 60)
    print("测试战场战斗逻辑")
    print("=" * 60)
    
    # 初始化服务
    player_repo = MySQLPlayerRepo()
    beast_repo = MySQLPlayerBeastRepo()
    battle_repo = MySQLBattlefieldBattleRepo()
    beast_pvp_service = BeastPvpService()
    
    service = BattlefieldService(
        player_repo=player_repo,
        player_beast_repo=beast_repo,
        battle_repo=battle_repo,
        beast_pvp_service=beast_pvp_service,
    )
    
    # 测试猛虎战场
    print("\n【测试猛虎战场】")
    print("-" * 60)
    try:
        result = service.run_tournament("tiger")
        if result.get("ok"):
            print(f"✓ 猛虎战场开赛成功")
            print(f"  期数: {result.get('period')}")
            print(f"  参赛人数: {result.get('total_players')}")
            print(f"  总轮数: {result.get('total_rounds')}")
            print(f"  冠军: {result.get('champion_name')} (ID: {result.get('champion_id')})")
            print(f"  阵营: {result.get('champion_team')}")
            print(f"  胜场数: {result.get('champion_wins')}")
        else:
            print(f"✗ 猛虎战场开赛失败: {result.get('error')}")
    except Exception as e:
        print(f"✗ 猛虎战场异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试飞鹤战场
    print("\n【测试飞鹤战场】")
    print("-" * 60)
    try:
        result = service.run_tournament("crane")
        if result.get("ok"):
            print(f"✓ 飞鹤战场开赛成功")
            print(f"  期数: {result.get('period')}")
            print(f"  参赛人数: {result.get('total_players')}")
            print(f"  总轮数: {result.get('total_rounds')}")
            print(f"  冠军: {result.get('champion_name')} (ID: {result.get('champion_id')})")
            print(f"  阵营: {result.get('champion_team')}")
            print(f"  胜场数: {result.get('champion_wins')}")
        else:
            print(f"✗ 飞鹤战场开赛失败: {result.get('error')}")
    except Exception as e:
        print(f"✗ 飞鹤战场异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 查询战报
    print("\n【查询战报】")
    print("-" * 60)
    for bf_type in ["tiger", "crane"]:
        period = battle_repo.get_latest_period(bf_type)
        if period:
            logs = battle_repo.get_matches_for_period(bf_type, period)
            print(f"\n{bf_type.upper()} 战场第 {period} 期，共 {len(logs)} 场战斗:")
            for log in logs[:5]:  # 只显示前5场
                winner = log.first_user_name if log.is_first_win else log.second_user_name
                print(f"  第{log.round_num}轮第{log.match_num}场: {log.first_user_name} vs {log.second_user_name} -> {winner}胜")
            if len(logs) > 5:
                print(f"  ... 还有 {len(logs) - 5} 场战斗")
        else:
            print(f"\n{bf_type.upper()} 战场暂无战报")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_battlefield_battle()
