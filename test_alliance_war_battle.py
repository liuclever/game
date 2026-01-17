#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试盟战对战流程
用于调试和验证整个盟战流程是否正确
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from interfaces.web_api.bootstrap import services
from domain.entities.alliance_registration import STATUS_REGISTERED, STATUS_VICTOR

def test_land_battle(land_id: int):
    """测试单个土地的对战流程"""
    print(f"\n{'='*60}")
    print(f"测试土地 {land_id} 的对战流程")
    print(f"{'='*60}\n")
    
    # 1. 检查报名情况
    print(f"[步骤1] 检查报名情况...")
    all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
    active_registrations = [r for r in all_registrations if r.is_active() or r.status == STATUS_VICTOR]
    
    print(f"  总报名数: {len(all_registrations)}")
    print(f"  活跃报名数: {len(active_registrations)}")
    
    if len(active_registrations) == 0:
        print("  ❌ 没有活跃的报名")
        return False
    
    for reg in active_registrations:
        print(f"  - 联盟 {reg.alliance_id}, 军队: {reg.army}, 状态: {reg.status}")
        
        # 检查成员情况
        assignments = services.alliance_repo.get_army_assignments(reg.alliance_id)
        filtered = [a for a in assignments if a.army == reg.army]
        print(f"    成员数: {len(filtered)}")
        if len(filtered) == 0:
            print(f"    ⚠️  警告：联盟 {reg.alliance_id} 的 {reg.army} 军队没有成员！")
    
    if len(active_registrations) < 2:
        print(f"  ❌ 至少需要2个联盟报名才能配对，当前只有 {len(active_registrations)} 个")
        return False
    
    # 2. 尝试配对
    print(f"\n[步骤2] 尝试配对...")
    pair_result = services.alliance_battle_service.lock_and_pair_land(land_id)
    
    if not pair_result.get("ok"):
        error = pair_result.get("error", "未知错误")
        print(f"  ❌ 配对失败: {error}")
        return False
    
    battles = pair_result.get("battles", [])
    bye_allocation = pair_result.get("bye_allocation")
    
    print(f"  ✅ 配对成功")
    print(f"  对战数: {len(battles)}")
    if bye_allocation:
        print(f"  轮空联盟: {bye_allocation.get('alliance_id')}")
    
    if not battles:
        print("  ⚠️  没有可配对的对战")
        return True
    
    # 3. 执行对战
    print(f"\n[步骤3] 执行对战...")
    for idx, battle_info in enumerate(battles, 1):
        battle_id = battle_info["battle_id"]
        left_alliance_id = battle_info["left_alliance_id"]
        right_alliance_id = battle_info["right_alliance_id"]
        
        print(f"\n  对战 {idx}: 联盟 {left_alliance_id} vs 联盟 {right_alliance_id}")
        
        rounds_executed = 0
        battle_finished = False
        
        while not battle_finished:
            advance_result = services.alliance_battle_service.advance_round(battle_id)
            if not advance_result.get("ok"):
                error = advance_result.get("error", "未知错误")
                print(f"    ❌ 推进回合失败: {error}")
                break
            
            rounds_executed += 1
            round_info = advance_result.get("round", {})
            left_alive = round_info.get("left_alive", 0)
            right_alive = round_info.get("right_alive", 0)
            
            print(f"    回合 {rounds_executed}: 左方存活 {left_alive} 人, 右方存活 {right_alive} 人")
            
            if advance_result.get("battle_finished"):
                battle_finished = True
                if left_alive > right_alive:
                    print(f"    ✅ 对战结束！胜利方: 联盟 {left_alliance_id}")
                elif right_alive > left_alive:
                    print(f"    ✅ 对战结束！胜利方: 联盟 {right_alliance_id}")
                else:
                    print(f"    ⚠️  双方同时战败")
    
    # 4. 检查最终结果
    print(f"\n[步骤4] 检查最终结果...")
    all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
    victor_registrations = [r for r in all_registrations if r.status == STATUS_VICTOR]
    
    print(f"  胜利者数: {len(victor_registrations)}")
    for victor in victor_registrations:
        print(f"  - 联盟 {victor.alliance_id}")
    
    # 检查占领情况
    land_detail = services.alliance_service.get_land_detail(land_id)
    if land_detail.get("ok"):
        occupation = land_detail.get("land", {}).get("occupation")
        if occupation:
            alliance_id = occupation.get("alliance_id")
            alliance_name = occupation.get("alliance_name", f"联盟{alliance_id}")
            print(f"  ✅ 土地 {land_id} 已被联盟 {alliance_name} (ID: {alliance_id}) 占领")
        else:
            print(f"  ⚠️  土地 {land_id} 当前未被占领")
    
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test_alliance_war_battle.py <land_id>")
        print("示例: python test_alliance_war_battle.py 1")
        return
    
    land_id = int(sys.argv[1])
    test_land_battle(land_id)

if __name__ == "__main__":
    main()
