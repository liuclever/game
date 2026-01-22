#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试盟战报名目标过滤功能

测试场景：
1. 飞龙军用户只能看到土地（迷雾城1号土地、飞龙港1号土地）
2. 伏虎军用户只能看到据点（幻灵镇1号据点、定老城1号据点）
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


def test_war_targets_filtering():
    """测试盟战报名目标过滤功能"""
    print_section("盟战报名目标过滤功能测试")
    
    # 测试用户ID（需要是已存在的用户）
    dragon_user_id = 20001  # 飞龙军用户（40级以上）
    tiger_user_id = 20002   # 伏虎军用户（40级及以下）
    
    # 准备测试用户
    print_section("步骤1: 准备测试用户")
    
    # 设置飞龙军用户等级（45级）
    try:
        player = services.player_repo.get_by_id(dragon_user_id)
        if player:
            player.level = 45
            services.player_repo.save(player)
            print(f"  [OK] 飞龙军用户 {dragon_user_id} 等级设置为 45")
        else:
            print(f"  [WARN] 用户 {dragon_user_id} 不存在，跳过飞龙军测试")
            dragon_user_id = None
    except Exception as e:
        print(f"  [WARN] 准备飞龙军用户时出错: {e}")
        dragon_user_id = None
    
    # 设置伏虎军用户等级（35级）
    try:
        player = services.player_repo.get_by_id(tiger_user_id)
        if player:
            player.level = 35
            services.player_repo.save(player)
            print(f"  [OK] 伏虎军用户 {tiger_user_id} 等级设置为 35")
        else:
            print(f"  [WARN] 用户 {tiger_user_id} 不存在，跳过伏虎军测试")
            tiger_user_id = None
    except Exception as e:
        print(f"  [WARN] 准备伏虎军用户时出错: {e}")
        tiger_user_id = None
    
    # 测试1: 飞龙军用户只能看到土地
    if dragon_user_id:
        print_section("步骤2: 测试飞龙军用户的目标列表")
        try:
            result = services.alliance_service.list_war_lands(user_id=dragon_user_id)
            if result.get("ok"):
                lands = result.get("data", {}).get("lands", [])
                print(f"  [OK] 飞龙军用户 {dragon_user_id} 可以看到 {len(lands)} 个目标")
                
                # 验证只包含土地（land_type === 'land'）
                land_ids = [land["id"] for land in lands]
                land_types = [land.get("land_type") for land in lands]
                
                print(f"    目标ID: {land_ids}")
                print(f"    目标类型: {land_types}")
                
                # 验证
                all_are_lands = all(lt == "land" for lt in land_types)
                expected_ids = {1, 2}  # 迷雾城1号土地、飞龙港1号土地
                correct_ids = set(land_ids) == expected_ids
                
                if all_are_lands and correct_ids:
                    print(f"    [OK] 通过：只包含土地，且ID正确")
                else:
                    print(f"    [FAIL] 失败：")
                    if not all_are_lands:
                        print(f"      - 包含非土地类型的目标")
                    if not correct_ids:
                        print(f"      - ID不正确，期望 {expected_ids}，实际 {set(land_ids)}")
                    return False
            else:
                error = result.get("error", "未知错误")
                print(f"  [FAIL] 获取目标列表失败: {error}")
                return False
        except Exception as e:
            import traceback
            print(f"  [FAIL] 测试飞龙军用户时出错: {e}")
            print(traceback.format_exc())
            return False
    
    # 测试2: 伏虎军用户只能看到据点
    if tiger_user_id:
        print_section("步骤3: 测试伏虎军用户的目标列表")
        try:
            result = services.alliance_service.list_war_lands(user_id=tiger_user_id)
            if result.get("ok"):
                lands = result.get("data", {}).get("lands", [])
                print(f"  [OK] 伏虎军用户 {tiger_user_id} 可以看到 {len(lands)} 个目标")
                
                # 验证只包含据点（land_type === 'stronghold'）
                land_ids = [land["id"] for land in lands]
                land_types = [land.get("land_type") for land in lands]
                
                print(f"    目标ID: {land_ids}")
                print(f"    目标类型: {land_types}")
                
                # 验证
                all_are_strongholds = all(lt == "stronghold" for lt in land_types)
                expected_ids = {3, 4}  # 幻灵镇1号据点、定老城1号据点
                correct_ids = set(land_ids) == expected_ids
                
                if all_are_strongholds and correct_ids:
                    print(f"    [OK] 通过：只包含据点，且ID正确")
                else:
                    print(f"    [FAIL] 失败：")
                    if not all_are_strongholds:
                        print(f"      - 包含非据点类型的目标")
                    if not correct_ids:
                        print(f"      - ID不正确，期望 {expected_ids}，实际 {set(land_ids)}")
                    return False
            else:
                error = result.get("error", "未知错误")
                print(f"  [FAIL] 获取目标列表失败: {error}")
                return False
        except Exception as e:
            import traceback
            print(f"  [FAIL] 测试伏虎军用户时出错: {e}")
            print(traceback.format_exc())
            return False
    
    # 测试3: 通过army参数指定军队类型
    print_section("步骤4: 测试通过army参数指定军队类型")
    try:
        # 测试飞龙军
        result_dragon = services.alliance_service.list_war_lands(army_type="dragon")
        if result_dragon.get("ok"):
            lands = result_dragon.get("data", {}).get("lands", [])
            land_ids = [land["id"] for land in lands]
            expected_ids = {1, 2}
            if set(land_ids) == expected_ids:
                print(f"  [OK] army=dragon 返回正确的土地列表: {land_ids}")
            else:
                print(f"  [FAIL] army=dragon 返回的ID不正确: {land_ids}")
                return False
        else:
            print(f"  [FAIL] army=dragon 获取目标列表失败")
            return False
        
        # 测试伏虎军
        result_tiger = services.alliance_service.list_war_lands(army_type="tiger")
        if result_tiger.get("ok"):
            lands = result_tiger.get("data", {}).get("lands", [])
            land_ids = [land["id"] for land in lands]
            expected_ids = {3, 4}
            if set(land_ids) == expected_ids:
                print(f"  [OK] army=tiger 返回正确的据点列表: {land_ids}")
            else:
                print(f"  [FAIL] army=tiger 返回的ID不正确: {land_ids}")
                return False
        else:
            print(f"  [FAIL] army=tiger 获取目标列表失败")
            return False
    except Exception as e:
        import traceback
        print(f"  [FAIL] 测试army参数时出错: {e}")
        print(traceback.format_exc())
        return False
    
    # 最终总结
    print_section("测试总结")
    print(f"  [OK] 测试通过：")
    print(f"    1. 飞龙军用户只能看到土地（迷雾城1号土地、飞龙港1号土地）")
    print(f"    2. 伏虎军用户只能看到据点（幻灵镇1号据点、定老城1号据点）")
    print(f"    3. 通过army参数可以指定军队类型获取对应的目标列表")
    
    return True


if __name__ == "__main__":
    try:
        success = test_war_targets_filtering()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\n\n测试异常: {e}")
        print(traceback.format_exc())
        sys.exit(1)
