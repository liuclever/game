#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断盟战配对问题
检查为什么3号和4号土地有联盟报名但没有竞争出对手
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from interfaces.web_api.bootstrap import services
from domain.entities.alliance_registration import (
    STATUS_REGISTERED, 
    STATUS_CONFIRMED, 
    STATUS_IN_BATTLE,
    STATUS_ELIMINATED,
    STATUS_VICTOR
)
from datetime import datetime

def diagnose_land(land_id: int):
    """诊断单个土地的配对问题"""
    print(f"\n{'='*60}")
    print(f"诊断土地 {land_id} 的配对问题")
    print(f"{'='*60}\n")
    
    # 1. 检查所有报名记录
    print(f"[步骤1] 检查所有报名记录...")
    all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
    print(f"  总报名记录数: {len(all_registrations)}")
    
    if len(all_registrations) == 0:
        print("  [X] 没有找到任何报名记录！")
        return
    
    for reg in all_registrations:
        status_names = {
            0: "已取消",
            1: "已报名",
            2: "待确认",
            3: "已确认",
            4: "对战中",
            5: "已淘汰",
            6: "胜利者"
        }
        status_name = status_names.get(reg.status, f"未知({reg.status})")
        print(f"  - 联盟 {reg.alliance_id}, 军队: {reg.army}, 状态: {status_name} (status={reg.status})")
        print(f"    报名ID: {reg.id}, 轮空等待: {reg.bye_waiting_round}, 最后轮空: {reg.last_bye_round}")
        print(f"    is_active(): {reg.is_active()}")
    
    # 2. 检查可用于配对的状态
    print(f"\n[步骤2] 检查可用于配对的状态...")
    registrations_for_pairing = services.alliance_repo.list_land_registrations_by_land(
        land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
    )
    print(f"  可用于配对的报名数: {len(registrations_for_pairing)}")
    
    if len(registrations_for_pairing) < 2:
        print(f"  [X] 至少需要2个联盟报名才能配对，当前只有 {len(registrations_for_pairing)} 个")
        if len(registrations_for_pairing) == 1:
            reg = registrations_for_pairing[0]
            print(f"  [!] 只有1个联盟报名（联盟 {reg.alliance_id}），无法配对")
        return
    
    # 3. 检查每个联盟的参战人员
    print(f"\n[步骤3] 检查每个联盟的参战人员...")
    now = datetime.utcnow()
    weekday = now.weekday()
    war_phase = "first" if weekday <= 2 else "second"
    checkin_date = now.date()
    
    for reg in registrations_for_pairing:
        print(f"\n  联盟 {reg.alliance_id} ({reg.army}):")
        
        # 获取军队成员
        assignments = services.alliance_repo.get_army_assignments(reg.alliance_id)
        army_assignments = [a for a in assignments if a.army == reg.army]
        print(f"    军队成员数: {len(army_assignments)}")
        
        if len(army_assignments) == 0:
            army_label = "飞龙军" if reg.army == "dragon" else "伏虎军"
            print(f"    [X] {army_label}没有成员！")
            continue
        
        # 检查每个成员
        valid_members = []
        invalid_members = []
        for assign in army_assignments:
            issues = []
            
            # 检查是否已签到（基于报名记录）
            has_checkin = False
            if reg.id:
                has_checkin = services.alliance_repo.has_war_checkin(reg.id, assign.user_id)
            if not has_checkin:
                issues.append("未签到")
            
            # 检查是否有出战幻兽
            team_beasts = services.player_beast_repo.get_team_beasts(assign.user_id)
            if not team_beasts or len(team_beasts) == 0:
                issues.append("没有出战幻兽")
            
            player = services.player_repo.get_by_id(assign.user_id)
            player_name = player.nickname if player else f"玩家{assign.user_id}"
            
            if issues:
                invalid_members.append(f"{player_name}({', '.join(issues)})")
            else:
                valid_members.append(player_name)
        
        print(f"    满足参战要求的成员: {len(valid_members)}")
        if valid_members:
            print(f"      {', '.join(valid_members[:5])}{'...' if len(valid_members) > 5 else ''}")
        
        print(f"    不满足参战要求的成员: {len(invalid_members)}")
        if invalid_members:
            print(f"      [X] {', '.join(invalid_members[:5])}{'...' if len(invalid_members) > 5 else ''}")
    
    # 4. 尝试配对
    print(f"\n[步骤4] 尝试配对...")
    try:
        pair_result = services.alliance_battle_service.lock_and_pair_land(land_id)
        if pair_result.get("ok"):
            battles = pair_result.get("battles", [])
            print(f"  [OK] 配对成功！共 {len(battles)} 场对战")
            for battle in battles:
                print(f"    - 对战 {battle['battle_id']}: 联盟 {battle['left_alliance_id']} vs 联盟 {battle['right_alliance_id']}")
        else:
            error = pair_result.get("error", "未知错误")
            print(f"  [X] 配对失败: {error}")
            if "validation_errors" in pair_result:
                print(f"  详细错误:")
                for err in pair_result["validation_errors"]:
                    print(f"    - {err}")
    except Exception as e:
        print(f"  [X] 配对时发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("="*60)
    print("盟战配对问题诊断工具")
    print("="*60)
    
    # 诊断3号和4号土地
    for land_id in [3, 4]:
        diagnose_land(land_id)
    
    print(f"\n{'='*60}")
    print("诊断完成")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
