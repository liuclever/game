
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain.services.beast_stats import get_beast_max_realm, get_realm_multiplier, REALM_ORDER

def test_multiplier():
    # 模拟采矿猴的模板境界
    mining_monkey_realms = ["地界", "灵界", "神界"]
    
    # 1. 测试获取最高境界
    max_realm = get_beast_max_realm(mining_monkey_realms)
    print(f"采矿猴最高境界: {max_realm} (期望: 神界)")
    
    # 2. 测试地界下的倍率
    mult_di = get_realm_multiplier("地界", max_realm)
    print(f"采矿猴地界倍率: {mult_di:.2f} (期望: 0.80)")
    
    # 3. 测试灵界下的倍率
    mult_ling = get_realm_multiplier("灵界", max_realm)
    print(f"采矿猴灵界倍率: {mult_ling:.2f} (期望: 0.90)")
    
    # 4. 测试神界下的倍率
    mult_shen = get_realm_multiplier("神界", max_realm)
    print(f"采矿猴神界倍率: {mult_shen:.2f} (期望: 1.00)")
    
    # 5. 测试普通幻兽 (最高灵界)
    common_realms = ["地界", "灵界"]
    common_max = get_beast_max_realm(common_realms)
    mult_common = get_realm_multiplier("地界", common_max)
    print(f"普通幻兽(最高灵界)地界倍率: {mult_common:.2f} (期望: 0.90)")

if __name__ == "__main__":
    test_multiplier()
