"""测试战场奖励配置和领取逻辑"""
import sys
sys.path.insert(0, '.')

from infrastructure.config.battlefield_reward_config import BattlefieldRewardConfig

def test_reward_config():
    """测试奖励配置加载"""
    print("=" * 60)
    print("测试战场奖励配置")
    print("=" * 60)
    
    try:
        config = BattlefieldRewardConfig()
        
        # 测试战王奖励
        print("\n【战王奖励】")
        print("-" * 60)
        king_reward = config.get_king_reward()
        print(f"描述: {king_reward.get('description')}")
        print(f"铜钱: {king_reward.get('gold'):,}")
        print(f"道具:")
        for item in king_reward.get('items', []):
            print(f"  - {item['name']} × {item['quantity']}")
        
        # 测试阵营奖励
        print("\n【阵营奖励】")
        print("-" * 60)
        
        print("\n胜利阵营:")
        win_reward = config.get_camp_reward(True)
        print(f"描述: {win_reward.get('description')}")
        print(f"铜钱: {win_reward.get('gold'):,}")
        print(f"道具:")
        for item in win_reward.get('items', []):
            print(f"  - {item['name']} × {item['quantity']}")
        
        print("\n失败阵营:")
        lose_reward = config.get_camp_reward(False)
        print(f"描述: {lose_reward.get('description')}")
        print(f"铜钱: {lose_reward.get('gold'):,}")
        print(f"道具:")
        for item in lose_reward.get('items', []):
            print(f"  - {item['name']} × {item['quantity']}")
        
        # 测试杀敌奖励
        print("\n【杀敌奖励】")
        print("-" * 60)
        for kills in [0, 1, 2, 3, 4, 5, 10]:
            kill_reward = config.get_kill_reward(kills)
            print(f"\n击杀{kills}人:")
            print(f"  描述: {kill_reward.get('description')}")
            print(f"  铜钱: {kill_reward.get('gold'):,}")
            if kill_reward.get('items'):
                print(f"  道具:")
                for item in kill_reward.get('items', []):
                    print(f"    - {item['name']} × {item['quantity']}")
        
        print("\n" + "=" * 60)
        print("✓ 配置加载成功")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()

def test_reward_calculation():
    """测试奖励计算示例"""
    print("\n" + "=" * 60)
    print("奖励计算示例")
    print("=" * 60)
    
    config = BattlefieldRewardConfig()
    
    # 示例1：战王（击杀5人，胜利阵营）
    print("\n【示例1：战王】")
    print("-" * 60)
    print("身份: 战王")
    print("击杀: 5人")
    print("阵营: 胜利")
    
    total_gold = 0
    total_items = []
    
    # 战王奖励
    king_reward = config.get_king_reward()
    total_gold += king_reward.get('gold', 0)
    total_items.extend(king_reward.get('items', []))
    print(f"\n战王奖励: 铜钱+{king_reward.get('gold'):,}")
    
    # 阵营奖励
    camp_reward = config.get_camp_reward(True)
    total_gold += camp_reward.get('gold', 0)
    total_items.extend(camp_reward.get('items', []))
    print(f"阵营奖励: 铜钱+{camp_reward.get('gold'):,}")
    
    # 杀敌奖励
    kill_reward = config.get_kill_reward(5)
    total_gold += kill_reward.get('gold', 0)
    total_items.extend(kill_reward.get('items', []))
    print(f"杀敌奖励: 铜钱+{kill_reward.get('gold'):,}")
    
    print(f"\n总计: 铜钱+{total_gold:,}，道具×{len(total_items)}")
    
    # 示例2：普通玩家（击杀2人，失败阵营）
    print("\n【示例2：普通玩家】")
    print("-" * 60)
    print("身份: 普通玩家")
    print("击杀: 2人")
    print("阵营: 失败")
    
    total_gold = 0
    total_items = []
    
    # 阵营奖励
    camp_reward = config.get_camp_reward(False)
    total_gold += camp_reward.get('gold', 0)
    total_items.extend(camp_reward.get('items', []))
    print(f"\n阵营奖励: 铜钱+{camp_reward.get('gold'):,}")
    
    # 杀敌奖励
    kill_reward = config.get_kill_reward(2)
    total_gold += kill_reward.get('gold', 0)
    total_items.extend(kill_reward.get('items', []))
    print(f"杀敌奖励: 铜钱+{kill_reward.get('gold'):,}")
    
    print(f"\n总计: 铜钱+{total_gold:,}，道具×{len(total_items)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_reward_config()
    test_reward_calculation()
