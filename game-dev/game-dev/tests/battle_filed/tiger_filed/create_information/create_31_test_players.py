"""创建31个测试玩家和幻兽，用于古战场测试。

运行方式：
    python tests/battle_filed/tiger_filed/create_information/create_31_test_players.py

功能：
    - 创建31个玩家（user_id从2000开始）
    - 每个玩家等级在20-39之间（猛虎战场范围）
    - 每个玩家至少有一只出战幻兽（is_in_team=1）
    - 如果玩家已存在，会先删除再重新创建

注意：
    - 本脚本会删除user_id在2000-2030范围内的现有玩家和幻兽数据
    - 请勿在生产环境运行
"""

import sys
import os
import random
from pathlib import Path

# 添加项目根目录到路径（tests/battle_filed/tiger_filed/create_information -> 根目录需向上5级）
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query, execute_update, execute_insert


# 测试玩家ID范围
START_USER_ID = 2000
END_USER_ID = 2030
NUM_PLAYERS = 31


def delete_existing_test_players():
    """删除现有的测试玩家数据"""
    print("清理现有测试玩家数据...")
    
    # 删除幻兽
    execute_update(
        "DELETE FROM player_beast WHERE user_id BETWEEN %s AND %s",
        (START_USER_ID, END_USER_ID)
    )
    
    # 删除玩家
    execute_update(
        "DELETE FROM player WHERE user_id BETWEEN %s AND %s",
        (START_USER_ID, END_USER_ID)
    )
    
    print(f"已清理 user_id {START_USER_ID}-{END_USER_ID} 范围内的数据")


def create_test_player(user_id: int, index: int) -> None:
    """创建单个测试玩家及其幻兽"""
    
    # 随机等级（20-39）
    level = random.randint(20, 39)
    
    # 玩家信息
    username = f"battlefield_test_{index}"
    password = "123456"  # 测试用固定密码
    nickname = f"测试玩家{index}"
    
    # 创建玩家
    execute_insert(
        """
        INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, username, password, nickname, level, 0, 10000)
    )
    
    # 为玩家创建至少一只出战幻兽
    # 根据等级生成合理的属性值
    base_hp = level * 100 + random.randint(500, 1500)
    base_attack = level * 10 + random.randint(50, 200)
    base_defense = level * 8 + random.randint(40, 160)
    base_speed = 50 + level * 5 + random.randint(-10, 20)
    
    # 随机选择物系或法系
    is_physical = random.choice([True, False])
    
    if is_physical:
        physical_attack = base_attack
        magic_attack = base_attack // 2
        nature = "物系普攻"
    else:
        physical_attack = base_attack // 2
        magic_attack = base_attack
        nature = "法系普攻"
    
    # 创建第一只出战幻兽
    beast_name = f"{nickname}的幻兽1"
    realm = random.choice(["凡界", "天界", "神界"])
    race = random.choice(["龙族", "飞禽", "虫族", "神兽", "魔族"])
    personality = random.choice(["勇敢", "冷静", "暴躁", "稳重", "狂暴"])
    
    # 资质值（用于PVP先手判定）
    hp_aptitude = random.randint(800, 1200)
    attack_aptitude = random.randint(800, 1200)
    speed_aptitude = random.randint(800, 1200)
    physical_defense_aptitude = random.randint(800, 1200)
    magic_defense_aptitude = random.randint(800, 1200)
    
    # 星数（用于PVP先手判定）
    hp_star = random.randint(0, 5)
    attack_star = random.randint(0, 5)
    speed_star = random.randint(0, 5)
    physical_defense_star = random.randint(0, 5)
    magic_defense_star = random.randint(0, 5)
    
    # 技能列表（简单技能，用于测试）
    skills = '["普攻"]'
    if random.random() < 0.5:
        skills = '["普攻", "必杀"]'
    
    execute_insert(
        """
        INSERT INTO player_beast (
            user_id, name, realm, race, level, nature, personality,
            hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
            combat_power, growth_rate,
            hp_aptitude, speed_aptitude, magic_attack_aptitude, 
            physical_defense_aptitude, magic_defense_aptitude,
            lifespan, skills, counters, countered_by,
            is_in_team, team_position
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s
        )
        """,
        (
            user_id, beast_name, realm, race, level, nature, personality,
            base_hp, physical_attack, magic_attack, base_defense, base_defense, base_speed,
            base_hp + base_attack + base_defense * 2,  # 简单战力计算
            random.randint(80, 100),
            hp_aptitude, speed_aptitude, attack_aptitude,
            physical_defense_aptitude, magic_defense_aptitude,
            "10000/10000", skills, "", "",
            1, 1  # is_in_team=1, team_position=1
        )
    )
    
    # 可选：再创建1-2只备用幻兽（不在队伍中）
    num_extra_beasts = random.randint(0, 2)
    for i in range(num_extra_beasts):
        extra_beast_name = f"{nickname}的幻兽{i+2}"
        extra_base_hp = level * 80 + random.randint(400, 1200)
        extra_attack = level * 8 + random.randint(40, 160)
        extra_defense = level * 6 + random.randint(30, 120)
        extra_speed = 40 + level * 4 + random.randint(-10, 15)
        
        extra_is_physical = random.choice([True, False])
        if extra_is_physical:
            extra_physical_attack = extra_attack
            extra_magic_attack = extra_attack // 2
            extra_nature = "物系普攻"
        else:
            extra_physical_attack = extra_attack // 2
            extra_magic_attack = extra_attack
            extra_nature = "法系普攻"
        
        execute_insert(
            """
            INSERT INTO player_beast (
                user_id, name, realm, race, level, nature, personality,
                hp, physical_attack, magic_attack, physical_defense, magic_defense, speed,
                combat_power, growth_rate,
                hp_aptitude, speed_aptitude, magic_attack_aptitude,
                physical_defense_aptitude, magic_defense_aptitude,
                lifespan, skills, counters, countered_by,
                is_in_team, team_position
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s
            )
            """,
            (
                user_id, extra_beast_name, realm, race, level, extra_nature, personality,
                extra_base_hp, extra_physical_attack, extra_magic_attack, 
                extra_defense, extra_defense, extra_speed,
                extra_base_hp + extra_attack + extra_defense * 2,
                random.randint(75, 95),
                random.randint(700, 1100), random.randint(700, 1100), random.randint(700, 1100),
                random.randint(700, 1100), random.randint(700, 1100),
                "10000/10000", '["普攻"]', "", "",
                0, 0  # 不在队伍中
            )
        )


def main():
    """主函数"""
    print("=" * 60)
    print("创建31个测试玩家和幻兽（用于古战场测试）")
    print("=" * 60)
    print()
    
    # 确认操作
    print(f"将创建 {NUM_PLAYERS} 个测试玩家（user_id: {START_USER_ID}-{START_USER_ID + NUM_PLAYERS - 1}）")
    print("每个玩家将拥有至少1只出战幻兽")
    print()
    
    try:
        # 1. 清理现有数据
        delete_existing_test_players()
        print()
        
        # 2. 创建玩家和幻兽
        print(f"开始创建 {NUM_PLAYERS} 个测试玩家...")
        for i in range(NUM_PLAYERS):
            user_id = START_USER_ID + i
            index = i + 1
            create_test_player(user_id, index)
            if (i + 1) % 10 == 0:
                print(f"  已创建 {i + 1}/{NUM_PLAYERS} 个玩家...")
        
        print(f"✅ 成功创建 {NUM_PLAYERS} 个测试玩家！")
        print()
        
        # 3. 验证创建结果
        print("验证创建结果...")
        players = execute_query(
            """
            SELECT user_id, nickname, level, 
                   (SELECT COUNT(*) FROM player_beast WHERE user_id = p.user_id AND is_in_team = 1) as team_beast_count
            FROM player p
            WHERE user_id BETWEEN %s AND %s
            ORDER BY user_id
            """,
            (START_USER_ID, START_USER_ID + NUM_PLAYERS - 1)
        )
        
        print(f"  找到 {len(players)} 个玩家")
        
        # 检查是否有玩家没有出战幻兽
        players_without_beasts = [p for p in players if p['team_beast_count'] == 0]
        if players_without_beasts:
            print(f"  ⚠️  警告：{len(players_without_beasts)} 个玩家没有出战幻兽：")
            for p in players_without_beasts:
                print(f"    - user_id={p['user_id']}, {p['nickname']}")
        else:
            print("  ✅ 所有玩家都有至少1只出战幻兽")
        
        # 检查等级范围
        players_out_of_range = [p for p in players if not (20 <= p['level'] <= 39)]
        if players_out_of_range:
            print(f"  ⚠️  警告：{len(players_out_of_range)} 个玩家等级不在20-39范围内")
        else:
            print("  ✅ 所有玩家等级都在20-39范围内（猛虎战场）")
        
        print()
        print("=" * 60)
        print("创建完成！现在可以运行测试：")
        print("  python -m pytest tests/battle_filed/test_battlefield_signup.py -vv")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 创建失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
