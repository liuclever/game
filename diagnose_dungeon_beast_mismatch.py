"""诊断副本幻兽错配问题"""
import sys
sys.path.insert(0, '.')

from infrastructure.db.player_repo_mysql import execute_query
import json

def diagnose_beast_mismatch():
    """诊断副本幻兽是否匹配"""
    
    print("=" * 70)
    print("诊断副本幻兽错配问题")
    print("=" * 70)
    
    # 加载配置
    with open('configs/dungeon_beasts.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 检查所有副本配置
    print("\n所有副本配置:")
    print("-" * 70)
    
    dungeons_by_name = {}
    for dungeon_id, dungeon in config['dungeons'].items():
        name = dungeon.get('name')
        dungeons_by_name[name] = dungeon
        
        beasts = dungeon.get('beasts', {})
        normal = beasts.get('normal', [])
        elite = beasts.get('elite', [])
        
        print(f"\n{dungeon_id}. {name} ({dungeon.get('map_name')})")
        print(f"   等级范围: {dungeon.get('level_range')}")
        print(f"   普通幻兽: {[b['name'] for b in normal]}")
        print(f"   精英幻兽: {[b['name'] for b in elite]}")
    
    # 检查特定副本
    print("\n" + "=" * 70)
    print("检查回音之谷副本")
    print("=" * 70)
    
    huiyinzhigu = dungeons_by_name.get('回音之谷')
    if huiyinzhigu:
        print(f"\n✓ 找到副本: {huiyinzhigu['name']}")
        print(f"  副本ID: {huiyinzhigu['dungeon_id']}")
        print(f"  地图: {huiyinzhigu['map_name']}")
        print(f"  等级范围: {huiyinzhigu['level_range']}")
        
        beasts = huiyinzhigu.get('beasts', {})
        normal = beasts.get('normal', [])
        elite = beasts.get('elite', [])
        
        print(f"\n  普通幻兽:")
        for beast in normal:
            print(f"    - {beast['name']} (Lv.{beast['level']}, ID: {beast['id']})")
        
        print(f"\n  精英幻兽:")
        for beast in elite:
            print(f"    - {beast['name']} (Lv.{beast['level']}, ID: {beast['id']})")
        
        # 检查是否有其他副本的幻兽
        print(f"\n  检查幻兽是否属于本副本:")
        all_beasts = normal + elite
        for beast in all_beasts:
            beast_id = beast['id']
            expected_prefix = f"d{huiyinzhigu['dungeon_id']}_"
            if beast_id.startswith(expected_prefix):
                print(f"    ✓ {beast['name']} ({beast_id}) - 正确")
            else:
                print(f"    ❌ {beast['name']} ({beast_id}) - 错误！应该以 {expected_prefix} 开头")
    else:
        print("❌ 未找到回音之谷副本")
    
    # 检查玩家进度
    print("\n" + "=" * 70)
    print("检查玩家副本进度")
    print("=" * 70)
    
    user_id = 8
    progress = execute_query("""
        SELECT dungeon_name, current_floor, floor_cleared, floor_event_type
        FROM player_dungeon_progress
        WHERE user_id = %s
        ORDER BY dungeon_name
    """, (user_id,))
    
    if progress:
        print(f"\n用户ID: {user_id}")
        for p in progress:
            print(f"  {p['dungeon_name']}: 第{p['current_floor']}层, "
                  f"{'已通关' if p['floor_cleared'] else '未通关'}, "
                  f"事件: {p['floor_event_type']}")
    else:
        print(f"⚠️  用户 {user_id} 没有副本进度")
    
    # 检查是否有重名副本
    print("\n" + "=" * 70)
    print("检查是否有重名副本")
    print("=" * 70)
    
    name_count = {}
    for dungeon_id, dungeon in config['dungeons'].items():
        name = dungeon.get('name')
        if name not in name_count:
            name_count[name] = []
        name_count[name].append(dungeon_id)
    
    has_duplicate = False
    for name, ids in name_count.items():
        if len(ids) > 1:
            print(f"❌ 重复的副本名称: {name} (ID: {ids})")
            has_duplicate = True
    
    if not has_duplicate:
        print("✓ 没有重名副本")
    
    print("\n" + "=" * 70)
    print("诊断完成")
    print("=" * 70)
    
    print("\n建议:")
    print("1. 检查前端传递的 dungeon_name 参数是否正确")
    print("2. 检查后端 get_dungeon_by_name 函数是否正确匹配副本名称")
    print("3. 在浏览器开发者工具中查看网络请求，确认传递的参数")
    print("4. 检查是否有缓存问题导致显示错误的数据")

if __name__ == '__main__':
    diagnose_beast_mismatch()
