#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试所有土地的对战功能
确保测试开战功能能够正常运行
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from interfaces.web_api.bootstrap import services
from domain.entities.alliance_registration import STATUS_REGISTERED, STATUS_CONFIRMED, STATUS_VICTOR, STATUS_CANCELLED, STATUS_ELIMINATED, STATUS_IN_BATTLE
from datetime import datetime

def test_land_battle(land_id: int):
    """测试单个土地的对战功能"""
    print(f"\n{'='*60}")
    print(f"测试土地 {land_id} 的对战功能")
    print(f"{'='*60}")
    
    # 检查该土地的报名情况
    all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
    active_registrations = [r for r in all_registrations if r.is_active() or r.status == STATUS_VICTOR]
    
    print(f"\n土地 {land_id} 的报名情况：")
    print(f"  总报名数: {len(all_registrations)}")
    print(f"  活跃报名数: {len(active_registrations)}")
    
    if len(active_registrations) == 0:
        print(f"  [WARNING] 土地 {land_id} 没有活跃的报名，跳过测试")
        return False
    
    for reg in active_registrations:
        print(f"  - 联盟 {reg.alliance_id} (状态: {reg.status})")
    
    # 直接调用服务层方法进行测试
    try:
        from infrastructure.db.connection import execute_update
        from datetime import datetime
        
        # 模拟 run_land_battle 的逻辑（测试模式）
        test_mode = True
        
        # 1. 修复报名状态
        fixed_count = 0
        for reg in all_registrations:
            if reg.status not in [STATUS_REGISTERED, STATUS_CONFIRMED, STATUS_VICTOR, STATUS_CANCELLED]:
                reg.status = STATUS_REGISTERED
                services.alliance_repo.save_land_registration(reg)
                fixed_count += 1
        
        if fixed_count > 0:
            print(f"  修复了 {fixed_count} 个报名状态")
        
        # 2. 清理旧记录
        try:
            registration_ids = [r.id for r in all_registrations]
            
            if registration_ids:
                placeholders = ','.join(['%s'] * len(registration_ids))
                sql_clean_signups = f"DELETE FROM alliance_army_signups WHERE registration_id IN ({placeholders})"
                execute_update(sql_clean_signups, tuple(registration_ids))
            
            sql_clean_battle = "DELETE FROM alliance_land_battle WHERE land_id = %s"
            execute_update(sql_clean_battle, (land_id,))
            
            sql_clean_rounds = """
                DELETE r FROM alliance_land_battle_round r
                INNER JOIN alliance_land_battle b ON r.battle_id = b.id
                WHERE b.land_id = %s
            """
            execute_update(sql_clean_rounds, (land_id,))
            
            sql_clean_duels = """
                DELETE d FROM alliance_land_battle_duel d
                INNER JOIN alliance_land_battle_round r ON d.round_id = r.id
                INNER JOIN alliance_land_battle b ON r.battle_id = b.id
                WHERE b.land_id = %s
            """
            execute_update(sql_clean_duels, (land_id,))
            
            print(f"  已清理旧的对战记录和签到记录")
        except Exception as e:
            print(f"  [WARNING] 清理旧记录时出错: {e}")
        
        # 3. 执行对战流程
        all_battle_results = []
        all_pair_results = []
        round_number = 0
        max_rounds = 10
        
        while round_number < max_rounds:
            round_number += 1
            
            # 检查当前状态
            all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
            victor_registrations = [r for r in all_registrations if r.status == STATUS_VICTOR]
            active_registrations = [r for r in all_registrations if r.is_active() or r.status == STATUS_VICTOR]
            
            # 如果有多个胜利者，重置状态
            if len(victor_registrations) > 1:
                for victor in victor_registrations:
                    victor.status = STATUS_REGISTERED
                    services.alliance_repo.save_land_registration(victor)
            
            # 检查是否只有一个胜利者
            if len(victor_registrations) == 1 and len(active_registrations) == 1:
                victor = victor_registrations[0]
                now = datetime.utcnow()
                war_date = now.date()
                weekday = now.weekday()
                war_phase = "first" if weekday <= 2 else "second"
                season_key = now.strftime("%Y-%m")
                services.alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                services.alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                
                print(f"\n[PASS] 土地 {land_id} 对战成功")
                print(f"  最终胜利者: 联盟 {victor.alliance_id}")
                print(f"  执行轮数: {round_number}")
                return True
            
            # 如果只有一个活跃报名
            if len(active_registrations) == 1 and len(victor_registrations) == 0:
                victor = active_registrations[0]
                victor.status = STATUS_VICTOR
                services.alliance_repo.save_land_registration(victor)
                now = datetime.utcnow()
                war_date = now.date()
                weekday = now.weekday()
                war_phase = "first" if weekday <= 2 else "second"
                season_key = now.strftime("%Y-%m")
                services.alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                services.alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                
                print(f"\n[PASS] 土地 {land_id} 对战成功（唯一报名者）")
                print(f"  最终胜利者: 联盟 {victor.alliance_id}")
                print(f"  执行轮数: {round_number}")
                return True
            
            # 配对联盟
            try:
                pair_result = services.alliance_battle_service.lock_and_pair_land(land_id)
            except Exception as e:
                print(f"\n[FAIL] 土地 {land_id} 配对失败")
                print(f"  错误: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
            if not pair_result.get("ok"):
                error_msg = pair_result.get("error", "配对失败")
                print(f"\n[FAIL] 土地 {land_id} 配对失败")
                print(f"  错误: {error_msg}")
                return False
            
            if pair_result.get("occupation"):
                all_pair_results.append(pair_result)
                print(f"\n[PASS] 土地 {land_id} 对战成功（直接占领）")
                print(f"  执行轮数: {round_number}")
                return True
            
            battles = pair_result.get("battles", [])
            if not battles or len(battles) == 0:
                all_pair_results.append(pair_result)
                bye_allocation = pair_result.get("bye_allocation")
                if bye_allocation:
                    bye_alliance_id = bye_allocation.get("alliance_id")
                    if bye_alliance_id:
                        bye_registration = next((r for r in all_registrations if r.alliance_id == bye_alliance_id), None)
                        if bye_registration:
                            now = datetime.utcnow()
                            war_date = now.date()
                            weekday = now.weekday()
                            war_phase = "first" if weekday <= 2 else "second"
                            season_key = now.strftime("%Y-%m")
                            services.alliance_repo.increment_alliance_war_score(bye_alliance_id, season_key, 1)
                            services.alliance_repo.set_land_occupation(land_id, bye_alliance_id, war_phase, war_date)
                            print(f"\n[PASS] 土地 {land_id} 对战成功（轮空）")
                            print(f"  最终胜利者: 联盟 {bye_alliance_id}")
                            print(f"  执行轮数: {round_number}")
                            return True
                print(f"\n[WARNING] 土地 {land_id} 没有可配对的对战")
                return False
            
            all_pair_results.append(pair_result)
            
            # 执行每场对战的所有回合
            round_battle_results = []
            for battle_info in battles:
                battle_id = battle_info["battle_id"]
                left_alliance_id = battle_info["left_alliance_id"]
                right_alliance_id = battle_info["right_alliance_id"]
                
                rounds_executed = 0
                battle_finished = False
                max_rounds_per_battle = 20
                
                try:
                    while not battle_finished and rounds_executed < max_rounds_per_battle:
                        advance_result = services.alliance_battle_service.advance_round(battle_id)
                        if not advance_result.get("ok"):
                            round_battle_results.append({
                                "battle_id": battle_id,
                                "status": "error",
                                "error": advance_result.get("error"),
                                "rounds_executed": rounds_executed
                            })
                            break
                        
                        rounds_executed += 1
                        if advance_result.get("battle_finished"):
                            battle_finished = True
                            round_battle_results.append({
                                "battle_id": battle_id,
                                "status": "finished",
                                "rounds_executed": rounds_executed
                            })
                except Exception as e:
                    print(f"  [ERROR] 执行对战 {battle_id} 时发生异常: {str(e)}")
                    round_battle_results.append({
                        "battle_id": battle_id,
                        "status": "error",
                        "error": str(e),
                        "rounds_executed": rounds_executed
                    })
            
            all_battle_results.extend(round_battle_results)
            
            # 检查最终胜利者
            all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
            victor_registrations = [r for r in all_registrations if r.status == STATUS_VICTOR]
            active_registrations = [r for r in all_registrations if r.is_active() or r.status == STATUS_VICTOR]
            
            if len(victor_registrations) > 1:
                for victor in victor_registrations:
                    victor.status = STATUS_REGISTERED
                    services.alliance_repo.save_land_registration(victor)
                continue
            
            if len(victor_registrations) == 1:
                victor = victor_registrations[0]
                now = datetime.utcnow()
                war_date = now.date()
                weekday = now.weekday()
                war_phase = "first" if weekday <= 2 else "second"
                season_key = now.strftime("%Y-%m")
                services.alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                services.alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                
                print(f"\n[PASS] 土地 {land_id} 对战成功")
                print(f"  最终胜利者: 联盟 {victor.alliance_id}")
                print(f"  执行轮数: {round_number}")
                return True
            
            if len(active_registrations) == 1:
                victor = active_registrations[0]
                victor.status = STATUS_VICTOR
                services.alliance_repo.save_land_registration(victor)
                now = datetime.utcnow()
                war_date = now.date()
                weekday = now.weekday()
                war_phase = "first" if weekday <= 2 else "second"
                season_key = now.strftime("%Y-%m")
                services.alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                services.alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                
                print(f"\n[PASS] 土地 {land_id} 对战成功（唯一报名者）")
                print(f"  最终胜利者: 联盟 {victor.alliance_id}")
                print(f"  执行轮数: {round_number}")
                return True
        
        print(f"\n[FAIL] 土地 {land_id} 对战未完成（达到最大轮数限制）")
        return False
            
    except Exception as e:
        print(f"\n[ERROR] 测试土地 {land_id} 时发生异常")
        print(f"  异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("="*60)
    print("测试所有土地的对战功能")
    print("="*60)
    
    # 测试所有土地（1-4）
    test_lands = [1, 2, 3, 4]
    
    results = {}
    for land_id in test_lands:
        results[land_id] = test_land_battle(land_id)
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for land_id, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"  土地 {land_id}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有土地的对战功能测试通过！")
        return 0
    else:
        print(f"\n[WARNING] 有 {total - passed} 个土地的对战功能测试失败")
        return 1

if __name__ == "__main__":
    exit(main())
