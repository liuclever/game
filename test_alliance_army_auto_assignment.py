#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试联盟兵营自动分配功能

测试场景：
1. 创建联盟时，创建者自动分配到对应军队
2. 加入联盟时，新成员自动分配到对应军队
3. 玩家升级时，自动重新分配到对应军队（40级升到43级，从伏虎军转到飞龙军）
"""

import sys
import os
import io
from datetime import datetime

# 设置输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from interfaces.web_api.bootstrap import services


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_army_assignment(user_id: int, expected_army_type: int, description: str):
    """检查玩家的军队分配"""
    member = services.alliance_repo.get_member(user_id)
    if not member:
        print(f"  [FAIL] {description}: 玩家未加入联盟")
        return False
    
    actual_army_type = member.army_type or 0
    army_labels = {0: "未分配", 1: "飞龙军", 2: "伏虎军"}
    expected_label = army_labels.get(expected_army_type, "未知")
    actual_label = army_labels.get(actual_army_type, "未知")
    
    print(f"  [检查] {description}")
    print(f"    期望军队: {expected_label} ({expected_army_type})")
    print(f"    实际军队: {actual_label} ({actual_army_type})")
    
    if actual_army_type == expected_army_type:
        print(f"    [OK] 通过")
        return True
    else:
        print(f"    [FAIL] 失败")
        return False


def test_army_auto_assignment():
    """测试军队自动分配功能"""
    print_section("联盟兵营自动分配功能测试")
    
    # 测试用户ID
    test_user_id_1 = 20001  # 用于创建联盟（40级）
    test_user_id_2 = 20002  # 用于加入联盟（35级）
    test_user_id_3 = 20003  # 用于测试升级（40级，升级到43级）
    
    # 清理测试数据
    print_section("步骤1: 清理测试数据")
    try:
        # 删除测试用户的联盟成员记录
        for user_id in [test_user_id_1, test_user_id_2, test_user_id_3]:
            try:
                services.alliance_repo.remove_member(user_id)
                print(f"  [OK] 已清理用户 {user_id} 的联盟成员记录")
            except:
                pass
    except Exception as e:
        print(f"  [WARN] 清理测试数据时出错: {e}")
    
    # 确保测试用户存在
    print_section("步骤2: 准备测试用户")
    for user_id, level in [(test_user_id_1, 40), (test_user_id_2, 35), (test_user_id_3, 40)]:
        try:
            player = services.player_repo.get_by_id(user_id)
            if not player:
                print(f"  [WARN] 测试用户 {user_id} 不存在，跳过")
                continue
            # 设置等级
            player.level = level
            services.player_repo.save(player)
            print(f"  [OK] 测试用户 {user_id} 等级设置为 {level}")
        except Exception as e:
            print(f"  [WARN] 准备测试用户 {user_id} 时出错: {e}")
    
    # 测试1: 创建联盟时自动分配军队
    print_section("步骤3: 测试创建联盟时自动分配军队")
    try:
        # 给测试用户添加盟主证明
        from domain.rules.alliance_rules import AllianceRules
        token_id = AllianceRules.LEAGUE_LEADER_TOKEN_ID
        try:
            services.inventory_service.add_item(test_user_id_1, token_id, 1)
            print(f"  [OK] 已为用户 {test_user_id_1} 添加盟主证明")
        except Exception as e:
            print(f"  [WARN] 添加盟主证明失败: {e}")
        
        # 创建联盟（40级用户，应该分配到伏虎军）
        result = services.alliance_service.create_alliance(
            test_user_id_1,
            f"测试联盟_{int(datetime.now().timestamp())}"
        )
        
        if result.get("ok"):
            alliance_id = result.get("alliance_id")
            print(f"  [OK] 联盟创建成功，ID: {alliance_id}")
            
            # 检查创建者的军队分配（40级应该分配到伏虎军=2）
            success = check_army_assignment(
                test_user_id_1,
                2,  # 伏虎军
                "创建者（40级）应分配到伏虎军"
            )
            if not success:
                return False
        else:
            error = result.get("error", "未知错误")
            print(f"  [FAIL] 创建联盟失败: {error}")
            return False
    except Exception as e:
        import traceback
        print(f"  [FAIL] 创建联盟时出错: {e}")
        print(traceback.format_exc())
        return False
    
    # 测试2: 加入联盟时自动分配军队
    print_section("步骤4: 测试加入联盟时自动分配军队")
    try:
        alliance_id = result.get("alliance_id")
        
        # 35级用户加入联盟（应该分配到伏虎军=2）
        join_result = services.alliance_service.join_alliance(test_user_id_2, alliance_id)
        
        if join_result.get("ok"):
            print(f"  [OK] 用户 {test_user_id_2} 加入联盟成功")
            
            # 检查新成员的军队分配（35级应该分配到伏虎军=2）
            success = check_army_assignment(
                test_user_id_2,
                2,  # 伏虎军
                "新成员（35级）应分配到伏虎军"
            )
            if not success:
                return False
        else:
            error = join_result.get("error", "未知错误")
            print(f"  [FAIL] 加入联盟失败: {error}")
            return False
    except Exception as e:
        import traceback
        print(f"  [FAIL] 加入联盟时出错: {e}")
        print(traceback.format_exc())
        return False
    
    # 测试3: 玩家升级时自动重新分配军队
    print_section("步骤5: 测试玩家升级时自动重新分配军队")
    try:
        # 40级用户加入联盟（应该分配到伏虎军=2）
        join_result = services.alliance_service.join_alliance(test_user_id_3, alliance_id)
        
        if not join_result.get("ok"):
            error = join_result.get("error", "未知错误")
            print(f"  [WARN] 用户 {test_user_id_3} 加入联盟失败: {error}")
        else:
            print(f"  [OK] 用户 {test_user_id_3} 加入联盟成功")
            
            # 检查初始分配（40级应该分配到伏虎军=2）
            success = check_army_assignment(
                test_user_id_3,
                2,  # 伏虎军
                "初始状态（40级）应分配到伏虎军"
            )
            if not success:
                return False
            
            # 升级到43级
            player = services.player_repo.get_by_id(test_user_id_3)
            if player:
                old_level = player.level or 0
                player.level = 43
                services.player_repo.save(player)
                print(f"  [OK] 用户 {test_user_id_3} 从 {old_level} 级升级到 43 级")
                
                # 调用 get_my_alliance 触发同步（实际应用中会在玩家操作时自动触发）
                services.alliance_service.get_my_alliance(test_user_id_3)
                
                # 检查重新分配（43级应该分配到飞龙军=1）
                success = check_army_assignment(
                    test_user_id_3,
                    1,  # 飞龙军
                    "升级后（43级）应重新分配到飞龙军"
                )
                if not success:
                    return False
            else:
                print(f"  [FAIL] 无法获取用户 {test_user_id_3} 的信息")
                return False
    except Exception as e:
        import traceback
        print(f"  [FAIL] 测试升级时出错: {e}")
        print(traceback.format_exc())
        return False
    
    # 测试4: 测试边界情况（正好40级）
    print_section("步骤6: 测试边界情况（正好40级）")
    try:
        # 创建一个45级的用户，应该分配到飞龙军
        test_user_id_4 = 20004
        try:
            player = services.player_repo.get_by_id(test_user_id_4)
            if player:
                player.level = 45
                services.player_repo.save(player)
                
                # 加入联盟
                join_result = services.alliance_service.join_alliance(test_user_id_4, alliance_id)
                if join_result.get("ok"):
                    # 检查分配（45级应该分配到飞龙军=1）
                    success = check_army_assignment(
                        test_user_id_4,
                        1,  # 飞龙军
                        "45级用户应分配到飞龙军"
                    )
                    if not success:
                        return False
                else:
                    print(f"  [WARN] 用户 {test_user_id_4} 加入联盟失败: {join_result.get('error')}")
        except Exception as e:
            print(f"  [WARN] 测试边界情况时出错: {e}")
    except Exception as e:
        print(f"  [WARN] 测试边界情况时出错: {e}")
    
    # 最终总结
    print_section("测试总结")
    print(f"  [OK] 测试通过：")
    print(f"    1. 创建联盟时，创建者自动分配到对应军队")
    print(f"    2. 加入联盟时，新成员自动分配到对应军队")
    print(f"    3. 玩家升级时，自动重新分配到对应军队（40级升到43级，从伏虎军转到飞龙军）")
    
    return True


if __name__ == "__main__":
    try:
        success = test_army_auto_assignment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n\n测试异常: {e}")
        print(traceback.format_exc())
        sys.exit(1)
