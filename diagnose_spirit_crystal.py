"""诊断灵力水晶功能"""
import json
import os

def check_item_config():
    """检查道具配置"""
    print("=== 1. 检查道具配置 ===")
    
    config_path = "configs/items.json"
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    with open(config_path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    crystal = None
    for item in items:
        if item.get('id') == 6101:
            crystal = item
            break
    
    if crystal:
        print(f"✓ 找到灵力水晶配置:")
        print(f"  - ID: {crystal['id']}")
        print(f"  - 名称: {crystal['name']}")
        print(f"  - 类型: {crystal['type']}")
        print(f"  - 描述: {crystal['description']}")
        return True
    else:
        print("❌ 未找到灵力水晶配置 (ID: 6101)")
        return False

def check_route_config():
    """检查路由配置"""
    print("\n=== 2. 检查前端路由配置 ===")
    
    # 检查 itemUseRoutes.js
    routes_path = "interfaces/client/src/utils/itemUseRoutes.js"
    if not os.path.exists(routes_path):
        print(f"❌ 路由配置文件不存在: {routes_path}")
        return False
    
    with open(routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '6101' in content and '/spirit/crystal-use' in content:
        print("✓ itemUseRoutes.js 中已配置灵力水晶路由")
        print("  - 道具ID: 6101")
        print("  - 路由: /spirit/crystal-use")
    else:
        print("❌ itemUseRoutes.js 中未找到灵力水晶路由配置")
        return False
    
    # 检查 router/index.js
    router_path = "interfaces/client/src/router/index.js"
    if not os.path.exists(router_path):
        print(f"❌ 路由文件不存在: {router_path}")
        return False
    
    with open(router_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'SpiritCrystalUsePage' in content and '/spirit/crystal-use' in content:
        print("✓ router/index.js 中已注册灵力水晶使用页面")
        print("  - 组件: SpiritCrystalUsePage")
        print("  - 路径: /spirit/crystal-use")
    else:
        print("❌ router/index.js 中未找到灵力水晶使用页面路由")
        return False
    
    return True

def check_page_component():
    """检查页面组件"""
    print("\n=== 3. 检查前端页面组件 ===")
    
    page_path = "interfaces/client/src/features/beast/SpiritCrystalUsePage.vue"
    if not os.path.exists(page_path):
        print(f"❌ 页面组件不存在: {page_path}")
        return False
    
    with open(page_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('loadData', '加载数据函数'),
        ('useCrystal', '使用水晶函数'),
        ('/spirit/consume-crystal', 'API接口调用'),
        ('item_id === 6101', '道具ID检查'),
    ]
    
    all_ok = True
    for check_str, desc in checks:
        if check_str in content:
            print(f"✓ {desc} 存在")
        else:
            print(f"❌ {desc} 缺失")
            all_ok = False
    
    return all_ok

def check_backend_route():
    """检查后端路由"""
    print("\n=== 4. 检查后端路由 ===")
    
    route_path = "interfaces/routes/spirit_routes.py"
    if not os.path.exists(route_path):
        print(f"❌ 后端路由文件不存在: {route_path}")
        return False
    
    with open(route_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'consume-crystal' in content and 'consume_spirit_crystal' in content:
        print("✓ 后端路由已配置")
        print("  - 路由: /api/spirit/consume-crystal")
        print("  - 服务方法: consume_spirit_crystal")
    else:
        print("❌ 后端路由未配置")
        return False
    
    return True

def check_backend_service():
    """检查后端服务"""
    print("\n=== 5. 检查后端服务 ===")
    
    service_path = "application/services/spirit_service.py"
    if not os.path.exists(service_path):
        print(f"❌ 后端服务文件不存在: {service_path}")
        return False
    
    with open(service_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('consume_spirit_crystal', '消耗水晶方法'),
        ('SPIRIT_CRYSTAL_ITEM_ID = 6101', '道具ID常量'),
        ('POWER_PER_CRYSTAL = 10', '兑换比例常量'),
    ]
    
    all_ok = True
    for check_str, desc in checks:
        if check_str in content:
            print(f"✓ {desc} 存在")
        else:
            print(f"❌ {desc} 缺失")
            all_ok = False
    
    return all_ok

def check_inventory_page():
    """检查背包页面"""
    print("\n=== 6. 检查背包页面 ===")
    
    inv_path = "interfaces/client/src/features/inventory/InventoryPage.vue"
    if not os.path.exists(inv_path):
        print(f"❌ 背包页面不存在: {inv_path}")
        return False
    
    with open(inv_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('getItemUseRoute', '导入路由工具函数'),
        ('openUseSelect', '使用道具函数'),
        ('router.push(useRoute)', '路由跳转'),
    ]
    
    all_ok = True
    for check_str, desc in checks:
        if check_str in content:
            print(f"✓ {desc} 存在")
        else:
            print(f"❌ {desc} 缺失")
            all_ok = False
    
    return all_ok

def main():
    print("灵力水晶功能诊断")
    print("=" * 60)
    
    results = []
    
    results.append(("道具配置", check_item_config()))
    results.append(("前端路由配置", check_route_config()))
    results.append(("前端页面组件", check_page_component()))
    results.append(("后端路由", check_backend_route()))
    results.append(("后端服务", check_backend_service()))
    results.append(("背包页面", check_inventory_page()))
    
    print("\n" + "=" * 60)
    print("诊断结果汇总:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有检查通过！灵力水晶功能配置完整。")
        print("\n可能的问题:")
        print("1. 后端服务未启动")
        print("2. 前端未重新编译")
        print("3. 浏览器缓存问题")
        print("\n建议操作:")
        print("1. 启动后端服务: python start-backend.bat")
        print("2. 启动前端服务: npm run dev (在 interfaces/client 目录)")
        print("3. 清除浏览器缓存并刷新页面")
        print("4. 在背包中找到灵力水晶，点击【使用】按钮")
        print("5. 应该会自动跳转到 /spirit/crystal-use 页面")
    else:
        print("❌ 发现配置问题，请根据上述检查结果修复。")

if __name__ == "__main__":
    main()
