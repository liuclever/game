"""
创建20个50级测试账号，每个账号都有追风狼幻兽并上阵
"""
import sys
from pathlib import Path

# 将项目根目录添加到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print("正在导入模块...")
try:
    from infrastructure.db.connection import execute_query, execute_update
    print("✅ 数据库连接模块导入成功")
except Exception as e:
    print(f"❌ 导入数据库模块失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

import random
from datetime import datetime

def create_test_accounts():
    """创建20个50级测试账号"""
    
    print("=" * 60)
    print("开始创建测试账号...")
    print("=" * 60)
    
    # 追风狼模板ID
    BEAST_TEMPLATE_ID = 6
    
    # 测试数据库连接
    print("\n[1/4] 测试数据库连接...")
    try:
        result = execute_query("SELECT 1 as test")
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 获取当前最大的user_id
    print("\n[2/4] 查询当前最大用户ID...")
    try:
        result = execute_query("SELECT MAX(user_id) as max_id FROM player")
        start_id = (result[0]['max_id'] or 1000) + 1
        print(f"✅ 将从 user_id={start_id} 开始创建")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    created_count = 0
    
    print(f"\n[3/4] 开始创建20个测试账号...\n")
    
    for i in range(20):
        user_id = start_id + i
        username = f"test_lv50_{i+1:02d}"
        nickname = f"测试玩家{i+1:02d}"
        
        try:
            # 1. 检查用户是否已存在
            existing = execute_query(
                "SELECT user_id FROM player WHERE username = %s OR user_id = %s",
                (username, user_id)
            )
            
            if existing:
                print(f"⚠️  用户 {username} 已存在，跳过")
                continue
            
            # 2. 创建玩家账号（50级）
            execute_update(
                """INSERT INTO player (
                    user_id, username, nickname, password, level, 
                    exp, gold, yuanbao, energy, prestige, 
                    enhancement_stone, vip_level, crystal_tower,
                    created_at
                ) VALUES (
                    %s, %s, %s, 'test123', 50,
                    0, 1000000, 10000, 190, 0,
                    10000, 0, 0,
                    NOW()
                )""",
                (user_id, username, nickname)
            )
            
            # 3. 创建追风狼幻兽（50级，上阵）
            # 随机生成资质（800-1200）
            hp_aptitude = random.randint(900, 1200)
            physical_attack_aptitude = random.randint(900, 1200)
            physical_defense_aptitude = random.randint(900, 1200)
            speed_aptitude = random.randint(1000, 1300)  # 追风狼速度资质更高
            magic_attack_aptitude = random.randint(800, 1100)
            magic_defense_aptitude = random.randint(800, 1100)
            
            # 成长率
            growth_rate = random.randint(850, 900)
            
            # 随机性格
            personalities = ["勇敢", "冷静", "暴躁", "稳重", "狂暴"]
            personality = random.choice(personalities)
            
            # 计算50级的属性（简化计算）
            hp = int(hp_aptitude * 50 / 10)
            physical_attack = int(physical_attack_aptitude * 50 / 10)
            physical_defense = int(physical_defense_aptitude * 50 / 10)
            speed = int(speed_aptitude * 50 / 10)
            magic_attack = int(magic_attack_aptitude * 50 / 10)
            magic_defense = int(magic_defense_aptitude * 50 / 10)
            combat_power = hp + physical_attack + physical_defense + speed + magic_attack + magic_defense
            
            execute_update(
                """INSERT INTO player_beast (
                    user_id, template_id, name, nickname, level, exp, realm,
                    race, nature, personality, attack_type,
                    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
                    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
                    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
                    growth_rate, combat_power, lifespan, skills,
                    is_in_team, team_position,
                    created_at
                ) VALUES (
                    %s, %s, '追风狼', '追风狼', 50, 0, '天界',
                    '兽族', '物系高速', %s, 'physical',
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, '10000/10000', '[]',
                    1, 1,
                    NOW()
                )""",
                (
                    user_id, BEAST_TEMPLATE_ID, personality,
                    hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
                    hp_aptitude, physical_attack_aptitude, magic_attack_aptitude,
                    physical_defense_aptitude, magic_defense_aptitude, speed_aptitude,
                    growth_rate, combat_power
                )
            )
            
            # 4. 给玩家背包添加初始召唤球（和正常注册一样）
            # 血螳螂(20003) / 追风狼(20006) / 羽精灵(20009) 各1个
            # 额外再给5个追风狼召唤球用于测试
            execute_update(
                """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary) 
                   VALUES (%s, 20003, 1, 0)""",
                (user_id,)
            )
            execute_update(
                """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary) 
                   VALUES (%s, 20006, 6, 0)""",  # 1个初始 + 5个额外
                (user_id,)
            )
            execute_update(
                """INSERT INTO player_inventory (user_id, item_id, quantity, is_temporary) 
                   VALUES (%s, 20009, 1, 0)""",
                (user_id,)
            )
            
            created_count += 1
            print(f"✅ [{created_count}/20] {username} (ID:{user_id}) - 追风狼50级({personality})")
            
        except Exception as e:
            print(f"❌ 创建账号 {username} 失败: {e}")
            import traceback
            traceback.print_exc()
            print()
            continue
    
    print("\n" + "=" * 60)
    print(f"[4/4] 完成！成功创建 {created_count} 个测试账号")
    print("=" * 60)
    
    if created_count > 0:
        print("\n✅ 测试账号信息：")
        print("  用户名: test_lv50_01 ~ test_lv50_20")
        print("  密码: 需要通过后台设置")
        print("  等级: 50级")
        print("  铜钱: 5,000,000")
        print("  元宝: 10,000")
        print("  强化石: 10,000")
        print("  幻兽: 追风狼 (50级, 已上阵)")
        print("\n💡 提示: 可以使用这些账号进行连胜竞技场测试")
    else:
        print("\n⚠️  没有创建任何账号，请检查上面的错误信息")
    print()

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  创建测试账号工具")
    print("=" * 60 + "\n")
    
    try:
        create_test_accounts()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n按任意键退出...")
    input()
