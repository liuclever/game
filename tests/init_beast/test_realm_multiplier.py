"""
测试境界倍率规则：
- 最高境界对应倍率 1.0
- 依次递减 0.9, 0.85, 0.8
"""
from domain.services.beast_stats import get_realm_multiplier

def test_all_combinations():
    test_cases = [
        # (当前境界, 最高境界, 期望倍率)
        ("天界", "天界", 1.0),
        ("神界", "天界", 0.9),
        ("灵界", "天界", 0.85),
        ("地界", "天界", 0.8),
        
        ("神界", "神界", 1.0),
        ("灵界", "神界", 0.9),
        ("地界", "神界", 0.85),
        
        ("灵界", "灵界", 1.0),
        ("地界", "灵界", 0.9),
        
        ("地界", "地界", 1.0),
    ]
    
    all_pass = True
    for current, max_r, expected in test_cases:
        actual = get_realm_multiplier(current, max_r)
        status = "PASS" if actual == expected else "FAIL"
        print(f"[{status}] 当前={current}, 最高={max_r}: 期望={expected}, 实际={actual}")
        if actual != expected:
            all_pass = False
    
    print(f"\n{'全部通过！' if all_pass else '有测试失败！'}")
    return all_pass

if __name__ == "__main__":
    test_all_combinations()