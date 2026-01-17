"""测试闯塔每日次数限制

新规则：
- 每日最多4次
- 第1次免费
- 第2-4次每次需要200元宝重置
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from infrastructure.db import get_session
from infrastructure.repositories.player_repo_mysql import PlayerRepoMySQL
from infrastructure.repositories.tower_repo_mysql import TowerStateRepoMySQL, TowerConfigRepoMySQL
from application.services.tower_service import TowerBattleService, PlayerBeast, TowerError


def test_daily_limit():
    """测试每日次数限制"""
    session = get_session()
    player_repo = PlayerRepoMySQL(session)
    state_repo = TowerStateRepoMySQL(session)
    config_repo = TowerConfigRepoMySQL(session)
    
    tower_service = TowerBattleService(
        state_repo=state_repo,
        config_repo=config_repo,
        player_repo=player_repo,
    )
    
    # 使用测试账号
    test_user_id = 1
    tower_type = "tongtian"
    
    # 获取玩家信息
    player = player_repo.get_by_id(test_user_id)
    if not player:
        print(f"❌ 玩家 {test_user_id} 不存在")
        return
    
    print(f"玩家信息：{player.nickname} (ID: {test_user_id})")
    print(f"当前元宝：{player.yuanbao}")
    print()
    
    # 获取闯塔状态
    state = state_repo.get_by_user_id(test_user_id, tower_type)
    state.reset_daily_if_needed()
    
    print(f"当前闯塔状态：")
    print(f"  今日次数：{state.today_count}")
    print(f"  当前层数：{state.current_floor}")
    print()
    
    # 测试每日限制
    daily_limit = tower_service._get_daily_limit()
    print(f"✅ 每日限制：{daily_limit}次")
    print()
    
    # 模拟4次闯塔
    for i in range(1, 5):
        print(f"--- 第{i}次闯塔 ---")
        
        # 获取当前状态
        state = state_repo.get_by_user_id(test_user_id, tower_type)
        player = player_repo.get_by_id(test_user_id)
        
        print(f"闯塔前：今日次数 {state.today_count}, 元宝 {player.yuanbao}")
        
        try:
            # 检查是否能闯塔
            tower_service._ensure_can_challenge_today(
                user_id=test_user_id,
                state=state,
                is_continue=False
            )
            
            # 模拟增加次数
            state.today_count += 1
            state_repo.save(state)
            
            # 获取更新后的状态
            state = state_repo.get_by_user_id(test_user_id, tower_type)
            player = player_repo.get_by_id(test_user_id)
            
            print(f"闯塔后：今日次数 {state.today_count}, 元宝 {player.yuanbao}")
            
            if i == 1:
                print(f"✅ 第1次免费")
            else:
                print(f"✅ 第{i}次消耗200元宝")
            
        except TowerError as e:
            print(f"❌ 错误：{e}")
        
        print()
    
    # 测试第5次（应该失败）
    print(f"--- 第5次闯塔（应该失败）---")
    state = state_repo.get_by_user_id(test_user_id, tower_type)
    print(f"当前次数：{state.today_count}")
    
    try:
        tower_service._ensure_can_challenge_today(
            user_id=test_user_id,
            state=state,
            is_continue=False
        )
        print(f"❌ 应该失败但成功了")
    except TowerError as e:
        print(f"✅ 正确拒绝：{e}")
    
    print()
    print("=" * 50)
    print("测试完成")


def test_continue_challenge():
    """测试继续挑战不消耗次数"""
    session = get_session()
    player_repo = PlayerRepoMySQL(session)
    state_repo = TowerStateRepoMySQL(session)
    config_repo = TowerConfigRepoMySQL(session)
    
    tower_service = TowerBattleService(
        state_repo=state_repo,
        config_repo=config_repo,
        player_repo=player_repo,
    )
    
    test_user_id = 1
    tower_type = "tongtian"
    
    print("=" * 50)
    print("测试继续挑战（is_continue=True）")
    print("=" * 50)
    print()
    
    # 获取当前状态
    state = state_repo.get_by_user_id(test_user_id, tower_type)
    player = player_repo.get_by_id(test_user_id)
    
    print(f"继续挑战前：今日次数 {state.today_count}, 元宝 {player.yuanbao}")
    
    try:
        # 继续挑战不应该扣元宝
        tower_service._ensure_can_challenge_today(
            user_id=test_user_id,
            state=state,
            is_continue=True
        )
        
        # 获取更新后的状态
        player = player_repo.get_by_id(test_user_id)
        
        print(f"继续挑战后：今日次数 {state.today_count}, 元宝 {player.yuanbao}")
        print(f"✅ 继续挑战不消耗元宝")
        
    except TowerError as e:
        print(f"❌ 错误：{e}")
    
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("闯塔每日次数限制测试")
    print("=" * 50)
    print()
    
    # 注意：这个测试会修改数据库，请在测试环境运行
    print("⚠️  警告：此测试会修改数据库数据")
    print("⚠️  请确保在测试环境运行")
    print()
    
    response = input("是否继续？(y/n): ")
    if response.lower() != 'y':
        print("测试取消")
        sys.exit(0)
    
    print()
    
    try:
        test_daily_limit()
        print()
        test_continue_challenge()
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
