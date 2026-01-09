"""添加战骨升级材料并测试升级

运行方式（项目根目录）：
    python tests/bone/add_meterial.py

前置条件：
    - Flask 应用已启动: python -m interfaces.web_api.app
    - 数据库中存在测试账号（默认使用 test1/123456）

功能：
    1. 添加强化石（战骨升级材料）
    2. 创建战骨（如果需要）
    3. 查询升级消耗
    4. 执行战骨升级
"""

import requests

# ==================== 配置 ====================
BASE_URL = "http://127.0.0.1:5000"

# 默认测试账号（需要在数据库中已存在）
DEFAULT_USERNAME = "test1"
DEFAULT_PASSWORD = "123456"

# 强化石 item_id（来自 bone_system.json）
STRENGTHEN_STONE_ID = 9001

# 战骨模板ID（来自 bone_templates.json）
BONE_TEMPLATES = {
    910001: "基础头骨",
    910002: "基础胸骨",
    910003: "基础臂骨",
    910004: "基础手骨",
    910005: "基础腿骨",
    910006: "基础尾骨",
    910007: "基础元魂",
}


class BoneUpgradeTester:
    """战骨升级测试工具"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.logged_in = False
        self.user_id = None
    
    def login(self, username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> dict:
        """登录（获取 session）"""
        resp = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        data = self._safe_json(resp)
        if data.get("ok"):
            self.logged_in = True
            self.user_id = data.get("user_id")
            print(f"✅ 登录成功：{data.get('nickname', username)} (user_id={self.user_id})")
        else:
            print(f"❌ 登录失败：{data.get('error')}")
        return data
    
    def ensure_logged_in(self, username: str = DEFAULT_USERNAME, password: str = DEFAULT_PASSWORD) -> bool:
        """确保已登录，返回是否成功"""
        if self.logged_in:
            return True
        
        result = self.login(username, password)
        if result.get("ok"):
            return True
        
        # 登录失败，提示用户如何创建账号
        print("\n" + "=" * 50)
        print("⚠️ 需要先在数据库中创建测试账号！")
        print("请在 MySQL 中执行以下 SQL：")
        print("-" * 50)
        print(f"""
-- 1. 先创建用户（auth_users 表）
INSERT INTO auth_users (username, password_hash, nickname) 
VALUES ('{username}', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.V4ferT6LWz.Nh2', '测试玩家');

-- 2. 获取刚创建的 user_id
SET @uid = LAST_INSERT_ID();

-- 3. 创建玩家数据（players 表）
INSERT INTO players (user_id, nickname, level, gold) 
VALUES (@uid, '测试玩家', 50, 100000);
""")
        print("-" * 50)
        print("或者使用已有账号运行（修改脚本中的 DEFAULT_USERNAME）")
        print("=" * 50 + "\n")
        return False
    
    def _safe_json(self, resp) -> dict:
        """安全解析 JSON 响应"""
        try:
            return resp.json()
        except Exception:
            print(f"⚠️ 响应解析失败，状态码: {resp.status_code}")
            print(f"   响应内容: {resp.text[:200] if resp.text else '(空)'}")
            return {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:100]}"}
    
    def add_strengthen_stones(self, quantity: int = 1000) -> dict:
        """添加强化石（使用需要登录的正式接口）"""
        resp = self.session.post(
            f"{self.base_url}/api/inventory/add",
            json={"item_id": STRENGTHEN_STONE_ID, "quantity": quantity}
        )
        data = self._safe_json(resp)
        if data.get("ok"):
            item_info = data.get("item", {})
            is_temp = item_info.get("is_temporary", False)
            print(f"✅ 添加强化石成功：+{quantity} 个")
            print(f"   物品ID: {item_info.get('id')}, 数量: {item_info.get('quantity')}, 临时背包: {'是' if is_temp else '否'}")
        else:
            print(f"❌ 添加强化石失败：{data.get('error')}")
        return data
    
    def get_inventory(self) -> list:
        """获取背包物品列表（正式背包）"""
        resp = self.session.get(f"{self.base_url}/api/inventory/list")
        data = self._safe_json(resp)
        if data.get("ok"):
            items = data.get("items", [])
            # 显示背包信息
            bag_info = data.get("bag_info", {})
            print(f"   背包容量: {bag_info.get('current_slots', 0)}/{bag_info.get('capacity', 0)}")
            return items
        else:
            print(f"❌ 获取背包失败：{data.get('error')}")
        return []
    
    def get_temp_inventory(self) -> list:
        """获取临时背包物品列表"""
        resp = self.session.get(f"{self.base_url}/api/inventory/temp")
        data = self._safe_json(resp)
        if data.get("ok"):
            return data.get("items", [])
        else:
            print(f"❌ 获取临时背包失败：{data.get('error')}")
        return []
    
    def get_item_count(self, item_id: int, include_temp: bool = True) -> int:
        """查询指定物品的数量（包括临时背包）"""
        total = 0
        
        # 正式背包
        items = self.get_inventory()
        for item in items:
            if item.get("item_id") == item_id:
                total += item.get("quantity", 0)
        
        # 临时背包
        if include_temp:
            temp_items = self.get_temp_inventory()
            for item in temp_items:
                if item.get("item_id") == item_id:
                    total += item.get("quantity", 0)
        
        return total
    
    def get_strengthen_stone_count(self) -> int:
        """查询强化石数量（包括临时背包）"""
        # 正式背包
        items = self.get_inventory()
        normal_count = sum(item.get("quantity", 0) for item in items if item.get("item_id") == STRENGTHEN_STONE_ID)
        
        # 临时背包
        temp_items = self.get_temp_inventory()
        temp_count = sum(item.get("quantity", 0) for item in temp_items if item.get("item_id") == STRENGTHEN_STONE_ID)
        
        total = normal_count + temp_count
        print(f"💎 当前强化石数量：{total} 个（正式背包: {normal_count}, 临时背包: {temp_count}）")
        return total
    
    def create_bone(self, template_id: int = 910001, stage: int = 1, level: int = 1) -> dict:
        """创建战骨（使用需要登录的正式接口）"""
        template_name = BONE_TEMPLATES.get(template_id, f"模板{template_id}")
        resp = self.session.post(
            f"{self.base_url}/api/bone/create",
            json={"template_id": template_id, "stage": stage, "level": level}
        )
        data = self._safe_json(resp)
        if data.get("ok"):
            bone = data["bone"]
            print(f"✅ 创建战骨成功：{template_name}")
            print(f"   ID: {bone['id']}, 槽位: {bone['slot']}, 等级: {bone['level']}, 阶段: {bone['stage']}")
        else:
            print(f"❌ 创建战骨失败：{data.get('error')}")
        return data
    
    def get_bone_list(self) -> list:
        """获取战骨列表（使用需要登录的正式接口）"""
        resp = self.session.get(f"{self.base_url}/api/bone/list")
        data = self._safe_json(resp)
        if data.get("ok"):
            bones = data.get("bones", [])
            print(f"📋 当前拥有 {len(bones)} 枚战骨：")
            for bone in bones:
                print(f"   ID:{bone['id']} | {bone['slot']} | Lv.{bone['level']} | 阶段{bone['stage']} | {bone.get('stage_name', '')}")
            return bones
        else:
            print(f"❌ 获取战骨列表失败：{data.get('error')}")
        return []
    
    def get_upgrade_cost(self, bone_id: int) -> dict:
        """查询升级消耗"""
        resp = self.session.get(f"{self.base_url}/api/bone/{bone_id}/upgrade-cost")
        data = self._safe_json(resp)
        if data.get("ok"):
            print(f"📊 战骨 {bone_id} 升级消耗：")
            print(f"   当前等级: {data['current_level']} → 目标等级: {data.get('target_level', '?')}")
            print(f"   可升级: {'✅ 是' if data['can_upgrade'] else '❌ 否'}")
            if not data['can_upgrade'] and data.get('reason'):
                print(f"   原因: {data['reason']}")
            for mat in data.get("materials", []):
                status = "✅" if mat["has_enough"] else "❌"
                print(f"   {status} {mat['name']}: 需要 {mat['required']}，拥有 {mat['owned']}")
        else:
            print(f"❌ 查询消耗失败：{data.get('error')}")
        return data
    
    def upgrade_bone(self, bone_id: int) -> dict:
        """升级战骨"""
        resp = self.session.post(f"{self.base_url}/api/bone/{bone_id}/upgrade")
        data = self._safe_json(resp)
        if data.get("ok"):
            bone = data["bone"]
            print(f"✅ 升级成功！")
            print(f"   新等级: {bone['level']}")
            print(f"   属性: HP+{bone['hp_flat']} 攻击+{bone['attack_flat']} 物防+{bone['physical_defense_flat']} 魔防+{bone['magic_defense_flat']} 速度+{bone['speed_flat']}")
        else:
            print(f"❌ 升级失败：{data.get('error')}")
        return data
    
    def upgrade_bone_to_level(self, bone_id: int, target_level: int) -> dict:
        """将战骨升级到指定等级"""
        print(f"\n🎯 目标：将战骨 {bone_id} 升级到 {target_level} 级")
        
        while True:
            cost = self.get_upgrade_cost(bone_id)
            if not cost.get("ok"):
                return cost
            
            current_level = cost.get("current_level", 0)
            if current_level >= target_level:
                print(f"✅ 已达到目标等级 {target_level}！")
                break
            
            if not cost.get("can_upgrade"):
                print(f"⚠️ 无法继续升级：{cost.get('reason')}")
                break
            
            result = self.upgrade_bone(bone_id)
            if not result.get("ok"):
                break
        
        return cost


def main():
    """主函数 - 演示完整的升级流程"""
    tester = BoneUpgradeTester()
    
    print("=" * 50)
    print("🦴 战骨升级材料添加与测试工具")
    print("=" * 50)
    
    # 0. 登录（必须！否则 upgrade-cost 等接口无法使用）
    print("\n【步骤0】登录")
    if not tester.ensure_logged_in():
        print("❌ 登录失败，无法继续测试")
        return
    
    # 1. 添加强化石
    print("\n【步骤1】添加强化石")
    tester.add_strengthen_stones(500)
    
    # 2. 查看现有战骨
    print("\n【步骤2】查看现有战骨")
    bones = tester.get_bone_list()
    
    # 3. 如果没有战骨，创建一个
    if not bones or len(bones) == 0:
        print("\n【步骤3】创建新战骨")
        create_result = tester.create_bone(template_id=910001, stage=1, level=1)
        if create_result.get("ok"):
            bone_id = create_result["bone"]["id"]
        else:
            print("无法创建战骨，退出")
            return
    else:
        bone_id = bones[0]["id"]
        print(f"\n【步骤3】使用已有战骨 ID: {bone_id}")
    
    # 4. 查询升级消耗
    print("\n【步骤4】查询升级消耗")
    tester.get_upgrade_cost(bone_id)
    
    # 5. 执行升级
    print("\n【步骤5】执行升级")
    tester.upgrade_bone(bone_id)
    
    # 6. 可选：连续升级到指定等级
    # print("\n【步骤6】连续升级到5级")
    # tester.upgrade_bone_to_level(bone_id, 5)
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")
    print("=" * 50)


def quick_add_materials(stone_qty: int = 1000, username: str = DEFAULT_USERNAME):
    """快速添加材料（不创建战骨、不升级）"""
    tester = BoneUpgradeTester()
    if not tester.ensure_logged_in(username=username, password=DEFAULT_PASSWORD):
        return
    tester.add_strengthen_stones(stone_qty)


def quick_upgrade(bone_id: int, times: int = 1, username: str = DEFAULT_USERNAME):
    """快速升级指定战骨"""
    tester = BoneUpgradeTester()
    if not tester.ensure_logged_in(username=username, password=DEFAULT_PASSWORD):
        return
    for i in range(times):
        print(f"\n--- 第 {i+1}/{times} 次升级 ---")
        result = tester.upgrade_bone(bone_id)
        if not result.get("ok"):
            break


def add_and_query_stones(add_qty: int = 500):
    """添加强化石并查询当前数量"""
    tester = BoneUpgradeTester()
    
    print("=" * 50)
    print("💎 强化石添加与查询工具")
    print("=" * 50)
    
    # 1. 登录
    print("\n【步骤1】登录")
    if not tester.ensure_logged_in():
        print("❌ 登录失败，无法继续")
        return
    
    # 2. 查询添加前的数量
    print("\n【步骤2】查询添加前的强化石数量")
    before_count = tester.get_strengthen_stone_count()
    
    # 3. 添加强化石
    print(f"\n【步骤3】添加 {add_qty} 个强化石")
    tester.add_strengthen_stones(add_qty)
    
    # 4. 查询添加后的数量
    print("\n【步骤4】查询添加后的强化石数量")
    after_count = tester.get_strengthen_stone_count()
    
    # 5. 显示结果
    print("\n" + "=" * 50)
    print(f"📊 结果汇总：")
    print(f"   添加前：{before_count} 个")
    print(f"   添加数量：+{add_qty} 个")
    print(f"   添加后：{after_count} 个")
    print("=" * 50)


if __name__ == "__main__":
    # 添加强化石并查询数量
    # add_and_query_stones(500)
    
    # 其他可用函数：
    main()                        # 完整的战骨升级流程
    # quick_add_materials(500)      # 只添加500个强化石
    # quick_upgrade(bone_id=1, times=5)  # 将战骨1升级5次

