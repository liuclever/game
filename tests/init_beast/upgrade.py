"""tests/init_beast/upgrade.py

脚本：给指定玩家的指定幻兽派发经验，用于测试幻兽升级。

使用方法：
1. 修改下方配置变量
2. 在项目根目录运行：python -m tests.init_beast.upgrade

配置说明：
- USER_ID: 玩家ID（默认4035）
- BEAST_ID: 要派发经验的幻兽ID（设为None则显示玩家所有幻兽列表供选择）
- EXP_AMOUNT: 派发的经验数量
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infrastructure.db.player_beast_repo_mysql import MySQLPlayerBeastRepo
from infrastructure.config.beast_template_repo_from_config import ConfigBeastTemplateRepo
from application.services.beast_service import BeastService

# ==================== 配置区域 ====================
USER_ID = 4035          # 玩家ID
BEAST_ID = None         # 幻兽ID（设为None则列出所有幻兽供选择）
EXP_AMOUNT = 100000     # 派发经验数量
# ================================================


def list_beasts(beast_repo, template_repo, user_id: int):
    """列出玩家所有幻兽"""
    beasts = beast_repo.get_by_user_id(user_id)
    if not beasts:
        print(f"玩家 {user_id} 没有幻兽")
        return []
    
    print(f"\n玩家 {user_id} 的幻兽列表：")
    print("-" * 60)
    for b in beasts:
        template = template_repo.get_by_id(b.template_id)
        template_name = template.name if template else "未知"
        name = b.nickname or template_name
        print(f"  ID: {b.id:5d} | {name:12s} | Lv.{b.level:3d} | 境界: {b.realm or '地界':4s} | 经验: {b.exp}")
    print("-" * 60)
    return beasts


def add_exp_to_beast(beast_service: BeastService, user_id: int, beast_id: int, exp: int):
    """给幻兽添加经验"""
    print(f"\n正在给幻兽 {beast_id} 添加 {exp} 经验...")
    
    try:
        result = beast_service.add_exp_to_beast(user_id, beast_id, exp)
        beast = result.beast
        template = result.template
        
        name = beast.nickname or (template.name if template else "未知")
        print(f"\n✓ 经验添加成功！")
        print(f"  幻兽: {name}")
        print(f"  当前等级: Lv.{beast.level}")
        print(f"  当前经验: {beast.exp}")
        print(f"  境界: {beast.realm or '地界'}")
        return True
    except Exception as e:
        print(f"\n✗ 经验添加失败: {e}")
        return False


def main():
    # 初始化仓库和服务
    beast_repo = MySQLPlayerBeastRepo()
    template_repo = ConfigBeastTemplateRepo()
    beast_service = BeastService(template_repo=template_repo, beast_repo=beast_repo)
    
    print("=" * 60)
    print("幻兽经验派发工具")
    print("=" * 60)
    print(f"目标玩家ID: {USER_ID}")
    print(f"派发经验量: {EXP_AMOUNT}")
    
    # 列出玩家幻兽
    beasts = list_beasts(beast_repo, template_repo, USER_ID)
    if not beasts:
        return
    
    # 确定目标幻兽
    target_beast_id = BEAST_ID
    if target_beast_id is None:
        # 交互式选择
        print("\n请输入要派发经验的幻兽ID（或直接修改脚本中的 BEAST_ID 变量）:")
        try:
            target_beast_id = int(input("> "))
        except (ValueError, EOFError):
            print("输入无效，退出")
            return
    
    # 验证幻兽ID属于该玩家
    beast_ids = [b.id for b in beasts]
    if target_beast_id not in beast_ids:
        print(f"\n✗ 幻兽ID {target_beast_id} 不属于玩家 {USER_ID}")
        return
    
    # 派发经验
    add_exp_to_beast(beast_service, USER_ID, target_beast_id, EXP_AMOUNT)
    
    # 显示更新后的列表
    print("\n更新后的幻兽列表：")
    list_beasts(beast_repo, template_repo, USER_ID)


if __name__ == "__main__":
    main()
