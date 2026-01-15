#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盟战功能测试数据生成脚本
生成测试用户、联盟、成员、报名、签到、战绩等数据
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from datetime import datetime, date, timedelta
import random

# 数据库配置
DB_CONFIG = {
    'host': '8.146.206.229',
    'user': 'root',
    'password': 'Wxs1230.0',
    'database': 'game_tower',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def create_test_players(conn, count=50):
    """创建测试玩家"""
    print(f"\n创建 {count} 个测试玩家...")
    # 测试账号统一密码
    TEST_PASSWORD = "123456"
    
    with conn.cursor() as cursor:
        for i in range(1, count + 1):
            user_id = 20000 + i
            username = f"test_war_{user_id}"
            nickname = f"测试玩家{i}"
            # 随机等级：1-60级，确保有40级以下和40级以上的玩家
            level = random.randint(1, 60)
            
            cursor.execute("""
                INSERT INTO player (user_id, username, password, nickname, level)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    username = VALUES(username),
                    password = VALUES(password),
                    nickname = VALUES(nickname),
                    level = VALUES(level)
            """, (user_id, username, TEST_PASSWORD, nickname, level))
        
        conn.commit()
        print(f"✓ 成功创建/更新 {count} 个测试玩家")
        print(f"  账号格式: test_war_20001 ~ test_war_20050")
        print(f"  统一密码: {TEST_PASSWORD}")

def create_test_alliances(conn, count=5):
    """创建测试联盟"""
    print(f"\n创建 {count} 个测试联盟...")
    alliance_ids = []
    with conn.cursor() as cursor:
        for i in range(1, count + 1):
            alliance_name = f"测试联盟{i}"
            leader_id = 20000 + i  # 每个联盟的盟主
            
            # 检查联盟是否已存在
            cursor.execute("SELECT id FROM alliances WHERE name = %s", (alliance_name,))
            existing = cursor.fetchone()
            
            if existing:
                alliance_id = existing['id']
                print(f"  联盟 '{alliance_name}' 已存在 (ID: {alliance_id})")
            else:
                # 创建联盟
                cursor.execute("""
                    INSERT INTO alliances (name, leader_id, level, funds, crystals, prosperity, war_honor, war_honor_history)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (alliance_name, leader_id, random.randint(1, 5), 
                      random.randint(10000, 100000), random.randint(1000, 10000),
                      random.randint(10000, 100000), random.randint(0, 10), random.randint(0, 50)))
                alliance_id = cursor.lastrowid
                print(f"  ✓ 创建联盟 '{alliance_name}' (ID: {alliance_id})")
            
            alliance_ids.append(alliance_id)
            
            # 确保盟主存在
            TEST_PASSWORD = "123456"
            cursor.execute("""
                INSERT INTO player (user_id, username, password, nickname, level)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    username = VALUES(username),
                    password = VALUES(password),
                    nickname = VALUES(nickname), 
                    level = VALUES(level)
            """, (leader_id, f"test_war_{leader_id}", TEST_PASSWORD, f"盟主{i}", random.randint(30, 60)))
            
            # 添加盟主为成员
            cursor.execute("""
                INSERT INTO alliance_members (alliance_id, user_id, role, contribution)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE role = VALUES(role)
            """, (alliance_id, leader_id, 1, 1000))  # role=1是盟主
            
            # 设置联盟建筑等级
            buildings = ['council', 'furnace', 'beast', 'warehouse']
            for building in buildings:
                cursor.execute("""
                    INSERT INTO alliance_buildings (alliance_id, building_key, level)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE level = VALUES(level)
                """, (alliance_id, building, random.randint(1, 5)))
        
        conn.commit()
        print(f"✓ 成功创建/更新 {len(alliance_ids)} 个测试联盟")
        return alliance_ids

def assign_members_to_alliances(conn, alliance_ids):
    """为联盟分配成员"""
    print(f"\n为联盟分配成员...")
    with conn.cursor() as cursor:
        # 获取所有测试玩家
        cursor.execute("SELECT user_id, level FROM player WHERE user_id >= 20000 AND user_id < 20100 ORDER BY user_id")
        players = cursor.fetchall()
        
        # 为每个联盟分配成员
        members_per_alliance = len(players) // len(alliance_ids)
        for idx, alliance_id in enumerate(alliance_ids):
            start_idx = idx * members_per_alliance
            end_idx = start_idx + members_per_alliance if idx < len(alliance_ids) - 1 else len(players)
            alliance_players = players[start_idx:end_idx]
            
            for player in alliance_players:
                user_id = player['user_id']
                level = player['level']
                
                # 根据等级分配军队：40级以上飞龙军(1)，40级及以下伏虎军(2)
                army_type = 1 if level > 40 else 2
                
                # 随机角色：大部分是普通成员(0)，少数是副盟主(2)或长老(3)
                role = 0
                if random.random() < 0.1:  # 10%概率是副盟主
                    role = 2
                elif random.random() < 0.2:  # 20%概率是长老
                    role = 3
                
                cursor.execute("""
                    INSERT INTO alliance_members (alliance_id, user_id, role, contribution, army_type)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        role = VALUES(role),
                        contribution = VALUES(contribution),
                        army_type = VALUES(army_type)
                """, (alliance_id, user_id, role, random.randint(100, 1000), army_type))
            
            print(f"  ✓ 联盟 {alliance_id} 分配了 {len(alliance_players)} 个成员")
        
        conn.commit()

def create_war_registrations(conn, alliance_ids):
    """创建盟战报名数据"""
    print(f"\n创建盟战报名数据...")
    with conn.cursor() as cursor:
        # 获取当前时间，判断是第一次还是第二次盟战
        now = datetime.utcnow()
        weekday = now.weekday()
        
        # 确定可报名的土地/据点
        # 飞龙军只能选择土地：1, 2
        # 伏虎军只能选择据点：3, 4
        
        for alliance_id in alliance_ids[:3]:  # 前3个联盟报名
            # 随机选择一个飞龙军土地和一个伏虎军据点
            dragon_land = random.choice([1, 2])
            tiger_land = random.choice([3, 4])
            
            # 飞龙军报名
            cursor.execute("""
                INSERT INTO alliance_land_registration 
                (land_id, alliance_id, army, registration_time, cost, status)
                VALUES (%s, %s, %s, NOW(), %s, %s)
                ON DUPLICATE KEY UPDATE 
                    army = VALUES(army),
                    registration_time = NOW(),
                    status = VALUES(status)
            """, (dragon_land, alliance_id, 'dragon', 0, 3))  # status=3表示已生效
            
            # 伏虎军报名
            cursor.execute("""
                INSERT INTO alliance_land_registration 
                (land_id, alliance_id, army, registration_time, cost, status)
                VALUES (%s, %s, %s, NOW(), %s, %s)
                ON DUPLICATE KEY UPDATE 
                    army = VALUES(army),
                    registration_time = NOW(),
                    status = VALUES(status)
            """, (tiger_land, alliance_id, 'tiger', 0, 3))
            
            print(f"  ✓ 联盟 {alliance_id} 报名了土地 {dragon_land} 和据点 {tiger_land}")
        
        conn.commit()

def create_war_checkins(conn, alliance_ids):
    """创建盟战签到数据"""
    print(f"\n创建盟战签到数据...")
    with conn.cursor() as cursor:
        now = datetime.utcnow()
        weekday = now.weekday()
        
        # 判断是第一次还是第二次盟战
        if weekday <= 2:  # 周一-周三
            war_phase = "first"
        else:  # 周四-周六
            war_phase = "second"
        
        checkin_date = now.date()
        
        for alliance_id in alliance_ids[:3]:  # 前3个联盟
            # 获取联盟成员
            cursor.execute("""
                SELECT user_id FROM alliance_members 
                WHERE alliance_id = %s AND army_type IN (1, 2)
                LIMIT 10
            """, (alliance_id,))
            members = cursor.fetchall()
            
            for member in members:
                user_id = member['user_id']
                # 随机决定是否签到（80%概率签到）
                if random.random() < 0.8:
                    cursor.execute("""
                        INSERT INTO alliance_war_checkin 
                        (alliance_id, user_id, war_phase, war_weekday, checkin_date, copper_reward)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE copper_reward = VALUES(copper_reward)
                    """, (alliance_id, user_id, war_phase, weekday, checkin_date, 30000))
            
            print(f"  ✓ 联盟 {alliance_id} 有 {len(members)} 个成员签到")
        
        conn.commit()

def create_war_battle_records(conn, alliance_ids):
    """创建盟战战绩数据"""
    print(f"\n创建盟战战绩数据...")
    with conn.cursor() as cursor:
        now = datetime.utcnow()
        war_date = now.date()
        weekday = now.weekday()
        
        if weekday <= 2:
            war_phase = "first"
        else:
            war_phase = "second"
        
        # 创建一些历史战绩
        for i in range(min(3, len(alliance_ids))):
            alliance_id = alliance_ids[i]
            # 随机选择一个对手联盟
            opponent_id = alliance_ids[(i + 1) % len(alliance_ids)]
            
            # 随机选择土地/据点
            land_id = random.choice([1, 2, 3, 4])
            army_type = 'dragon' if land_id <= 2 else 'tiger'
            
            # 随机胜负
            battle_result = 'win' if random.random() > 0.5 else 'lose'
            honor_gained = 1 if battle_result == 'win' else 0
            
            cursor.execute("""
                INSERT INTO alliance_war_battle_records 
                (alliance_id, opponent_alliance_id, land_id, army_type, war_phase, war_date, battle_result, honor_gained)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (alliance_id, opponent_id, land_id, army_type, war_phase, war_date, battle_result, honor_gained))
            
            print(f"  ✓ 创建战绩：联盟 {alliance_id} vs 联盟 {opponent_id} ({battle_result})")
        
        conn.commit()

def create_season_scores(conn, alliance_ids):
    """创建赛季积分数据"""
    print(f"\n创建赛季积分数据...")
    with conn.cursor() as cursor:
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'alliance_war_scores'")
        if not cursor.fetchone():
            print("  alliance_war_scores表不存在，跳过创建赛季积分数据")
            return
        
        # 当前赛季
        season_key = datetime.utcnow().strftime("%Y-%m")
        
        for i, alliance_id in enumerate(alliance_ids):
            # 给每个联盟分配不同的积分，用于测试排行
            score = (len(alliance_ids) - i) * 5 + random.randint(0, 10)
            
            try:
                cursor.execute("""
                    INSERT INTO alliance_war_scores (alliance_id, season_key, score)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE score = VALUES(score)
                """, (alliance_id, season_key, score))
                print(f"  ✓ 联盟 {alliance_id} 赛季积分: {score}")
            except Exception as e:
                print(f"  ✗ 联盟 {alliance_id} 创建赛季积分失败: {e}")
        
        conn.commit()

def create_land_occupations(conn, alliance_ids):
    """创建土地占领数据"""
    print(f"\n创建土地占领数据...")
    with conn.cursor() as cursor:
        now = datetime.utcnow()
        weekday = now.weekday()
        
        if weekday <= 2:
            war_phase = "first"
        else:
            war_phase = "second"
        
        war_date = now.date()
        
        # 为每个土地/据点分配占领联盟
        lands = [1, 2, 3, 4]
        for land_id in lands:
            # 随机选择一个联盟占领
            occupier_id = random.choice(alliance_ids)
            
            cursor.execute("""
                INSERT INTO alliance_land_occupation (land_id, alliance_id, war_phase, war_date)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    alliance_id = VALUES(alliance_id),
                    war_phase = VALUES(war_phase),
                    war_date = VALUES(war_date)
            """, (land_id, occupier_id, war_phase, war_date))
            
            print(f"  ✓ 土地 {land_id} 被联盟 {occupier_id} 占领")
        
        conn.commit()

def main():
    print("=" * 60)
    print("盟战功能测试数据生成脚本")
    print("=" * 60)
    
    conn = None
    try:
        conn = get_connection()
        print("\n✓ 数据库连接成功")
        
        # 1. 创建测试玩家
        create_test_players(conn, count=50)
        
        # 2. 创建测试联盟
        alliance_ids = create_test_alliances(conn, count=5)
        
        # 3. 分配成员到联盟
        assign_members_to_alliances(conn, alliance_ids)
        
        # 4. 创建盟战报名数据
        create_war_registrations(conn, alliance_ids)
        
        # 5. 创建盟战签到数据
        create_war_checkins(conn, alliance_ids)
        
        # 6. 创建盟战战绩数据
        create_war_battle_records(conn, alliance_ids)
        
        # 7. 创建赛季积分数据
        create_season_scores(conn, alliance_ids)
        
        # 8. 创建土地占领数据
        create_land_occupations(conn, alliance_ids)
        
        print("\n" + "=" * 60)
        print("测试数据生成完成！")
        print("=" * 60)
        print("\n测试账号信息：")
        print("  测试玩家ID范围: 20001-20050")
        print("  测试联盟: 测试联盟1-5")
        print("  盟主ID: 20001-20005")
        print("\n可以使用以下账号测试：")
        print("  - 登录任意测试玩家账号（user_id: 20001-20050）")
        print("  - 查看盟战信息、报名、签到等功能")
        print("  - 查看盟战排行榜、战绩等")
        print()
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
