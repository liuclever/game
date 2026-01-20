"""
为 user_id=20052 生成“正常游玩”可用的测试数据，并用于验证：
幻兽等级不能超过玩家等级 + 5（玩家30级 => 幻兽最多35级），第三次升级会提示不能升级。

运行（项目根目录）：
    python -m scripts.setup_beast_level_cap_user_20052
"""

from __future__ import annotations

import json
from pathlib import Path

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo, PlayerBeastData
from domain.entities.immortalize_pool import ImmortalizePool
from infrastructure.db.immortalize_pool_repo_mysql import MySQLImmortalizePoolRepo


USER_ID = 20052
USERNAME = "u20052"
PASSWORD = "pw20052"
NICKNAME = "封顶测试20052"

PLAYER_LEVEL = 30
BEAST_TEMPLATE_ID = 1
BEAST_NICKNAME = "[封顶测试]小黑鼠"
BEAST_NAME = "小黑鼠"
BEAST_REALM = "地界"
BEAST_LEVEL_START = 33  # 33 -> 34 -> 35，第三次就会被限制（玩家30 + 5 = 35）


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_beast_level_exp() -> dict:
    path = _get_repo_root() / "configs" / "beast_level_up_exp.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def upsert_player():
    # 尽量只用确定存在的字段，兼容不同库版本
    sql = """
        INSERT INTO player (
            user_id, username, password,
            nickname, level, exp,
            gold, silver_diamond, yuanbao, dice,
            location, vip_level, vip_exp
        )
        VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            username = VALUES(username),
            password = VALUES(password),
            nickname = VALUES(nickname),
            level = VALUES(level),
            exp = VALUES(exp),
            gold = VALUES(gold),
            silver_diamond = VALUES(silver_diamond),
            yuanbao = VALUES(yuanbao),
            dice = VALUES(dice),
            location = VALUES(location),
            vip_level = VALUES(vip_level),
            vip_exp = VALUES(vip_exp),
            updated_at = CURRENT_TIMESTAMP
    """
    execute_update(
        sql,
        (
            USER_ID,
            USERNAME,
            PASSWORD,
            NICKNAME,
            PLAYER_LEVEL,
            0,
            50000,  # 铜钱（正常游玩可用）
            0,
            0,
            0,
            "落龙镇",
            0,
            0,
        ),
    )


def upsert_pool():
    pool_repo = MySQLImmortalizePoolRepo()
    pool = pool_repo.get_by_user_id(USER_ID)
    if pool is None:
        pool = ImmortalizePool(
            user_id=USER_ID,
            pool_level=1,
            current_exp=0,
            formation_level=0,
            formation_started_at=None,
            formation_ends_at=None,
            formation_last_grant_at=None,
            created_at=None,
            updated_at=None,
        )

    # 给足够的化仙池经验，支持多次分配
    pool.pool_level = 1
    pool.current_exp = 500000
    pool_repo.upsert(pool)


def upsert_test_beast() -> int:
    repo = MySQLPlayerBeastRepo()

    # 先查是否已经存在这只测试幻兽（避免重复插入）
    rows = execute_query(
        "SELECT id FROM player_beast WHERE user_id = %s AND nickname = %s LIMIT 1",
        (USER_ID, BEAST_NICKNAME),
    )
    if rows:
        beast_id = int(rows[0]["id"])
        b = repo.get_by_id(beast_id)
        if b is None:
            # 理论上不会发生，兜底重新创建
            rows = []
        else:
            b.template_id = BEAST_TEMPLATE_ID
            b.name = BEAST_NAME
            b.nickname = BEAST_NICKNAME
            b.realm = BEAST_REALM
            b.race = "兽族"
            b.level = BEAST_LEVEL_START
            b.exp = 0
            b.attack_type = "physical"
            b.nature = "物系普攻"
            # 给一组“正常范围”的资质（参考模板1地界 min/max）
            b.hp_aptitude = 500
            b.speed_aptitude = 800
            b.physical_attack_aptitude = 650
            b.magic_attack_aptitude = 0
            b.physical_defense_aptitude = 650
            b.magic_defense_aptitude = 600
            b.growth_rate = 840
            # 放进战斗队更符合正常游玩（但不影响升级测试）
            b.is_in_team = 1
            b.team_position = 0
            repo.save(b)
            return beast_id

    # 不存在则创建
    b = PlayerBeastData(
        id=None,  # 关键：PlayerBeastData 默认 id=0，会导致 repo.save 走 UPDATE；这里必须显式设为 None 才会 INSERT
        user_id=USER_ID,
        template_id=BEAST_TEMPLATE_ID,
        name=BEAST_NAME,
        nickname=BEAST_NICKNAME,
        realm=BEAST_REALM,
        race="兽族",
        level=BEAST_LEVEL_START,
        exp=0,
        attack_type="physical",
        nature="物系普攻",
        growth_rate=840,
        hp_aptitude=500,
        speed_aptitude=800,
        physical_attack_aptitude=650,
        magic_attack_aptitude=0,
        physical_defense_aptitude=650,
        magic_defense_aptitude=600,
        is_in_team=1,
        team_position=0,
        skills=["高级冲撞", "敏捷"],
    )
    repo.save(b)
    return int(b.id or 0)


def main():
    level_cfg = _load_beast_level_exp()
    exp_map = level_cfg.get("exp_to_next_level", {}) or {}

    # 33->34 需要 exp_to_next_level["33"]，34->35 需要 exp_to_next_level["34"]
    exp_33 = int(exp_map.get("33", 0) or 0)
    exp_34 = int(exp_map.get("34", 0) or 0)

    upsert_player()
    upsert_pool()
    beast_id = upsert_test_beast()

    print("=== 测试数据已准备完毕 ===")
    print(f"user_id: {USER_ID}")
    print(f"登录账号: username={USERNAME}, password={PASSWORD}")
    print(f"玩家等级: Lv.{PLAYER_LEVEL}")
    print(f"测试幻兽: beast_id={beast_id}, nickname={BEAST_NICKNAME}, level=Lv.{BEAST_LEVEL_START}")
    print(f"化仙池经验: 已设置为 500000")
    print("")
    print("用于两次各升1级的推荐分配经验：")
    print(f"- 第一次（33->34）：exp = {exp_33}")
    print(f"- 第二次（34->35）：exp = {exp_34}")
    print("第三次再分配任意正数 exp，将提示“已达上限（玩家等级+5）”。")


if __name__ == "__main__":
    main()


