#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建联盟精英争霸赛测试数据
用于验证联盟积分排名和往届战绩功能
"""
import sys
import os
import io
from datetime import datetime, timedelta

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.db.connection import execute_update, execute_query, execute_insert

def get_or_create_alliance(name, leader_id):
    """获取或创建联盟"""
    # 确保玩家存在
    existing = execute_query("SELECT user_id FROM player WHERE user_id = %s", (leader_id,))
    if not existing:
        execute_insert("INSERT INTO player (user_id, username, nickname) VALUES (%s, %s, %s)", 
                      (leader_id, f"user_{leader_id}", f"玩家{leader_id}"))
    
    # 检查联盟是否存在
    rows = execute_query("SELECT id FROM alliances WHERE name = %s", (name,))
    if rows:
        alliance_id = rows[0]['id']
        # 更新盟主
        execute_update("UPDATE alliances SET leader_id = %s WHERE id = %s", (leader_id, alliance_id))
    else:
        # 创建联盟
        alliance_id = execute_insert(
            "INSERT INTO alliances (name, leader_id, level, exp, funds, crystals, prosperity, notice) VALUES (%s, %s, 1, 0, 0, 0, 0, %s)",
            (name, leader_id, f"测试联盟-{name}")
        )
    
    # 确保盟主是成员
    execute_update(
        "INSERT INTO alliance_members (alliance_id, user_id, role, contribution) VALUES (%s, %s, 1, 1000) ON DUPLICATE KEY UPDATE alliance_id = VALUES(alliance_id), role = VALUES(role)",
        (alliance_id, leader_id)
    )
    
    return alliance_id

def create_test_data():
    """创建测试数据"""
    print("=" * 60)
    print("创建联盟精英争霸赛测试数据")
    print("=" * 60)
    
    # 1. 创建测试联盟
    print("\n1. 创建测试联盟...")
    alliances = []
    alliance_data = [
        ("『幻閣不滅◇君臨天下』", 4053, 240),  # 第1名，威望240
        ("暗河|风起云涌", 4054, 118),  # 第2名，威望118
        ("明月", 4055, 86),  # 第3名，威望86
        ("【情义世家】", 4056, 54),  # 第4名，威望54
        ("ぞ紫月遮天づ", 4057, 48),  # 第5名，威望48
        ("玖幽之都", 4058, 41),  # 第6名，威望41
        ("手牵手,一起走。", 4059, 37),  # 第7名，威望37
        ("蹲街_浅/唱_季沫✨", 4060, 34),  # 第8名，威望34
        ("X、低调の", 4061, 17),  # 第9名，威望17
        ("恶人谷❄", 4062, 14),  # 第10名，威望14
    ]
    
    for name, leader_id, prestige in alliance_data:
        alliance_id = get_or_create_alliance(name, leader_id)
        alliances.append({
            "id": alliance_id,
            "name": name,
            "leader_id": leader_id,
            "prestige": prestige
        })
        print(f"  [成功] 创建联盟: {name} (ID: {alliance_id}, 盟主: {leader_id})")
    
    # 2. 创建测试届次（2026-01-11届，已结束）
    print("\n2. 创建测试届次...")
    session_key = "2026-01-11"
    session_name = f"第{session_key}届"
    
    # 检查届次是否存在
    rows = execute_query("SELECT id FROM alliance_competition_sessions WHERE session_key = %s", (session_key,))
    if rows:
        session_id = rows[0]['id']
        print(f"  [成功] 届次已存在: {session_name} (ID: {session_id})")
    else:
        # 创建届次（已结束）
        monday = datetime(2026, 1, 11, 0, 0, 0)
        session_id = execute_insert(
            """INSERT INTO alliance_competition_sessions 
               (session_key, session_name, phase, registration_start, registration_end,
                signup_start, signup_end, battle_date, battle_start, battle_end, result_published_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                session_key,
                session_name,
                'finished',
                monday,
                monday + timedelta(days=2, hours=23, minutes=59),
                monday + timedelta(days=3),
                monday + timedelta(days=6, hours=20),
                monday + timedelta(days=6),
                monday + timedelta(days=6, hours=20),
                monday + timedelta(days=6, hours=22),
                monday + timedelta(days=6, hours=22),
            )
        )
        print(f"  [成功] 创建届次: {session_name} (ID: {session_id})")
    
    # 3. 创建联盟报名记录
    print("\n3. 创建联盟报名记录...")
    for alliance in alliances:
        execute_update(
            """INSERT INTO alliance_competition_registrations 
               (session_id, alliance_id, registered_by, registered_at, status)
               VALUES (%s, %s, %s, %s, 1)
               ON DUPLICATE KEY UPDATE status = 1""",
            (session_id, alliance['id'], alliance['leader_id'], datetime.now())
        )
    print(f"  [成功] 创建了 {len(alliances)} 个联盟的报名记录")
    
    # 4. 创建成员签到记录（为每个联盟创建一些成员）
    print("\n4. 创建成员签到记录...")
    team_keys = ['calf_tiger', 'white_tiger', 'azure_dragon', 'vermillion_bird', 'black_tortoise', 'god_of_war']
    team_names = ['犊虎', '白虎', '青龙', '朱雀', '玄武', '战神']
    
    user_id_counter = 5000
    for alliance in alliances:
        # 为每个联盟创建3-5个成员，分配到不同战队
        num_members = 4
        for i in range(num_members):
            user_id = user_id_counter
            user_id_counter += 1
            
            # 确保玩家存在（先检查，不存在则插入）
            existing = execute_query("SELECT user_id FROM player WHERE user_id = %s", (user_id,))
            nickname = f"{alliance['name']}成员{i+1}"
            level = 30 + i * 10
            
            if not existing:
                # 检查 username 是否已存在，如果存在则使用不同的 username
                username = f"user_{user_id}"
                execute_insert(
                    "INSERT INTO player (user_id, username, nickname, level) VALUES (%s, %s, %s, %s)",
                    (user_id, username, nickname, level)
                )
            else:
                # 更新玩家信息
                execute_update(
                    "UPDATE player SET nickname = %s, level = %s WHERE user_id = %s",
                    (nickname, level, user_id)
                )
            
            # 加入联盟
            execute_update(
                "INSERT INTO alliance_members (alliance_id, user_id, role, contribution) VALUES (%s, %s, 0, 100) ON DUPLICATE KEY UPDATE alliance_id = VALUES(alliance_id)",
                (alliance['id'], user_id)
            )
            
            # 根据等级分配到战队
            level = 30 + i * 10
            if level < 40:
                team_key = 'calf_tiger'
            elif level < 50:
                team_key = 'white_tiger'
            elif level < 60:
                team_key = 'azure_dragon'
            elif level < 70:
                team_key = 'vermillion_bird'
            elif level < 80:
                team_key = 'black_tortoise'
            else:
                team_key = 'god_of_war'
            
            # 创建签到记录
            execute_update(
                """INSERT INTO alliance_competition_signups 
                   (session_id, alliance_id, user_id, team_key, signed_at, status)
                   VALUES (%s, %s, %s, %s, %s, 1)
                   ON DUPLICATE KEY UPDATE status = 1""",
                (session_id, alliance['id'], user_id, team_key, datetime.now())
            )
    print(f"  [成功] 创建了成员签到记录")
    
    # 5. 创建战斗记录（为第2名联盟创建各战队的战斗记录）
    print("\n5. 创建战斗记录...")
    battle_rounds = [
        (1, "第1轮"),
        (2, "第2轮"),
        (3, "第3轮"),
    ]
    
    # 为第2名联盟（暗河|风起云涌）创建战斗记录
    test_alliance = alliances[1]  # 暗河|风起云涌
    opponent_alliances = [
        alliances[2],  # 明月
        alliances[3],  # 【情义世家】
        alliances[0],  # 『幻閣不滅◇君臨天下』
    ]
    
    # 为犊虎队创建战斗记录（3轮）
    for round_num, (round_id, round_name) in enumerate(battle_rounds, 1):
        opponent = opponent_alliances[round_num - 1]
        is_win = round_num < 3  # 前两轮胜，第三轮负
        
        battle_id = execute_insert(
            """INSERT INTO alliance_competition_battles 
               (session_id, round, team_key, alliance_id, opponent_alliance_id, battle_result, battle_time)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                session_id,
                round_id,
                'calf_tiger',
                test_alliance['id'],
                opponent['id'],
                'win' if is_win else 'lose',
                datetime.now() - timedelta(days=7-round_id)
            )
        )
    
    # 为其他战队也创建一些战斗记录
    team_battles = {
        'white_tiger': [(1, alliances[2], True), (2, alliances[3], True)],  # 白虎队：2轮，都胜
        'azure_dragon': [(1, alliances[2], True)],  # 青龙队：1轮，胜
        'vermillion_bird': [(1, alliances[2], True), (2, alliances[3], True), (3, alliances[0], False)],  # 朱雀队：3轮，前两轮胜，第三轮负
        'god_of_war': [(1, alliances[2], True), (2, alliances[3], True), (3, alliances[0], True), (4, alliances[0], True)],  # 战神队：4轮，都胜（冠军）
    }
    
    for team_key, battles in team_battles.items():
        for round_id, opponent, is_win in battles:
            execute_insert(
                """INSERT INTO alliance_competition_battles 
                   (session_id, round, team_key, alliance_id, opponent_alliance_id, battle_result, battle_time)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (
                    session_id,
                    round_id,
                    team_key,
                    test_alliance['id'],
                    opponent['id'],
                    'win' if is_win else 'lose',
                    datetime.now() - timedelta(days=7-round_id)
                )
            )
    
    print(f"  [成功] 为联盟 {test_alliance['name']} 创建了各战队的战斗记录")
    
    # 6. 创建战队积分记录
    print("\n6. 创建战队积分记录...")
    # 为第2名联盟创建各战队的最终排名
    team_final_ranks = {
        'calf_tiger': 4,  # 犊虎队荣誉晋级4强
        'white_tiger': 4,  # 白虎队荣誉晋级4强
        'azure_dragon': 8,  # 青龙队荣誉晋级8强
        'vermillion_bird': 2,  # 朱雀队荣誉晋级2强
        'black_tortoise': None,
        'god_of_war': 1,  # 战神队荣誉获得冠军
    }
    
    for alliance in alliances[:3]:  # 只为前3个联盟创建战队积分
        for team_key, final_rank in team_final_ranks.items():
            if final_rank:
                team_score = {
                    1: 100,  # 冠军
                    2: 80,   # 2强
                    4: 50,   # 4强
                    8: 30,   # 8强
                }.get(final_rank, 10)
                
                execute_update(
                    """INSERT INTO alliance_competition_scores 
                       (session_id, alliance_id, team_key, team_score, team_rank, team_final_rank)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE 
                       team_score = VALUES(team_score),
                       team_rank = VALUES(team_rank),
                       team_final_rank = VALUES(team_final_rank)""",
                    (session_id, alliance['id'], team_key, team_score, final_rank, final_rank)
                )
    print(f"  [成功] 创建了战队积分记录")
    
    # 7. 创建个人积分记录（为第2名联盟创建2个进入8强的精英）
    print("\n7. 创建个人积分记录...")
    test_alliance = alliances[1]  # 暗河|风起云涌
    
    # 获取该联盟的签到成员
    signups = execute_query(
        "SELECT user_id, team_key FROM alliance_competition_signups WHERE session_id = %s AND alliance_id = %s AND status = 1 LIMIT 2",
        (session_id, test_alliance['id'])
    )
    
    for idx, signup in enumerate(signups, 1):
        user_id = signup['user_id']
        team_key = signup['team_key']
        personal_score = 50 - idx * 5
        personal_rank = idx + 5  # 第6名和第7名
        
        execute_update(
            """INSERT INTO alliance_competition_personal_scores 
               (session_id, user_id, alliance_id, team_key, personal_score, personal_rank, eliminated_count)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE 
               personal_score = VALUES(personal_score),
               personal_rank = VALUES(personal_rank),
               eliminated_count = VALUES(eliminated_count)""",
            (session_id, user_id, test_alliance['id'], team_key, personal_score, personal_rank, idx)
        )
    print(f"  [成功] 为联盟 {test_alliance['name']} 创建了2个进入8强的精英记录")
    
    # 8. 创建联盟威望记录（按威望排序）
    print("\n8. 创建联盟威望记录...")
    for rank, alliance in enumerate(alliances, 1):
        execute_update(
            """INSERT INTO alliance_competition_prestige 
               (session_id, alliance_id, prestige, alliance_rank)
               VALUES (%s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE 
               prestige = VALUES(prestige),
               alliance_rank = VALUES(alliance_rank)""",
            (session_id, alliance['id'], alliance['prestige'], rank)
        )
    print(f"  [成功] 创建了 {len(alliances)} 个联盟的威望记录")
    
    print("\n" + "=" * 60)
    print("测试数据创建完成！")
    print("=" * 60)
    print(f"\n测试数据摘要:")
    print(f"  - 届次: {session_name} (ID: {session_id})")
    print(f"  - 联盟数量: {len(alliances)}")
    print(f"  - 测试联盟（第2名）: {alliances[1]['name']} (ID: {alliances[1]['id']})")
    print(f"\n可以测试的功能:")
    print(f"  1. 联盟积分排行 - 查看所有联盟的威望排名")
    print(f"  2. 往届战绩 - 查看联盟 {alliances[1]['name']} 的战绩")
    print("=" * 60)

if __name__ == "__main__":
    try:
        create_test_data()
    except Exception as e:
        print(f"\n[错误] 创建测试数据失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
