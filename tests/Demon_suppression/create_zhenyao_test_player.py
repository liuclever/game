"""创建镇妖测试玩家：创建一个玩家，携带两只幻兽，随机分配技能。

运行方式：
    python tests/Demon_suppression/create_zhenyao_test_player.py

功能：
    - 创建一个测试玩家（user_id: 3000）
    - 玩家等级：100级（战神阶，可镇妖101-120层）
    - 创建两只出战幻兽（is_in_team=1）
    - 为每只幻兽随机分配技能（从技能配置中随机选择）

注意：
    - 本脚本会删除 user_id=3000 的现有玩家和幻兽数据
    - 请勿在生产环境运行
"""

import sys
import json
import random
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query, execute_update, execute_insert


# 测试玩家ID
TEST_USER_ID = 3000
TEST_USERNAME = "zhenyao_test"
TEST_PASSWORD = "123456"
TEST_NICKNAME = "镇妖测试玩家"


def load_skill_config():
    """加载技能配置"""
    config_path = project_root / "configs" / "skills.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_random_skills(skill_config, num_skills: int = 3) -> list:
    """随机选择技能
    
    Args:
        skill_config: 技能配置字典
        num_skills: 要选择的技能数量
    
    Returns:
        技能名称列表
    """
    all_skills = []
    
    # 收集所有主动技能
    active_skills = skill_config.get("active_skills", {})
    for tier in ["advanced", "normal"]:
        if tier in active_skills:
            all_skills.extend(active_skills[tier].keys())
    
    # 收集所有被动技能
    passive_skills = skill_config.get("passive_skills", {})
    for tier in ["advanced", "normal"]:
        if tier in passive_skills:
            all_skills.extend(passive_skills[tier].keys())
    
    # 收集所有增益技能
    buff_skills = skill_config.get("buff_skills", {})
    for tier in ["advanced", "normal"]:
        if tier in buff_skills:
            all_skills.extend(buff_skills[tier].keys())
    
    # 随机选择
    if len(all_skills) < num_skills:
        return all_skills
    
    return random.sample(all_skills, num_skills)


def delete_existing_test_player():
    """删除现有的测试玩家数据"""
    print("清理现有测试玩家数据...")
    
    # 删除幻兽
    execute_update(
        "DELETE FROM player_beast WHERE user_id = %s",
        (TEST_USER_ID,)
    )
    
    # 删除玩家
    execute_update(
        "DELETE FROM player WHERE user_id = %s",
        (TEST_USER_ID,)
    )
    
    print(f"已清理 user_id={TEST_USER_ID} 的数据")


def create_test_player():
    """创建测试玩家"""
    print(f"创建测试玩家 (user_id={TEST_USER_ID})...")
    
    # 创建玩家（100级，战神阶）
    execute_insert(
        """
        INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (TEST_USER_ID, TEST_USERNAME, TEST_PASSWORD, TEST_NICKNAME, 100, 0, 100000)
    )
    
    print(f"  ✅ 玩家创建成功: {TEST_NICKNAME} (等级100)")


def create_test_beasts(skill_config):
    """创建两只测试幻兽并随机分配技能"""
    print("创建测试幻兽...")
    
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
    
    # 创建两只幻兽
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
        
        # 根据等级生成属性（100级）
        level = 100
        base_hp = level * 200 + random.randint(5000, 15000)
        base_attack = level * 30 + random.randint(500, 2000)
        base_defense = level * 25 + random.randint(400, 1800)
        base_speed = 100 + level * 10 + random.randint(-20, 50)
        
        if is_physical:
            physical_attack = base_attack
            magic_attack = base_attack // 3
            nature = "物系普攻"
        else:
            physical_attack = base_attack // 3
            magic_attack = base_attack
            nature = "法系普攻"
        
        # 幻兽信息
        beast_name = f"{TEST_NICKNAME}的幻兽{beast_num}"
        realm = random.choice(["神界", "天界", "凡界"])
        race = random.choice(["龙族", "飞禽", "虫族", "神兽", "魔族"])
        personality = random.choice(["勇敢", "冷静", "暴躁", "稳重", "狂暴"])
        
        # 资质值
        hp_aptitude = random.randint(1200, 1800)
        attack_aptitude = random.randint(1200, 1800)
        speed_aptitude = random.randint(1200, 1800)
        physical_defense_aptitude = random.randint(1200, 1800)
        magic_defense_aptitude = random.randint(1200, 1800)
        
        # 星数
        hp_star = random.randint(3, 7)
        attack_star = random.randint(3, 7)
        speed_star = random.randint(3, 7)
        physical_defense_star = random.randint(3, 7)
        magic_defense_star = random.randint(3, 7)
        
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
                TEST_USER_ID, beast_name, realm, race, level, nature, personality,
                base_hp, physical_attack, magic_attack, base_defense, base_defense, base_speed,
                base_hp + base_attack + base_defense * 2,  # 简单战力计算
                random.randint(90, 110),
                hp_aptitude, speed_aptitude, attack_aptitude,
                physical_defense_aptitude, magic_defense_aptitude,
                "10000/10000", skills_json, "", "",
                1, beast_num  # is_in_team=1, team_position=1或2
            )
        )
        
        print(f"  ✅ 幻兽{beast_num}创建成功: {beast_name}")
        print(f"     类型: {nature}, 技能: {', '.join(selected_skills)}")


def setup_tower_progress():
    """设置通天塔进度（需要至少101层才能镇妖101层）"""
    print("设置通天塔进度...")
    
    # 检查是否已有记录
    rows = execute_query(
        "SELECT id FROM tower_state WHERE user_id = %s AND tower_type = 'tongtian'",
        (TEST_USER_ID,)
    )
    
    if rows:
        # 更新进度
        execute_update(
            """
            UPDATE tower_state 
            SET current_floor = 120, max_floor_record = 120, today_count = 0
            WHERE user_id = %s AND tower_type = 'tongtian'
            """,
            (TEST_USER_ID,)
        )
    else:
        # 创建新记录
        execute_insert(
            """
            INSERT INTO tower_state (user_id, tower_type, current_floor, max_floor_record, today_count)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (TEST_USER_ID, "tongtian", 120, 120, 0)
        )
    
    print("  ✅ 通天塔进度已设置为120层")


def main():
    """主函数"""
    print("=" * 60)
    print("创建镇妖测试玩家")
    print("=" * 60)
    print()
    
    try:
        # 1. 加载技能配置
        print("加载技能配置...")
        skill_config = load_skill_config()
        print("  ✅ 技能配置加载成功")
        print()
        
        # 2. 清理现有数据
        delete_existing_test_player()
        print()
        
        # 3. 创建玩家
        create_test_player()
        print()
        
        # 4. 创建幻兽
        create_test_beasts(skill_config)
        print()
        
        # 5. 设置通天塔进度
        setup_tower_progress()
        print()
        
        # 6. 验证
        print("验证创建结果...")
        player_rows = execute_query(
            "SELECT user_id, nickname, level FROM player WHERE user_id = %s",
            (TEST_USER_ID,)
        )
        beast_rows = execute_query(
            "SELECT id, name, skills FROM player_beast WHERE user_id = %s AND is_in_team = 1",
            (TEST_USER_ID,)
        )
        
        if player_rows:
            player = player_rows[0]
            print(f"  ✅ 玩家: {player['nickname']} (等级{player['level']})")
        
        print(f"  ✅ 出战幻兽数量: {len(beast_rows)}")
        for beast in beast_rows:
            skills = json.loads(beast['skills']) if beast['skills'] else []
            print(f"     - {beast['name']}: {', '.join(skills) if skills else '无技能'}")
        
        print()
        print("=" * 60)
        print("创建完成！")
        print()
        print("下一步：运行以下脚本让该玩家占领第101层：")
        print("  python tests/Demon_suppression/occupy_floor_101.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 创建失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
