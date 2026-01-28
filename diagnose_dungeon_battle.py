"""诊断副本战斗数据问题"""
import sys
sys.path.insert(0, '.')

from infrastructure.db.player_repo_mysql import execute_query
import json

def diagnose_dungeon_battle():
    """诊断副本战斗相关的数据"""
    
    print("=" * 70)
    print("副本战斗数据诊断")
    print("=" * 70)
    
    # 1. 检查副本配置文件
    print("\n1. 检查副本配置文件...")
    try:
        with open('configs/dungeon_beasts.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        dungeons = config.get('dungeons', {})
        print(f"   ✓ 配置文件加载成功，共 {len(dungeons)} 个副本")
        
        # 检查第一个副本的配置
        if dungeons:
            first_dungeon_id = list(dungeons.keys())[0]
            first_dungeon = dungeons[first_dungeon_id]
            print(f"   示例副本: {first_dungeon.get('name')}")
            
            floors = first_dungeon.get('floors', {})
            if floors:
                first_floor = list(floors.keys())[0]
                beasts = floors[first_floor].get('beasts', [])
                if beasts:
                    print(f"   第{first_floor}层幻兽数量: {len(beasts)}")
                    print(f"   第一个幻兽: {beasts[0].get('name')}")
                    print(f"   幻兽属性: {beasts[0].get('stats')}")
                else:
                    print("   ⚠️  第一层没有幻兽配置")
            else:
                print("   ⚠️  没有楼层配置")
    except Exception as e:
        print(f"   ❌ 配置文件加载失败: {e}")
    
    # 2. 检查测试账号的出战幻兽
    print("\n2. 检查测试账号的出战幻兽...")
    test_users = execute_query("""
        SELECT user_id, username, level 
        FROM player 
        WHERE username LIKE 'test%' OR user_id IN (8, 20057)
        LIMIT 5
    """)
    
    if not test_users:
        print("   ⚠️  没有找到测试账号")
    else:
        for user in test_users:
            user_id = user['user_id']
            username = user['username']
            level = user['level']
            
            # 检查出战幻兽
            beasts = execute_query("""
                SELECT pb.id, pb.name, pb.level, pb.hp, pb.physical_attack, pb.magic_attack,
                       pb.physical_defense, pb.magic_defense, pb.speed, pb.attack_type
                FROM player_beast pb
                WHERE pb.user_id = %s AND pb.is_in_team = 1
                ORDER BY pb.team_position
            """, (user_id,))
            
            print(f"\n   用户: {username} (ID: {user_id}, 等级: {level})")
            if not beasts:
                print("      ❌ 没有出战幻兽")
            else:
                print(f"      ✓ 出战幻兽数量: {len(beasts)}")
                for i, beast in enumerate(beasts, 1):
                    print(f"      {i}. {beast['name']} (Lv.{beast['level']}) - "
                          f"HP:{beast['hp']} 物攻:{beast['physical_attack']} "
                          f"法攻:{beast['magic_attack']} 速度:{beast['speed']}")
    
    # 3. 检查副本进度
    print("\n3. 检查副本进度...")
    progress = execute_query("""
        SELECT user_id, dungeon_name, current_floor, floor_cleared, loot_claimed
        FROM player_dungeon_progress
        WHERE user_id IN (SELECT user_id FROM player WHERE username LIKE 'test%' OR user_id IN (8, 20057))
        LIMIT 10
    """)
    
    if not progress:
        print("   ⚠️  没有副本进度记录")
    else:
        print(f"   找到 {len(progress)} 条副本进度记录")
        for p in progress[:5]:
            print(f"   用户{p['user_id']}: {p['dungeon_name']} - "
                  f"第{p['current_floor']}层 "
                  f"{'已通关' if p['floor_cleared'] else '未通关'} "
                  f"{'已领取' if p['loot_claimed'] else '未领取'}")
    
    print("\n" + "=" * 70)
    print("诊断完成")
    print("=" * 70)

if __name__ == '__main__':
    diagnose_dungeon_battle()
