#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试盟战配对修复
验证3号和4号土地是否能正确配对
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from interfaces.web_api.bootstrap import services
from domain.entities.alliance_registration import STATUS_REGISTERED

def test_land_pairing(land_id: int):
    """测试单个土地的配对"""
    print(f"\n{'='*60}")
    print(f"测试土地 {land_id} 的配对")
    print(f"{'='*60}\n")
    
    # 1. 检查报名情况
    print(f"[步骤1] 检查报名情况...")
    all_registrations = services.alliance_repo.list_land_registrations_by_land(land_id)
    registrations_for_pairing = services.alliance_repo.list_land_registrations_by_land(
        land_id, statuses=[STATUS_REGISTERED]
    )
    print(f"  总报名数: {len(all_registrations)}")
    print(f"  可用于配对的报名数: {len(registrations_for_pairing)}")
    
    for reg in registrations_for_pairing:
        print(f"  - 联盟 {reg.alliance_id}, 军队: {reg.army}")
    
    if len(registrations_for_pairing) < 2:
        print(f"  [X] 至少需要2个联盟报名才能配对，当前只有 {len(registrations_for_pairing)} 个")
        return False
    
    # 2. 尝试配对
    print(f"\n[步骤2] 尝试配对...")
    try:
        pair_result = services.alliance_battle_service.lock_and_pair_land(land_id)
        if pair_result.get("ok"):
            battles = pair_result.get("battles", [])
            print(f"  [OK] 配对成功！共 {len(battles)} 场对战")
            for battle in battles:
                print(f"    - 对战 {battle['battle_id']}: 联盟 {battle['left_alliance_id']} vs 联盟 {battle['right_alliance_id']}")
            return True
        else:
            error = pair_result.get("error", "未知错误")
            print(f"  [X] 配对失败: {error}")
            if "validation_errors" in pair_result:
                print(f"  详细错误:")
                for err in pair_result["validation_errors"]:
                    print(f"    - {err}")
            return False
    except Exception as e:
        print(f"  [X] 配对时发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("="*60)
    print("盟战配对修复测试")
    print("="*60)
    
    # 测试3号和4号土地
    success_count = 0
    for land_id in [3, 4]:
        if test_land_pairing(land_id):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"测试完成: {success_count}/2 个土地配对成功")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
