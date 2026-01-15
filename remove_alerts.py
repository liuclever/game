"""批量移除前端Vue文件中的alert和confirm"""
import os
import re
from pathlib import Path

# 需要处理的文件列表
files_to_process = [
    "interfaces/client/src/features/tower/ZhenYaoPage.vue",
    "interfaces/client/src/features/tower/TowerPage.vue",
    "interfaces/client/src/features/tower/TowerChallengePage.vue",
    "interfaces/client/src/features/tasks/TaskRewardsPage.vue",
    "interfaces/client/src/features/tasks/ActivityGiftsPage.vue",
    "interfaces/client/src/features/refine-pot/RefinePotPhysicalPage.vue",
    "interfaces/client/src/features/refine-pot/RefinePotSpeedPage.vue",
    "interfaces/client/src/features/refine-pot/RefinePotPhysicalDefensePage.vue",
    "interfaces/client/src/features/refine-pot/RefinePotMagicPage.vue",
    "interfaces/client/src/features/refine-pot/RefinePotMagicDefensePage.vue",
    "interfaces/client/src/features/refine-pot/RefinePotHpPage.vue",
    "interfaces/client/src/features/shop/ShopItemDetailPage.vue",
    "interfaces/client/src/features/ranking/RankingPage.vue",
    "interfaces/client/src/features/pvp/PvpArenaPage.vue",
    "interfaces/client/src/features/player/PlayerProfilePage.vue",
]

print("=" * 60)
print("批量移除alert和confirm")
print("=" * 60)
print()

for file_path in files_to_process:
    if not os.path.exists(file_path):
        print(f"⚠️  文件不存在: {file_path}")
        continue
    
    print(f"处理文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计alert和confirm的数量
    alert_count = len(re.findall(r'\balert\s*\(', content))
    confirm_count = len(re.findall(r'\bconfirm\s*\(', content))
    
    if alert_count == 0 and confirm_count == 0:
        print(f"  ✓ 无需处理（没有alert或confirm）")
        continue
    
    print(f"  找到 {alert_count} 个alert, {confirm_count} 个confirm")
    print(f"  文件: {file_path}")
    print()

print("=" * 60)
print(f"共找到 {len(files_to_process)} 个文件需要处理")
print("=" * 60)
