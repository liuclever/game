"""确保灵力水晶路由配置正确"""
import os
import re

def ensure_route_in_itemUseRoutes():
    """确保 itemUseRoutes.js 中有灵力水晶的路由配置"""
    file_path = "interfaces/client/src/utils/itemUseRoutes.js"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经有配置
    if '6101' in content and '/spirit/crystal-use' in content:
        print(f"✓ {file_path} 中已有灵力水晶路由配置")
        return True
    
    # 如果没有，添加配置
    print(f"⚠ {file_path} 中缺少灵力水晶路由配置，正在添加...")
    
    # 在 ITEM_USE_ROUTES 对象中添加
    pattern = r'(// 战灵钥匙：跳转战灵页用于激活属性条\s+6006: \'/spirit/warehouse\',)'
    replacement = r'\1\n\n  // 灵力水晶：跳转灵力水晶使用页面\n  6101: \'/spirit/crystal-use\','
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
    else:
        # 如果找不到战灵钥匙的配置，在 ITEM_USE_ROUTES 结束前添加
        pattern = r'(export const ITEM_USE_ROUTES = \{[^}]+)(}\s*\n)'
        replacement = r'\1  // 灵力水晶：跳转灵力水晶使用页面\n  6101: \'/spirit/crystal-use\',\n\2'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # 在 ITEM_USE_HINTS 对象中添加
    pattern = r'(6006: \'战灵钥匙：请前往\【战灵-灵件室/属性\】界面用于激活第2/第3条属性条。\',)'
    replacement = r'\1\n  6101: \'灵力水晶：请前往【战灵】界面兑换灵力。\','
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ 已添加灵力水晶路由配置到 {file_path}")
    return True

def ensure_route_in_router():
    """确保 router/index.js 中注册了灵力水晶使用页面"""
    file_path = "interfaces/client/src/router/index.js"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经导入组件
    if 'SpiritCrystalUsePage' not in content:
        print(f"⚠ {file_path} 中缺少 SpiritCrystalUsePage 导入")
        
        # 在其他 Spirit 相关导入后添加
        pattern = r'(import SpiritWarehouseSellResultPage from \'@/features/beast/SpiritWarehouseSellResultPage\.vue\')'
        replacement = r'\1\nimport SpiritCrystalUsePage from \'@/features/beast/SpiritCrystalUsePage.vue\''
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            print(f"✓ 已添加 SpiritCrystalUsePage 导入")
        else:
            print(f"❌ 无法找到合适的位置添加导入")
            return False
    else:
        print(f"✓ {file_path} 中已导入 SpiritCrystalUsePage")
    
    # 检查是否已经注册路由
    if "path: '/spirit/crystal-use'" not in content:
        print(f"⚠ {file_path} 中缺少灵力水晶使用页面路由")
        
        # 在 spirit/warehouse/sell-result 路由后添加
        pattern = r'(\{\s+path: \'/spirit/warehouse/sell-result\',\s+name: \'SpiritWarehouseSellResult\',\s+component: SpiritWarehouseSellResultPage,\s+\},)'
        replacement = r'''\1
  {
    path: '/spirit/crystal-use',
    name: 'SpiritCrystalUse',
    component: SpiritCrystalUsePage,
  },'''
        
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            print(f"✓ 已添加灵力水晶使用页面路由")
        else:
            print(f"❌ 无法找到合适的位置添加路由")
            return False
    else:
        print(f"✓ {file_path} 中已注册灵力水晶使用页面路由")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def check_component_exists():
    """检查组件文件是否存在"""
    file_path = "interfaces/client/src/features/beast/SpiritCrystalUsePage.vue"
    
    if os.path.exists(file_path):
        print(f"✓ 组件文件存在: {file_path}")
        return True
    else:
        print(f"❌ 组件文件不存在: {file_path}")
        print("   需要创建该文件！")
        return False

def main():
    print("灵力水晶路由配置修复脚本")
    print("=" * 60)
    
    results = []
    
    print("\n1. 检查组件文件...")
    results.append(check_component_exists())
    
    print("\n2. 检查 itemUseRoutes.js...")
    results.append(ensure_route_in_itemUseRoutes())
    
    print("\n3. 检查 router/index.js...")
    results.append(ensure_route_in_router())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ 所有配置检查/修复完成！")
        print("\n后续步骤:")
        print("1. 重启前端服务: cd interfaces/client && npm run dev")
        print("2. 清除浏览器缓存")
        print("3. 测试灵力水晶使用功能")
    else:
        print("❌ 部分配置存在问题，请手动检查")

if __name__ == "__main__":
    main()
