"""创建用于前端登录的测试玩家3（等级30，携带两只幻兽，随机技能）。

运行方式：
    python tests/battle_filed/tiger_filed/create_information/create_front_player3.py

功能：
    - 创建一个玩家（user_id: 2031，账号：front_test3，密码：123456，等级30）
    - 创建两只出战幻兽（is_in_team=1），随机分配技能

注意：
    - 会删除 user_id=2031 的现有玩家与幻兽记录，请勿在生产环境运行
"""

import sys
import json
import random
from pathlib import Path

# 添加项目根目录到路径（tests/battle_filed/tiger_filed/create_information -> 根目录需向上5级）
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_update, execute_insert

USER_ID = 2031
USERNAME = "front_test3"
PASSWORD = "123456"
NICKNAME = "前端测试玩家3"
LEVEL = 30  # 猛虎战场范围


def load_skill_config():
    path = project_root / "configs" / "skills.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def delete_existing():
    execute_update("DELETE FROM player_beast WHERE user_id = %s", (USER_ID,))
    execute_update("DELETE FROM player WHERE user_id = %s", (USER_ID,))
    print(f"已清理 user_id={USER_ID} 的旧数据")


def create_player():
    execute_insert(
        """
        INSERT INTO player (user_id, username, password, nickname, level, exp, gold)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (USER_ID, USERNAME, PASSWORD, NICKNAME, LEVEL, 0, 10000),
    )
    print(f"✅ 玩家创建成功：{NICKNAME} (等级{LEVEL})")


def create_beasts(skill_config):
    active = []
    passive = []
    buff = []
    for tier in ["advanced", "normal"]:
        active.extend(list(skill_config.get("active_skills", {}).get(tier, {}).keys()))
        passive.extend(list(skill_config.get("passive_skills", {}).get(tier, {}).keys()))
        buff.extend(list(skill_config.get("buff_skills", {}).get(tier, {}).keys()))

    for idx in range(1, 3):
        skills = []
        if active:
            skills.extend(random.sample(active, min(len(active), random.randint(1, 3))))
        if passive and random.random() < 0.7:
            num = random.randint(0, 2)
            if num > 0:
                skills.extend(random.sample(passive, min(len(passive), num)))
        if buff and random.random() < 0.6:
            num = random.randint(0, 2)
            if num > 0:
                skills.extend(random.sample(buff, min(len(buff), num)))
        skills = list(set(skills))
        skills_json = json.dumps(skills, ensure_ascii=False)

        base_hp = LEVEL * 120 + random.randint(3000, 8000)
        base_attack = LEVEL * 12 + random.randint(200, 600)
        base_defense = LEVEL * 10 + random.randint(150, 500)
        base_speed = 60 + LEVEL * 5 + random.randint(-10, 20)

        is_physical = random.choice([True, False])
        if is_physical:
            physical_attack = base_attack
            magic_attack = base_attack // 2
            nature = "物系普攻"
        else:
            physical_attack = base_attack // 2
            magic_attack = base_attack
            nature = "法系普攻"

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
                USER_ID,
                f"{NICKNAME}的幻兽{idx}",
                random.choice(["凡界", "天界", "神界"]),
                random.choice(["龙族", "飞禽", "虫族", "神兽", "魔族"]),
                LEVEL,
                nature,
                random.choice(["勇敢", "冷静", "暴躁", "稳重", "狂暴"]),
                base_hp,
                physical_attack,
                magic_attack,
                base_defense,
                base_defense,
                base_speed,
                base_hp + base_attack + base_defense * 2,
                random.randint(80, 100),
                random.randint(900, 1300),
                random.randint(900, 1300),
                random.randint(900, 1300),
                random.randint(900, 1300),
                random.randint(900, 1300),
                "10000/10000",
                skills_json,
                "",
                "",
                1,
                idx,
            ),
        )
        print(f"✅ 幻兽{idx} 创建成功，技能: {', '.join(skills) if skills else '无'}")


def main():
    print("=" * 60)
    print("创建前端登录测试玩家3（user_id=2031，等级30）")
    print("=" * 60)
    try:
        delete_existing()
        create_player()
        skill_cfg = load_skill_config()
        create_beasts(skill_cfg)
        print("\n完成！账号: front_test3 / 123456")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
