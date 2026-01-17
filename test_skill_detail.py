"""
测试技能详情查询功能
验证：通过技能名称和key都能查询到技能详情
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from interfaces.web_api.bootstrap import services

def test_skill_detail():
    """测试技能详情查询"""
    print("=" * 60)
    print("测试技能详情查询功能")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        ("gjbx", "高级必杀", "通过key查询"),
        ("高级必杀", "高级必杀", "通过技能名称查询"),
        ("gjlj", "高级连击", "通过key查询"),
        ("高级连击", "高级连击", "通过技能名称查询"),
        ("fy", "防御", "通过key查询"),
        ("防御", "防御", "通过技能名称查询"),
        ("invalid_key", None, "无效的key"),
        ("不存在的技能", None, "不存在的技能名称"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for query, expected_name, description in test_cases:
        print(f"\n测试: {description}")
        print(f"  查询参数: {query}")
        
        result = services.handbook_service.get_skill_detail(query)
        
        if expected_name is None:
            # 期望查询失败
            if not result.get("ok"):
                print(f"  ✓ 正确返回失败: {result.get('error')}")
                success_count += 1
            else:
                print(f"  ❌ 应该失败但成功了: {result}")
                fail_count += 1
        else:
            # 期望查询成功
            if result.get("ok"):
                skill = result.get("skill", {})
                actual_name = skill.get("name")
                if actual_name == expected_name:
                    print(f"  ✓ 查询成功")
                    print(f"    技能名称: {actual_name}")
                    print(f"    技能描述: {skill.get('desc', '')[:50]}...")
                    success_count += 1
                else:
                    print(f"  ❌ 技能名称不匹配")
                    print(f"    期望: {expected_name}")
                    print(f"    实际: {actual_name}")
                    fail_count += 1
            else:
                print(f"  ❌ 查询失败: {result.get('error')}")
                fail_count += 1
    
    print("\n" + "=" * 60)
    print(f"测试完成: 成功 {success_count}/{len(test_cases)}, 失败 {fail_count}/{len(test_cases)}")
    print("=" * 60)
    
    if fail_count == 0:
        print("\n✓ 所有测试通过！")
    else:
        print(f"\n❌ 有 {fail_count} 个测试失败")

if __name__ == '__main__':
    test_skill_detail()
