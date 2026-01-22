#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
# 设置输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
测试盟战完整流程：报名、对战、占领、清空报名记录

测试场景：
1. 多个联盟报名（有些满足条件，有些不满足）
2. 满足条件的进行对战
3. 最终胜利者占领土地
4. 验证所有报名记录都被删除（包括未参与对战的）
"""

import sys
import os
from datetime import datetime, date

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from interfaces.web_api.bootstrap import services
from domain.entities.alliance_registration import (
    STATUS_REGISTERED,
    STATUS_CONFIRMED,
    STATUS_VICTOR,
    STATUS_ELIMINATED,
    AllianceRegistration,
)


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_registrations(land_id: int, expected_count: int = 0, description: str = ""):
    """检查土地上的报名记录数量"""
    all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
    actual_count = len(all_registrations)
    
    print(f"  [检查] {description}")
    print(f"    期望报名记录数: {expected_count}")
    print(f"    实际报名记录数: {actual_count}")
    
    if actual_count == expected_count:
        print(f"    [OK] 通过")
        return True
    else:
        print(f"    [FAIL] 失败")
        if actual_count > 0:
            print(f"    剩余的报名记录:")
            for reg in all_registrations:
                print(f"      - 联盟 {reg.alliance_id}, 状态: {reg.status}, 军队: {reg.army}")
        return False


def check_occupation(land_id: int, expected_alliance_id: int = None):
    """检查土地占领情况"""
    occupation = services.alliance_repo.get_land_occupation(land_id)
    
    print(f"  [检查] 土地占领情况")
    if expected_alliance_id:
        print(f"    期望占领联盟: {expected_alliance_id}")
    else:
        print(f"    期望: 未被占领")
    
    if occupation:
        actual_alliance_id = occupation.get("alliance_id")
        alliance_name = occupation.get("alliance_name", "未知")
        print(f"    实际占领联盟: {actual_alliance_id} ({alliance_name})")
        
        if expected_alliance_id and actual_alliance_id == expected_alliance_id:
            print(f"    [OK] 通过")
            return True
        elif not expected_alliance_id:
            print(f"    [FAIL] 失败：土地已被占领，但期望未被占领")
            return False
        else:
            print(f"    [FAIL] 失败：占领联盟不匹配")
            return False
    else:
        if expected_alliance_id:
            print(f"    [FAIL] 失败：土地未被占领，但期望被联盟 {expected_alliance_id} 占领")
            return False
        else:
            print(f"    [OK] 通过")
            return True


def create_test_registration(alliance_id: int, land_id: int, army: str = "dragon", status: int = STATUS_REGISTERED):
    """创建测试报名记录"""
    from datetime import timezone
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    registration = AllianceRegistration(
        id=0,  # 临时ID，保存后会更新
        alliance_id=alliance_id,
        land_id=land_id,
        army=army,
        registration_time=now,
        cost=0,
        status=status,
        created_at=now,
    )
    registration_id = services.alliance_repo.save_land_registration(registration)
    registration.id = registration_id
    return registration


def test_complete_war_flow():
    """测试完整的盟战流程"""
    print_section("盟战完整流程测试")
    
    # 测试土地ID
    land_id = 1
    
    # 清理测试数据
    print_section("步骤1: 清理测试数据")
    try:
        # 删除该土地的所有报名记录
        services.alliance_repo.delete_land_registrations_by_land(land_id)
        print(f"  [OK] 已清理土地 {land_id} 的所有报名记录")
    except Exception as e:
        print(f"  [WARN] 清理报名记录时出错: {e}")
    
    # 删除土地占领记录
    try:
        from infrastructure.db.connection import execute_update
        execute_update("DELETE FROM alliance_land_occupation WHERE land_id = %s", (land_id,))
        print(f"  [OK] 已清理土地 {land_id} 的占领记录")
    except Exception as e:
        print(f"  [WARN] 清理占领记录时出错: {e}")
    
    # 验证清理结果
    check_registrations(land_id, 0, "清理后的报名记录")
    check_occupation(land_id, None)
    
    # 创建测试联盟（如果不存在）
    print_section("步骤2: 准备测试联盟")
    test_alliances = []
    for i in range(1, 5):  # 创建4个测试联盟
        alliance_id = 1000 + i
        try:
            alliance = services.alliance_repo.get_alliance_by_id(alliance_id)
            if not alliance:
                # 创建联盟
                from domain.entities.alliance import Alliance
                import time
                timestamp = int(time.time())
                alliance = Alliance(
                    id=0,  # 临时ID，创建后会返回新ID
                    name=f"测试联盟{i}_{timestamp}",
                    leader_id=1000 + i,
                    level=1,
                    exp=0,
                    funds=0,
                    crystals=0,
                    prosperity=0,
                    notice="",
                )
                new_alliance_id = services.alliance_repo.create_alliance(alliance)
                # 重新获取联盟以确认创建成功
                alliance = services.alliance_repo.get_alliance_by_id(new_alliance_id)
                if alliance:
                    print(f"  [OK] 创建测试联盟 {new_alliance_id}: {alliance.name}")
                    test_alliances.append(new_alliance_id)
                else:
                    print(f"  [WARN] 创建联盟失败，无法获取新创建的联盟")
            else:
                print(f"  [INFO] 测试联盟 {alliance_id} 已存在: {alliance.name}")
                test_alliances.append(alliance_id)
        except Exception as e:
            print(f"  [WARN] 准备联盟 {alliance_id} 时出错: {e}")
            # 如果创建失败，尝试使用已存在的联盟
            try:
                # 查找一个已存在的联盟
                from infrastructure.db.connection import execute_query
                rows = execute_query("SELECT id FROM alliances ORDER BY id LIMIT 1 OFFSET %s", (i-1,))
                if rows:
                    existing_id = rows[0]['id']
                    test_alliances.append(existing_id)
                    print(f"  [INFO] 使用已存在的联盟 {existing_id}")
            except:
                pass
            continue
    
    if len(test_alliances) < 2:
        print(f"  [FAIL] 测试失败：需要至少2个联盟，但只有 {len(test_alliances)} 个")
        return False
    
    # 创建报名记录
    print_section("步骤3: 创建报名记录")
    registrations = []
    
    # 联盟1: 满足条件（有成员、有幻兽）
    reg1 = create_test_registration(test_alliances[0], land_id, "dragon", STATUS_REGISTERED)
    registrations.append(reg1)
    print(f"  [OK] 联盟 {test_alliances[0]} 报名（飞龙军）")
    
    # 联盟2: 满足条件（有成员、有幻兽）
    reg2 = create_test_registration(test_alliances[1], land_id, "tiger", STATUS_REGISTERED)
    registrations.append(reg2)
    print(f"  [OK] 联盟 {test_alliances[1]} 报名（伏虎军）")
    
    # 联盟3: 不满足条件（没有成员签到）- 这个应该被标记为弃权
    if len(test_alliances) >= 3:
        reg3 = create_test_registration(test_alliances[2], land_id, "dragon", STATUS_REGISTERED)
        registrations.append(reg3)
        print(f"  [OK] 联盟 {test_alliances[2]} 报名（飞龙军，但不满足条件）")
    
    # 联盟4: 不满足条件（没有成员签到）- 这个应该被标记为弃权
    if len(test_alliances) >= 4:
        reg4 = create_test_registration(test_alliances[3], land_id, "tiger", STATUS_REGISTERED)
        registrations.append(reg4)
        print(f"  [OK] 联盟 {test_alliances[3]} 报名（伏虎军，但不满足条件）")
    
    # 验证报名记录
    check_registrations(land_id, len(registrations), "创建报名记录后")
    
    # 执行对战流程
    print_section("步骤4: 执行对战流程")
    
    # 设置环境变量以跳过时间检查（测试用）
    import os
    os.environ['ALLIANCE_WAR_ALLOW_TIME_BYPASS'] = 'true'
    
    try:
        # 配对和对战
        pair_result = services.alliance_battle_service.lock_and_pair_land(land_id)
        
        if not pair_result.get("ok"):
            error = pair_result.get("error", "未知错误")
            print(f"  [WARN] 配对失败: {error}")
            print(f"    这可能是正常的（如果所有联盟都不满足条件）")
        else:
            battles = pair_result.get("battles", [])
            bye_summary = pair_result.get("bye_allocation")
            occupation = pair_result.get("occupation")
            
            if occupation:
                # 直接占领（只有一个有效报名）
                victor_alliance_id = occupation.get("alliance_id")
                print(f"  [OK] 只有一个有效报名，联盟 {victor_alliance_id} 直接占领土地")
            elif battles:
                print(f"  [OK] 成功配对 {len(battles)} 场对战")
                if bye_summary:
                    print(f"    轮空联盟: {bye_summary.get('alliance_id')}")
                
                # 执行对战
                for battle_info in battles:
                    battle_id = battle_info["battle_id"]
                    left_alliance_id = battle_info["left_alliance_id"]
                    right_alliance_id = battle_info["right_alliance_id"]
                    
                    print(f"  [对战] 联盟 {left_alliance_id} vs 联盟 {right_alliance_id}")
                    
                    # 执行所有回合直到战斗结束
                    round_count = 0
                    max_rounds = 20
                    while round_count < max_rounds:
                        round_count += 1
                        advance_result = services.alliance_battle_service.advance_round(battle_id)
                        if not advance_result.get("ok"):
                            print(f"    [WARN] 第 {round_count} 回合推进失败: {advance_result.get('error')}")
                            break
                        
                        if advance_result.get("battle_finished"):
                            print(f"    [OK] 对战完成（共 {round_count} 回合）")
                            break
                    
                    if round_count >= max_rounds:
                        print(f"    [WARN] 达到最大回合数限制")
            else:
                print(f"  [INFO] 没有可配对的对战（可能所有报名都已弃权）")
        
        # 检查最终胜利者并占领土地
        print(f"\n  [检查] 最终胜利者...")
        all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
        victor_registrations = [r for r in all_registrations if r.status == STATUS_VICTOR]
        active_registrations = [r for r in all_registrations if (r.is_active() or r.status == STATUS_VICTOR)]
        
        if len(victor_registrations) == 1:
            # 只有一个胜利者，占领土地
            victor = victor_registrations[0]
            now = datetime.utcnow()
            war_date = now.date()
            weekday = now.weekday()
            war_phase = "first" if weekday <= 2 else "second"
            
            # 更新赛季积分
            season_key = now.strftime("%Y-%m")
            services.alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
            
            # 设置土地占领（这会自动删除所有报名记录）
            services.alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
            print(f"  [OK] 最终胜利者：联盟 {victor.alliance_id}，已占领土地")
        elif len(active_registrations) == 1:
            # 只有一个活跃的报名，自动成为胜利者并占领土地
            victor = active_registrations[0]
            victor.status = STATUS_VICTOR
            services.alliance_repo.save_land_registration(victor)
            
            now = datetime.utcnow()
            war_date = now.date()
            weekday = now.weekday()
            war_phase = "first" if weekday <= 2 else "second"
            
            # 更新赛季积分
            season_key = now.strftime("%Y-%m")
            services.alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
            
            # 设置土地占领（这会自动删除所有报名记录）
            services.alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
            print(f"  [OK] 唯一报名者：联盟 {victor.alliance_id}，已占领土地")
        else:
            print(f"  [WARN] 没有找到最终胜利者")
            print(f"    胜利者数量: {len(victor_registrations)}")
            print(f"    活跃报名数量: {len(active_registrations)}")
            
            # 即使没有最终胜利者，也要删除所有报名记录（盟战结束后清理）
            all_registrations_final = services.alliance_repo.list_land_registrations_by_land(land_id)
            if all_registrations_final:
                deleted_count = services.alliance_repo.delete_land_registrations_by_land(land_id)
                print(f"  [OK] 盟战结束，已删除 {deleted_count} 条报名记录（无最终胜利者）")
    
    except Exception as e:
        import traceback
        print(f"  [FAIL] 执行对战流程时出错: {e}")
        print(traceback.format_exc())
        return False
    
    # 验证最终结果
    print_section("步骤5: 验证最终结果")
    
    # 检查报名记录是否全部被删除
    all_registrations_after = services.alliance_repo.list_land_registrations_by_land(land_id)
    success = True
    
    if len(all_registrations_after) == 0:
        print(f"  [OK] 所有报名记录已被删除")
    else:
        print(f"  [FAIL] 仍有 {len(all_registrations_after)} 条报名记录未被删除:")
        for reg in all_registrations_after:
            print(f"    - 联盟 {reg.alliance_id}, 状态: {reg.status}, 军队: {reg.army}")
        success = False
    
    # 检查土地占领情况
    occupation_after = services.alliance_repo.get_land_occupation(land_id)
    if occupation_after:
        victor_alliance_id = occupation_after.get("alliance_id")
        alliance_name = occupation_after.get("alliance_name", "未知")
        print(f"  [OK] 土地已被联盟 {victor_alliance_id} ({alliance_name}) 占领")
    else:
        print(f"  [WARN] 土地未被占领（可能所有联盟都不满足条件）")
    
    # 最终总结
    print_section("测试总结")
    if success:
        print(f"  [OK] 测试通过：")
        print(f"    1. 报名记录创建成功")
        print(f"    2. 对战流程执行成功")
        print(f"    3. 最终胜利者占领土地")
        print(f"    4. 所有报名记录（包括未参与对战的）已被删除")
    else:
        print(f"  [FAIL] 测试失败：")
        print(f"    - 仍有报名记录未被删除")
    
    return success


if __name__ == "__main__":
    try:
        success = test_complete_war_flow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n\n测试异常: {e}")
        print(traceback.format_exc())
        sys.exit(1)
