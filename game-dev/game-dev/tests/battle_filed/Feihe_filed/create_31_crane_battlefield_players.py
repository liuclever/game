"""创建31个飞鹤战场测试玩家：每个玩家携带两只幻兽，并随机分配技能。

运行方式：
    python tests/battle_filed/Feihe_filed/create_31_crane_battlefield_players.py

功能：
    - 创建31个测试玩家（user_id从4000开始）
    - 每个玩家等级在40-100之间（飞鹤战场范围）
    - 每个玩家携带两只出战幻兽（is_in_team=1）
    - 为每只幻兽随机分配技能（从技能配置中随机选择）

注意：
    - 本脚本会删除 user_id 在 4000-4030 范围内的现有玩家和幻兽数据
    - 请勿在生产环境运行
"""

import sys
import json
import random
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query, execute_update, execute_insert


# 测试玩家ID范围
START_USER_ID = 4000
END_USER_ID = 4030
NUM_PLAYERS = 31

# 飞鹤战场等级范围
CRANE_LEVEL_MIN = 40
CRANE_LEVEL_MAX = 100


def load_skill_config():
    """加载技能配置"""
    config_path = project_root / "configs" / "skills.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


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


def create_test_player(user_id: int, index: int, skill_config) -> None:
    """创建单个测试玩家及其两只幻兽"""
    
    # 随机等级（40-100，飞鹤战场范围）
    level = random.randint(CRANE_LEVEL_MIN, CRANE_LEVEL_MAX)
    
    # 玩家信息
    username = f"crane_test_{index}"
    password = "123456"  # 测试用固定密码
    nickname = f"飞鹤测试玩家{index}"
    
    # 创建玩家
    execute_insert(
        """
        INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (user_id, username, password, nickname, level, 0, 10000)
    )
    
    # 加载技能配置
    all_active_skills = []
    all_passive_skills = []
    all_buff_skills = []
    
    active_skills = skill_config.get("active_skills", {})
    for tier in ["advanced", "normal"]:
        if tier in active_skills:
            all_active_skills.extend(active_skills[tier].keys())
    
    passive_skills = skill_config.get("passive_skills", {})
    for tier in ["advanced", "normal"]:
        if tier in passive_skills:
            all_passive_skills.extend(passive_skills[tier].keys())
    
    buff_skills = skill_config.get("buff_skills", {})
    for tier in ["advanced", "normal"]:
        if tier in buff_skills:
            all_buff_skills.extend(buff_skills[tier].keys())
    
    # 为玩家创建两只出战幻兽
    for beast_num in range(1, 3):
        # 随机选择技能组合（至少1个主动技能，可能包含被动和增益）
        selected_skills = []
        
        # 至少1个主动技能
        if all_active_skills:
            num_active = random.randint(1, 3)
            selected_skills.extend(random.sample(all_active_skills, min(num_active, len(all_active_skills))))
        
        # 可能包含被动技能
        if all_passive_skills and random.random() < 0.7:
            num_passive = random.randint(0, 2)
            if num_passive > 0:
                selected_skills.extend(random.sample(all_passive_skills, min(num_passive, len(all_passive_skills))))
        
        # 可能包含增益技能
        if all_buff_skills and random.random() < 0.6:
            num_buff = random.randint(0, 2)
            if num_buff > 0:
                selected_skills.extend(random.sample(all_buff_skills, min(num_buff, len(all_buff_skills))))
        
        # 去重
        selected_skills = list(set(selected_skills))
        
        # 随机选择物系或法系
        is_physical = random.choice([True, False])
        
        # 根据玩家等级生成幻兽属性
        base_hp = level * 150 + random.randint(3000, 12000)
        base_attack = level * 25 + random.randint(400, 1800)
        base_defense = level * 20 + random.randint(300, 1500)
        base_speed = 80 + level * 8 + random.randint(-15, 40)
        
        if is_physical:
            physical_attack = base_attack
            magic_attack = base_attack // 3
            nature = "物系普攻"
        else:
            physical_attack = base_attack // 3
            magic_attack = base_attack
            nature = "法系普攻"
        
        # 幻兽信息
        beast_name = f"{nickname}的幻兽{beast_num}"
        realm = random.choice(["神界", "天界", "凡界"])
        race = random.choice(["龙族", "飞禽", "虫族", "神兽", "魔族"])
        personality = random.choice(["勇敢", "冷静", "暴躁", "稳重", "狂暴"])
        
        # 资质值（用于PVP先手判定）
        hp_aptitude = random.randint(1000, 1600)
        attack_aptitude = random.randint(1000, 1600)
        speed_aptitude = random.randint(1000, 1600)
        physical_defense_aptitude = random.randint(1000, 1600)
        magic_defense_aptitude = random.randint(1000, 1600)
        
        # 星数（用于PVP先手判定）
        hp_star = random.randint(2, 6)
        attack_star = random.randint(2, 6)
        speed_star = random.randint(2, 6)
        physical_defense_star = random.randint(2, 6)
        magic_defense_star = random.randint(2, 6)
        
        # 技能JSON
        skills_json = json.dumps(selected_skills, ensure_ascii=False)
        
        # 插入幻兽
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
                random.randint(85, 105),
                hp_aptitude, speed_aptitude, attack_aptitude,
                physical_defense_aptitude, magic_defense_aptitude,
                "10000/10000", skills_json, "", "",
                1, beast_num  # is_in_team=1, team_position=1或2
            )
        )


def main():
    """主函数"""
    print("=" * 60)
    print("创建31个飞鹤战场测试玩家")
    print("=" * 60)
    print()
    
    # 确认操作
    print(f"将创建 {NUM_PLAYERS} 个测试玩家（user_id: {START_USER_ID}-{START_USER_ID + NUM_PLAYERS - 1}）")
    print(f"每个玩家等级范围: {CRANE_LEVEL_MIN}-{CRANE_LEVEL_MAX}级（飞鹤战场）")
    print("每个玩家将拥有2只出战幻兽（带随机技能）")
    print()
    
    try:
        # 1. 加载技能配置
        print("加载技能配置...")
        skill_config = load_skill_config()
        print("  ✅ 技能配置加载成功")
        print()
        
        # 2. 清理现有数据
        delete_existing_test_players()
        print()
        
        # 3. 创建玩家和幻兽
        print(f"开始创建 {NUM_PLAYERS} 个测试玩家...")
        for i in range(NUM_PLAYERS):
            user_id = START_USER_ID + i
            index = i + 1
            create_test_player(user_id, index, skill_config)
            if (i + 1) % 10 == 0:
                print(f"  已创建 {i + 1}/{NUM_PLAYERS} 个玩家...")
        
        print(f"✅ 成功创建 {NUM_PLAYERS} 个测试玩家！")
        print()
        
        # 4. 验证创建结果
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
            print("  ✅ 所有玩家都有2只出战幻兽")
        
        # 检查等级范围
        players_out_of_range = [p for p in players if not (CRANE_LEVEL_MIN <= p['level'] <= CRANE_LEVEL_MAX)]
        if players_out_of_range:
            print(f"  ⚠️  警告：{len(players_out_of_range)} 个玩家等级不在{CRANE_LEVEL_MIN}-{CRANE_LEVEL_MAX}范围内")
        else:
            print(f"  ✅ 所有玩家等级都在{CRANE_LEVEL_MIN}-{CRANE_LEVEL_MAX}范围内（飞鹤战场）")
        
        # 检查技能分配
        beasts_with_skills = execute_query(
            """
            SELECT COUNT(*) as cnt
            FROM player_beast
            WHERE user_id BETWEEN %s AND %s 
              AND is_in_team = 1
              AND skills IS NOT NULL
              AND skills != '[]'
              AND skills != ''
            """,
            (START_USER_ID, START_USER_ID + NUM_PLAYERS - 1)
        )
        total_beasts = NUM_PLAYERS * 2
        skill_count = beasts_with_skills[0]['cnt'] if beasts_with_skills else 0
        print(f"  ✅ 有技能的幻兽: {skill_count}/{total_beasts}")
        
        print()
        print("=" * 60)
        print("创建完成！")
        print()
        print("测试玩家信息：")
        print(f"  - user_id范围: {START_USER_ID}-{START_USER_ID + NUM_PLAYERS - 1}")
        print(f"  - 账号格式: crane_test_1 到 crane_test_{NUM_PLAYERS}")
        print(f"  - 密码: 123456（所有玩家）")
        print(f"  - 等级范围: {CRANE_LEVEL_MIN}-{CRANE_LEVEL_MAX}级")
        print(f"  - 每个玩家: 2只出战幻兽（带随机技能）")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 创建失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
