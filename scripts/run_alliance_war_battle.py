#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盟战土地对战执行脚本

用法：
    python scripts/run_alliance_war_battle.py <land_id>
    
示例：
    python scripts/run_alliance_war_battle.py 1  # 执行土地ID为1的对战
    python scripts/run_alliance_war_battle.py 1 2 3 4  # 执行多个土地的对战
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from interfaces.web_api.bootstrap import services


def run_land_battle(land_id: int):
    """执行土地对战完整流程"""
    print(f"\n{'='*60}")
    print(f"开始执行土地 {land_id} 的对战流程")
    print(f"{'='*60}\n")
    
    # 1. 配对联盟
    print(f"[步骤1] 配对联盟...")
    pair_result = services.alliance_battle_service.lock_and_pair_land(land_id)
    if not pair_result.get("ok"):
        error = pair_result.get("error", "未知错误")
        print(f"❌ 配对失败: {error}")
        
        # 检查是否有轮空的联盟
        bye_regs = pair_result.get("bye_registrations", [])
        if bye_regs:
            print(f"   轮空联盟: {len(bye_regs)} 个")
        return False
    
    battles = pair_result.get("battles", [])
    bye_summary = pair_result.get("bye_allocation")
    
    if not battles:
        print(f"⚠️  没有可配对的对战")
        if bye_summary:
            print(f"   轮空联盟ID: {bye_summary.get('alliance_id')}")
        return True
    
    print(f"✅ 成功配对 {len(battles)} 场对战")
    if bye_summary:
        print(f"   轮空联盟ID: {bye_summary.get('alliance_id')}")
    
    # 2. 执行每场对战的所有回合
    print(f"\n[步骤2] 执行对战...")
    finished_count = 0
    error_count = 0
    
    for idx, battle_info in enumerate(battles, 1):
        battle_id = battle_info["battle_id"]
        left_alliance_id = battle_info["left_alliance_id"]
        right_alliance_id = battle_info["right_alliance_id"]
        left_count = battle_info["left_count"]
        right_count = battle_info["right_count"]
        
        print(f"\n  对战 {idx}/{len(battles)} (ID: {battle_id})")
        print(f"    联盟 {left_alliance_id} ({left_count}人) vs 联盟 {right_alliance_id} ({right_count}人)")
        
        rounds_executed = 0
        battle_finished = False
        
        # 循环推进回合直到战斗结束
        while not battle_finished:
            advance_result = services.alliance_battle_service.advance_round(battle_id)
            if not advance_result.get("ok"):
                error = advance_result.get("error", "未知错误")
                print(f"    ❌ 推进失败: {error}")
                error_count += 1
                break
            
            rounds_executed += 1
            round_info = advance_result.get("round", {})
            round_no = round_info.get("round_no", rounds_executed)
            left_alive = round_info.get("left_alive", 0)
            right_alive = round_info.get("right_alive", 0)
            duel_count = round_info.get("duel_count", 0)
            
            print(f"    回合 {round_no}: 左方存活 {left_alive} 人, 右方存活 {right_alive} 人 (决斗 {duel_count} 场)")
            
            if advance_result.get("battle_finished"):
                battle_finished = True
                finished_count += 1
                
                # 判断胜负
                if left_alive > right_alive:
                    winner_id = left_alliance_id
                    loser_id = right_alliance_id
                elif right_alive > left_alive:
                    winner_id = right_alliance_id
                    loser_id = left_alliance_id
                else:
                    winner_id = None
                    loser_id = None
                    print(f"    ⚠️  双方同时战败")
                
                if winner_id:
                    print(f"    ✅ 对战结束！胜利方: 联盟 {winner_id}")
                break
    
    # 3. 检查土地占领情况
    print(f"\n[步骤3] 检查土地占领情况...")
    land_detail = services.alliance_service.get_land_detail(land_id)
    if land_detail.get("ok"):
        occupation = land_detail.get("land", {}).get("occupation")
        if occupation:
            alliance_id = occupation.get("alliance_id")
            alliance_name = occupation.get("alliance_name", f"联盟{alliance_id}")
            print(f"✅ 土地 {land_id} 已被联盟 {alliance_name} (ID: {alliance_id}) 占领")
        else:
            print(f"⚠️  土地 {land_id} 当前未被占领")
    
    # 总结
    print(f"\n{'='*60}")
    print(f"对战执行完成")
    print(f"  总对战数: {len(battles)}")
    print(f"  成功完成: {finished_count}")
    print(f"  执行失败: {error_count}")
    print(f"{'='*60}\n")
    
    return error_count == 0


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python scripts/run_alliance_war_battle.py <land_id> [land_id2] ...")
        print("示例: python scripts/run_alliance_war_battle.py 1")
        print("      python scripts/run_alliance_war_battle.py 1 2 3 4")
        sys.exit(1)
    
    land_ids = []
    for arg in sys.argv[1:]:
        try:
            land_id = int(arg)
            land_ids.append(land_id)
        except ValueError:
            print(f"⚠️  无效的土地ID: {arg}，已跳过")
    
    if not land_ids:
        print("❌ 没有有效的土地ID")
        sys.exit(1)
    
    success_count = 0
    fail_count = 0
    
    for land_id in land_ids:
        try:
            success = run_land_battle(land_id)
            if success:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"\n❌ 执行土地 {land_id} 的对战时发生异常: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"全部执行完成")
    print(f"  成功: {success_count}/{len(land_ids)}")
    print(f"  失败: {fail_count}/{len(land_ids)}")
    print(f"{'='*60}\n")
    
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
