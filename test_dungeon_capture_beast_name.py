"""测试副本捕捉幻兽名称是否正确"""
import sys
sys.path.insert(0, '.')

from infrastructure.db.player_repo_mysql import execute_query
import json

def test_capture_beast_name():
    """测试捕捉幻兽名称"""
    
    print("=" * 70)
    print("测试副本捕捉幻兽名称")
    print("=" * 70)
    
    # 1. 检查副本配置
    print("\n1. 检查副本配置...")
    with open('configs/dungeon_beasts.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    dungeons = config.get('dungeons', {})
    
    # 找到天罚山副本
    tianfashan = None
    for dungeon_id, dungeon in dungeons.items():
        if dungeon.get('name') == '天罚山':
            tianfashan = dungeon
            break
    
    if tianfashan:
        print(f"   ✓ 找到天罚山副本")
        beasts = tianfashan.get('beasts', {})
        normal = beasts.get('normal', [])
        elite = beasts.get('elite', [])
        
        print(f"\n   普通幻兽:")
        for beast in normal:
            print(f"      - {beast.get('name')} (Lv.{beast.get('level')})")
        
        print(f"\n   精英幻兽:")
        for beast in elite:
            print(f"      - {beast.get('name')} (Lv.{beast.get('level')})")
    else:
        print("   ❌ 未找到天罚山副本")
    
    # 2. 检查玩家当前副本进度
    print("\n2. 检查玩家副本进度...")
    user_id = 8  # 秦王
    
    progress = execute_query("""
        SELECT dungeon_name, current_floor, floor_cleared, floor_event_type
        FROM player_dungeon_progress
        WHERE user_id = %s AND dungeon_name = '天罚山'
    """, (user_id,))
    
    if progress:
        p = progress[0]
        print(f"   用户ID: {user_id}")
        print(f"   副本: {p['dungeon_name']}")
        print(f"   当前层: {p['current_floor']}")
        print(f"   已通关: {p['floor_cleared']}")
        print(f"   事件类型: {p['floor_event_type']}")
    else:
        print(f"   ⚠️  用户 {user_id} 没有天罚山的进度记录")
    
    # 3. 模拟获取楼层幻兽
    print("\n3. 模拟获取楼层幻兽...")
    if tianfashan:
        beasts = tianfashan.get('beasts', {})
        normal = beasts.get('normal', [])
        elite = beasts.get('elite', [])
        all_beasts = normal + elite
        
        print(f"   可能出现的幻兽:")
        for beast in all_beasts:
            print(f"      - {beast.get('name')} (Lv.{beast.get('level')})")
        
        # 模拟随机选择
        import random
        if all_beasts:
            chosen = random.choice(all_beasts)
            print(f"\n   随机选择: {chosen.get('name')}")
            print(f"   这个名称应该在战斗后作为 capturable_beast 返回")
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
    
    print("\n建议:")
    print("1. 检查前端是否正确传递了幻兽数据")
    print("2. 检查后端是否正确使用了 defender_pvp_beasts[0].name")
    print("3. 清除浏览器缓存并重启后端服务")

if __name__ == '__main__':
    test_capture_beast_name()
