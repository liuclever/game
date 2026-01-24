#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置盟战测试环境
1. 查看报名联盟的成员
2. 给没有战灵的成员分配战灵（尽量不同）
3. 确保成员已签到
4. 执行测试对战
"""
import sys
import os
from datetime import datetime

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from interfaces.web_api.bootstrap import services
from domain.entities.alliance_registration import STATUS_REGISTERED, STATUS_VICTOR
from infrastructure.db.connection import execute_query, execute_update

def get_land_registrations(land_id: int):
    """获取土地的所有报名记录"""
    from domain.entities.alliance_registration import STATUS_CONFIRMED, STATUS_REGISTERED
    # 获取所有报名记录（包括已确认和已报名的）
    all_registrations = services.alliance_repo.list_land_registrations_by_land(
        land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
    )
    return all_registrations

def get_alliance_members(alliance_id: int):
    """获取联盟的所有成员"""
    members = services.alliance_repo.get_alliance_members(alliance_id)
    return members

def ensure_member_in_army(alliance_id: int, user_id: int, army: str):
    """确保成员已加入指定军队"""
    assignments = services.alliance_repo.get_army_assignments(alliance_id)
    existing = [a for a in assignments if a.user_id == user_id and a.army == army]
    if existing:
        return True  # 已经加入
    
    # 加入军队
    services.alliance_repo.upsert_army_assignment(alliance_id, user_id, army)
    return True

def get_alliance_members_with_army(alliance_id: int, army: str):
    """获取联盟指定军队的成员（包括自动分配）"""
    # 先获取所有成员
    all_members = get_alliance_members(alliance_id)
    
    # 根据等级和军队类型筛选
    result = []
    for member in all_members:
        player = services.player_repo.get_by_id(member.user_id)
        if not player:
            continue
        
        level = player.level or 1
        # 根据等级判断应该加入哪个军队
        # 40级及以下伏虎军，40级以上飞龙军
        expected_army = "tiger" if level <= 40 else "dragon"
        
        if expected_army == army:
            # 确保成员已加入军队
            ensure_member_in_army(alliance_id, member.user_id, army)
            result.append(member)
    
    return result

def check_user_has_beasts(user_id: int):
    """检查用户是否有出战幻兽"""
    team_beasts = services.player_beast_repo.get_team_beasts(user_id)
    return len(team_beasts) > 0

def get_available_beast_templates():
    """获取可用的幻兽模板列表"""
    templates = services.beast_template_repo.get_all()
    # 返回前20个不同的模板ID
    template_ids = list(templates.keys())[:20]
    return template_ids

def assign_beast_to_user(user_id: int, template_id: int):
    """给用户分配一个幻兽并设置为出战"""
    try:
        # 检查用户是否已有出战幻兽
        team_beasts = services.player_beast_repo.get_team_beasts(user_id)
        if len(team_beasts) > 0:
            # 用户已有出战幻兽，不需要再分配
            return None
        
        # 获取模板信息
        template = services.beast_template_repo.get_by_id(template_id)
        if not template:
            print(f"  [WARN] 模板 {template_id} 不存在")
            return None
        
        # 直接创建PlayerBeastData（这是对战系统需要的）
        from infrastructure.db.player_beast_repo_mysql import PlayerBeastData
        from domain.services.beast_stat_calculator import BeastStatCalculator
        from domain.services.beast_factory import create_initial_beast
        
        # 先创建domain层的Beast对象（用于计算属性）
        domain_beast = create_initial_beast(user_id=user_id, template=template)
        
        # 计算属性
        stats = BeastStatCalculator.calc_base_stats(domain_beast, template, max_realm="地界")
        
        # 创建PlayerBeastData
        player_beast = PlayerBeastData(
            id=None,  # 新建，ID由数据库生成
            user_id=user_id,
            template_id=template_id,
            name=template.name,
            nickname=domain_beast.nickname or template.name,
            realm=domain_beast.realm or "地界",
            race=template.race,
            level=domain_beast.level,
            exp=domain_beast.exp or 0,
            nature="物系" if template.attack_type == "physical" else "法系",
            personality=domain_beast.personality or "",
            hp=stats.hp,
            physical_attack=stats.physical_attack,
            magic_attack=stats.magic_attack,
            physical_defense=stats.physical_defense,
            magic_defense=stats.magic_defense,
            speed=stats.speed,
            combat_power=stats.hp + stats.physical_attack + stats.magic_attack + stats.physical_defense + stats.magic_defense + stats.speed * 100,
            growth_rate=template.growth_score,
            hp_aptitude=getattr(domain_beast, 'hp_aptitude', 1000),
            speed_aptitude=getattr(domain_beast, 'speed_aptitude', 1000),
            physical_attack_aptitude=getattr(domain_beast, 'physical_atk_aptitude', 1000),
            magic_attack_aptitude=getattr(domain_beast, 'magic_atk_aptitude', 1000),
            physical_defense_aptitude=getattr(domain_beast, 'physical_def_aptitude', 1000),
            magic_defense_aptitude=getattr(domain_beast, 'magic_def_aptitude', 1000),
            lifespan="10000/10000",
            skills=domain_beast.skills or [],
            counters="",
            countered_by="",
            is_in_team=1,  # 设置为出战
            team_position=0,  # 设置位置
        )
        
        # 保存到数据库
        new_id = services.player_beast_repo.create_beast(player_beast)
        player_beast.id = new_id
        
        return player_beast
    except Exception as e:
        print(f"  [ERROR] 分配幻兽失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def ensure_war_checkin(registration_id: int, user_id: int):
    """确保用户已为指定报名记录签到"""
    now = datetime.utcnow()
    weekday = now.weekday()
    war_phase = "first" if weekday <= 2 else "second"
    checkin_date = now.date()
    
    # 检查是否已签到
    if services.alliance_repo.has_war_checkin(registration_id, user_id):
        return True
    
    # 获取报名记录以获取 alliance_id
    registration = services.alliance_repo.get_land_registration_by_id(registration_id)
    if not registration:
        print(f"  [ERROR] 找不到报名记录 {registration_id}")
        return False
    
    # 添加签到记录
    try:
        services.alliance_repo.add_war_checkin(
            registration.alliance_id, user_id, registration_id, war_phase, weekday, checkin_date, 30000
        )
        return True
    except Exception as e:
        print(f"  [ERROR] 签到失败: {str(e)}")
        return False

def setup_land_for_battle(land_id: int):
    """为土地设置测试环境"""
    print(f"\n{'='*60}")
    print(f"设置土地 {land_id} 的测试环境")
    print(f"{'='*60}\n")
    
    # 1. 获取报名联盟
    all_registrations = get_land_registrations(land_id)
    if len(all_registrations) < 2:
        print(f"[ERROR] 土地 {land_id} 只有 {len(all_registrations)} 个联盟报名，至少需要2个")
        return False
    
    print(f"[OK] 找到 {len(all_registrations)} 个联盟报名")
    
    # 过滤掉没有成员的联盟，并将它们标记为取消
    valid_registrations = []
    from domain.entities.alliance_registration import STATUS_CANCELLED
    for reg in all_registrations:
        alliance_id = reg.alliance_id
        army = reg.army or "dragon"
        members = get_alliance_members_with_army(alliance_id, army)
        if len(members) > 0:
            valid_registrations.append(reg)
        else:
            print(f"  [SKIP] 跳过联盟 {alliance_id} ({army} 军队)：没有符合条件的成员，标记为取消")
            # 将没有成员的联盟报名标记为取消
            reg.status = STATUS_CANCELLED
            services.alliance_repo.save_land_registration(reg)
    
    if len(valid_registrations) < 2:
        print(f"[ERROR] 土地 {land_id} 只有 {len(valid_registrations)} 个有成员的联盟，至少需要2个")
        return False
    
    registrations = valid_registrations
    
    # 确保所有更改已保存到数据库
    from infrastructure.db.connection import get_connection
    conn = get_connection()
    if conn:
        conn.commit()
    
    # 2. 获取可用的幻兽模板
    template_ids = get_available_beast_templates()
    template_index = 0
    
    # 3. 为每个联盟的成员分配战灵
    all_members_ready = True
    for reg in registrations:
        alliance_id = reg.alliance_id
        army = reg.army or "dragon"
        
        print(f"\n[联盟 {alliance_id} - {army} 军队]")
        
        # 获取该联盟该军队的成员（会自动加入军队）
        members = get_alliance_members_with_army(alliance_id, army)
        print(f"  成员数: {len(members)}")
        
        if len(members) == 0:
            print(f"  [WARN] 警告：联盟 {alliance_id} 的 {army} 军队没有符合条件的成员！")
            print(f"  提示：{army} 军队需要等级 {'<=40' if army == 'tiger' else '>40'} 的成员")
            all_members_ready = False
            continue
        
        # 为每个成员检查和分配战灵
        for member in members:
            user_id = member.user_id
            has_beasts = check_user_has_beasts(user_id)
            
            if not has_beasts:
                # 分配一个幻兽
                template_id = template_ids[template_index % len(template_ids)]
                template_index += 1
                
                print(f"  用户 {user_id}: 没有战灵，分配模板 {template_id}...", end="")
                beast = assign_beast_to_user(user_id, template_id)
                if beast:
                    print(f" [OK]")
                else:
                    print(f" [FAIL]")
                    all_members_ready = False
            else:
                print(f"  用户 {user_id}: 已有战灵 [OK]")
            
            # 确保已签到（基于报名记录）
            if not reg.id:
                print(f"  [WARN] 报名记录没有ID，无法签到")
                all_members_ready = False
            elif not ensure_war_checkin(reg.id, user_id):
                print(f"  [WARN] 用户 {user_id} 签到失败")
                all_members_ready = False
    
    return all_members_ready

def cleanup_old_battles(land_id: int):
    """清理该土地的旧对战记录和报名记录"""
    from infrastructure.db.connection import execute_update, execute_query
    
    # 获取该土地的所有报名记录ID
    sql_reg = "SELECT id FROM alliance_land_registration WHERE land_id = %s"
    registration_ids = [row['id'] for row in execute_query(sql_reg, (land_id,))]
    
    # 删除该土地的旧army_signups记录
    if registration_ids:
        placeholders = ','.join(['%s'] * len(registration_ids))
        sql_signups = f"DELETE FROM alliance_army_signups WHERE registration_id IN ({placeholders})"
        affected_signups = execute_update(sql_signups, tuple(registration_ids))
        print(f"  已清理 {affected_signups} 条旧的army_signups记录")
    
    # 删除该土地的所有旧对战记录（因为phase在lock_and_pair_land中硬编码为0）
    sql_battle = "DELETE FROM alliance_land_battle WHERE land_id = %s"
    affected_battles = execute_update(sql_battle, (land_id,))
    print(f"  已清理 {affected_battles} 条旧的battle记录")

def run_battle_test(land_id: int):
    """执行对战测试"""
    print(f"\n{'='*60}")
    print(f"执行土地 {land_id} 的对战测试")
    print(f"{'='*60}\n")
    
    # 清理旧对战记录
    cleanup_old_battles(land_id)
    
    # 检查当前报名状态
    from domain.entities.alliance_registration import STATUS_CONFIRMED, STATUS_REGISTERED, STATUS_VICTOR, STATUS_CANCELLED
    all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
    active_registrations = services.alliance_repo.list_land_registrations_by_land(
        land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
    )
    print(f"  当前报名总数: {len(all_registrations)}")
    print(f"  活跃报名数: {len(active_registrations)}")
    for reg in all_registrations:
        print(f"    联盟 {reg.alliance_id}, 状态: {reg.status}, 军队: {reg.army}")
    
    # 确保所有有效报名的状态正确（重置所有非取消状态为已报名）
    for reg in all_registrations:
        if reg.status != STATUS_CANCELLED and reg.status not in [STATUS_CONFIRMED, STATUS_REGISTERED]:
            print(f"  修复联盟 {reg.alliance_id} 的状态: {reg.status} -> {STATUS_REGISTERED}")
            reg.status = STATUS_REGISTERED
            services.alliance_repo.save_land_registration(reg)
    
    # 重新获取活跃报名
    active_registrations = services.alliance_repo.list_land_registrations_by_land(
        land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
    )
    print(f"  修复后活跃报名数: {len(active_registrations)}")
    if len(active_registrations) < 2:
        print(f"  [ERROR] 修复后仍然只有 {len(active_registrations)} 个活跃报名，无法配对")
        return False
    
    # 直接调用服务层方法
    try:
        # 循环配对和执行对战
        all_battle_results = []
        all_pair_results = []
        round_number = 0
        max_rounds = 10
        
        while round_number < max_rounds:
            round_number += 1
            print(f"\n[第 {round_number} 轮]")
            
            # 检查当前有多少个活跃的报名（包括胜利者和待配对的）
            all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
            victor_registrations = [r for r in all_registrations if r.status == STATUS_VICTOR]
            active_registrations = services.alliance_repo.list_land_registrations_by_land(
                land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
            )
            
            # 计算总活跃数（胜利者 + 待配对的）
            total_active = len(victor_registrations) + len(active_registrations)
            print(f"  当前状态: {len(victor_registrations)} 个胜利者, {len(active_registrations)} 个待配对")
            
            # 如果有胜利者和待配对的，需要让胜利者重新进入配对状态（以便与待配对的配对）
            if len(victor_registrations) > 0 and len(active_registrations) > 0:
                print(f"  发现 {len(victor_registrations)} 个胜利者和 {len(active_registrations)} 个待配对的，重置胜利者状态进行配对...")
                for victor in victor_registrations:
                    victor.status = STATUS_REGISTERED
                    services.alliance_repo.save_land_registration(victor)
                # 重新获取活跃报名（现在胜利者也变成了待配对状态）
                active_registrations = services.alliance_repo.list_land_registrations_by_land(
                    land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
                )
                total_active = len(active_registrations)
            
            # 如果有多个胜利者（但没有待配对的），需要让它们重新进入配对状态
            elif len(victor_registrations) > 1:
                print(f"  发现 {len(victor_registrations)} 个胜利者，重置状态进行下一轮...")
                for victor in victor_registrations:
                    victor.status = STATUS_REGISTERED
                    services.alliance_repo.save_land_registration(victor)
                active_registrations = services.alliance_repo.list_land_registrations_by_land(
                    land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
                )
                total_active = len(active_registrations)
            
            # 检查是否只剩下一个活跃的（胜利者或待配对的）
            if total_active == 1:
                # 确定最终胜利者（优先选择胜利者，否则选择待配对的）
                if victor_registrations:
                    victor = victor_registrations[0]
                elif active_registrations:
                    # 如果只有一个待配对的，它自动成为胜利者
                    victor = active_registrations[0]
                    victor.status = STATUS_VICTOR
                    services.alliance_repo.save_land_registration(victor)
                else:
                    print(f"  [ERROR] 没有找到最终胜利者")
                    return False
                now = datetime.utcnow()
                war_date = now.date()
                weekday = now.weekday()
                war_phase = "first" if weekday <= 2 else "second"
                season_key = now.strftime("%Y-%m")
                services.alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                services.alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                print(f"  [OK] 最终胜利者：联盟 {victor.alliance_id}")
                print(f"  [OK] 土地 {land_id} 已被联盟 {victor.alliance_id} 占领")
                return True
            
            # 配对前清理旧的army_signups和battle记录（避免重复）
            active_for_pairing = services.alliance_repo.list_land_registrations_by_land(
                land_id, statuses=[STATUS_CONFIRMED, STATUS_REGISTERED]
            )
            if active_for_pairing:
                reg_ids = [r.id for r in active_for_pairing if r.id]
                if reg_ids:
                    placeholders = ','.join(['%s'] * len(reg_ids))
                    sql_clean_signups = f"DELETE FROM alliance_army_signups WHERE registration_id IN ({placeholders})"
                    execute_update(sql_clean_signups, tuple(reg_ids))
            
            # 清理旧的battle记录（因为phase是硬编码的0）
            sql_clean_battle = "DELETE FROM alliance_land_battle WHERE land_id = %s"
            execute_update(sql_clean_battle, (land_id,))
            
            # 配对联盟
            print(f"  配对联盟...")
            pair_result = services.alliance_battle_service.lock_and_pair_land(land_id)
            if not pair_result.get("ok"):
                error_msg = pair_result.get("error", "配对失败")
                print(f"  [ERROR] 配对失败: {error_msg}")
                if "至少需要两个联盟" in error_msg and len(victor_registrations) == 1:
                    victor = victor_registrations[0]
                    now = datetime.utcnow()
                    war_date = now.date()
                    weekday = now.weekday()
                    war_phase = "first" if weekday <= 2 else "second"
                    season_key = now.strftime("%Y-%m")
                    services.alliance_repo.increment_alliance_war_score(victor.alliance_id, season_key, 1)
                    services.alliance_repo.set_land_occupation(land_id, victor.alliance_id, war_phase, war_date)
                    print(f"  ✅ 最终胜利者：联盟 {victor.alliance_id}")
                    return True
                return False
            
            all_pair_results.append(pair_result)
            battles = pair_result.get("battles", [])
            
            if not battles:
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
                            print(f"  [OK] 轮空胜利者：联盟 {bye_alliance_id}")
                            return True
                break
            
            print(f"  配对成功，{len(battles)} 场对战")
            
            # 执行每场对战
            round_battle_results = []
            for battle_info in battles:
                battle_id = battle_info["battle_id"]
                left_alliance_id = battle_info["left_alliance_id"]
                right_alliance_id = battle_info["right_alliance_id"]
                
                print(f"    对战: 联盟 {left_alliance_id} vs 联盟 {right_alliance_id}")
                
                rounds_executed = 0
                battle_finished = False
                
                while not battle_finished:
                    advance_result = services.alliance_battle_service.advance_round(battle_id)
                    if not advance_result.get("ok"):
                        error = advance_result.get("error", "未知错误")
                        print(f"      [ERROR] 推进回合失败: {error}")
                        break
                    
                    rounds_executed += 1
                    round_info = advance_result.get("round", {})
                    left_alive = round_info.get("left_alive", 0)
                    right_alive = round_info.get("right_alive", 0)
                    
                    if advance_result.get("battle_finished"):
                        battle_finished = True
                        if left_alive > right_alive:
                            print(f"      [OK] 胜利方: 联盟 {left_alliance_id}")
                        elif right_alive > left_alive:
                            print(f"      [OK] 胜利方: 联盟 {right_alliance_id}")
                        else:
                            print(f"      [WARN] 双方同时战败")
            
            all_battle_results.extend(round_battle_results)
        
        print(f"\n  [WARN] 达到最大轮数限制或无法继续")
        return False
        
    except Exception as e:
        print(f"[ERROR] 执行对战失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python setup_alliance_war_test.py <land_id> [setup_only]")
        print("示例: python setup_alliance_war_test.py 1")
        print("      python setup_alliance_war_test.py 1 setup_only  # 只设置，不执行对战")
        return
    
    land_id = int(sys.argv[1])
    setup_only = len(sys.argv) > 2 and sys.argv[2] == "setup_only"
    
    # 1. 设置测试环境
    setup_success = setup_land_for_battle(land_id)
    
    if setup_success:
        print("\n[OK] 测试环境设置完成！")
    else:
        print("\n[WARN] 部分设置失败，但继续尝试对战测试...")
    
    # 2. 执行对战测试
    if not setup_only:
        print("\n开始执行对战测试...")
        result = run_battle_test(land_id)
        if result:
            print("\n[OK] 对战测试完成！")
        else:
            print("\n[ERROR] 对战测试失败")
    else:
        print("\n（跳过对战测试，仅设置环境）")

if __name__ == "__main__":
    main()
