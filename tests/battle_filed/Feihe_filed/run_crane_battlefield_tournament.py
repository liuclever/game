"""让31个飞鹤战场测试玩家报名并运行比赛，生成战报文件。

运行方式：
    python tests/battle_filed/Feihe_filed/run_crane_battlefield_tournament.py

功能：
    - 让31个飞鹤战场测试玩家（user_id: 4000-4030）报名飞鹤战场
    - 运行一整期淘汰赛
    - 生成文本战报文件到 battle_report 目录

前置条件：
    - 需要先运行 create_31_crane_battlefield_players.py 创建测试玩家

注意：
    - 本脚本会清空当日飞鹤战场的报名记录和旧战报
    - 请勿在生产环境运行
"""

import sys
from pathlib import Path
from typing import List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.db.connection import execute_query, execute_update
from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.db.player_repo_mysql import MySQLPlayerRepo
from infrastructure.db.battlefield_repo_mysql import MySQLBattlefieldBattleRepo
from application.services.battlefield_service import BattlefieldService, BATTLEFIELD_TYPES

# 测试玩家ID范围
START_USER_ID = 4000
END_USER_ID = 4030
NUM_PLAYERS = 31

# 战场类型
BATTLEFIELD_TYPE = "crane"
REPORT_DIR = Path(__file__).parent / "battle_report"


def check_players_exist() -> List[int]:
    """检查测试玩家是否存在并返回user_id列表"""
    print("检查测试玩家...")
    
    rows = execute_query(
        """
        SELECT user_id, nickname, level
        FROM player
        WHERE user_id BETWEEN %s AND %s
        ORDER BY user_id
        """,
        (START_USER_ID, END_USER_ID)
    )
    
    if len(rows) < NUM_PLAYERS:
        raise ValueError(
            f"测试玩家不足，需要 {NUM_PLAYERS} 个，当前仅找到 {len(rows)} 个。"
            "请先运行 create_31_crane_battlefield_players.py 创建测试玩家。"
        )
    
    user_ids = [row["user_id"] for row in rows]
    
    # 检查等级范围
    min_lv, max_lv = BATTLEFIELD_TYPES[BATTLEFIELD_TYPE]["level_range"]
    out_of_range = [r for r in rows if not (min_lv <= r["level"] <= max_lv)]
    if out_of_range:
        print(f"  ⚠️  警告：{len(out_of_range)} 个玩家等级不在{min_lv}-{max_lv}范围内")
    
    # 检查是否有出战幻兽
    for uid in user_ids:
        beast_count = execute_query(
            "SELECT COUNT(*) as cnt FROM player_beast WHERE user_id = %s AND is_in_team = 1",
            (uid,)
        )
        count = beast_count[0]["cnt"] if beast_count else 0
        if count == 0:
            raise ValueError(f"玩家 {uid} 没有出战幻兽，请先创建测试玩家和幻兽")
    
    print(f"  ✅ 找到 {len(user_ids)} 个测试玩家")
    return user_ids


def signup_players(user_ids: List[int]):
    """为所有测试玩家报名飞鹤战场"""
    print(f"\n为 {len(user_ids)} 个玩家报名飞鹤战场...")
    
    # 仅清理测试账号的报名记录，保留前端已报名的真实玩家
    execute_update(
        """
        DELETE FROM battlefield_signup
        WHERE battlefield_type = %s
          AND signup_date = CURDATE()
          AND user_id BETWEEN %s AND %s
        """,
        (BATTLEFIELD_TYPE, START_USER_ID, END_USER_ID)
    )
    print("  ✅ 已清空测试账号的当日报名记录（保留其他玩家）")
    
    # 为每个玩家写入报名记录
    for uid in user_ids:
        execute_update(
            """
            INSERT INTO battlefield_signup (user_id, battlefield_type, signup_date)
            VALUES (%s, %s, CURDATE())
            ON DUPLICATE KEY UPDATE signup_time = NOW()
            """,
            (uid, BATTLEFIELD_TYPE)
        )
    
    print(f"  ✅ 已为 {len(user_ids)} 个玩家报名飞鹤战场")


def run_tournament():
    """运行飞鹤战场淘汰赛"""
    print("\n开始运行飞鹤战场淘汰赛...")
    
    # 清空旧战报（仅飞鹤战场）
    execute_update(
        "DELETE FROM battlefield_battle_log WHERE battlefield_type = %s",
        (BATTLEFIELD_TYPE,)
    )
    print("  ✅ 已清空旧战报记录")
    
    # 创建服务实例
    player_repo = MySQLPlayerRepo()
    beast_repo = MySQLPlayerBeastRepo()
    battle_repo = MySQLBattlefieldBattleRepo()
    
    service = BattlefieldService(
        player_repo=player_repo,
        player_beast_repo=beast_repo,
        battle_repo=battle_repo,
    )
    
    # 运行比赛
    result = service.run_tournament(BATTLEFIELD_TYPE)
    
    if not result["ok"]:
        raise ValueError(f"古战场运行失败: {result.get('error', '未知错误')}")
    
    print(f"  ✅ 比赛完成")
    print(f"     期数: {result['period']}")
    print(f"     参赛人数: {result['total_players']}")
    print(f"     总轮数: {result['total_rounds']}")
    print(f"     冠军: {result['champion_name']} (user_id: {result['champion_id']})")
    print(f"     冠军击杀数: {result['champion_wins']}")
    
    return result


def generate_battle_reports(period: int):
    """生成文本战报文件"""
    print(f"\n生成战报文件（期数: {period}）...")
    
    battle_repo = MySQLBattlefieldBattleRepo()
    logs = battle_repo.get_matches_for_period(BATTLEFIELD_TYPE, period)
    
    if not logs:
        print("  ⚠️  警告：未找到战报记录")
        return
    
    print(f"  找到 {len(logs)} 场对战")
    
    # 创建战报目录
    REPORT_DIR.mkdir(exist_ok=True, parents=True)
    
    # 生成文本文件
    for log in logs:
        filename = f"period{period}_round{log.round_num}_match{log.match_num}_id{log.id}.txt"
        path = REPORT_DIR / filename
        
        data = log.battle_data or {}
        battles = data.get("battles", [])
        
        with path.open("w", encoding="utf-8") as f:
            f.write(
                f"期数: {log.period}\n"
                f"战场: {log.battlefield_type}\n"
                f"轮次: 第{log.round_num}轮 第{log.match_num}场\n"
                f"对阵: {log.first_user_name} VS {log.second_user_name}\n"
                f"结果: {'胜利' if log.is_first_win else '失败'} (针对左侧玩家)\n\n"
            )
            
            for battle in battles:
                f.write(f"[第{battle.get('battle_num', 1)}战] {battle.get('result', '')}\n")
                for r in battle.get("rounds", []):
                    f.write(f"[回合{r.get('round')}]: {r.get('action')}\n")
                f.write("\n")
    
    print(f"  ✅ 已生成 {len(logs)} 个战报文件到 {REPORT_DIR}")


def main():
    """主函数"""
    print("=" * 60)
    print("飞鹤战场：报名并运行比赛")
    print("=" * 60)
    print()
    
    try:
        # 1. 检查测试玩家
        user_ids = check_players_exist()
        print()
        
        # 2. 报名
        signup_players(user_ids)
        print()
        
        # 3. 运行比赛
        result = run_tournament()
        print()
        
        # 4. 生成战报
        generate_battle_reports(result["period"])
        print()
        
        print("=" * 60)
        print("完成！")
        print()
        print("比赛结果：")
        print(f"  - 期数: {result['period']}")
        print(f"  - 参赛人数: {result['total_players']}")
        print(f"  - 总轮数: {result['total_rounds']}")
        print(f"  - 冠军: {result['champion_name']} (user_id: {result['champion_id']})")
        print(f"  - 冠军击杀数: {result['champion_wins']}")
        print()
        print(f"战报文件已保存到: {REPORT_DIR}")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 操作失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
