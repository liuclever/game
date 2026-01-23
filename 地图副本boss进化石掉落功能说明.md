# 地图副本Boss进化石掉落功能说明

## 功能概述

在地图副本挑战35层（Boss层）时，击败Boss并开启战利品后，有30%概率获得对应地图的进化石。

## 进化石掉落规则

### 掉落对应关系

| 地图 | 副本 | 进化石 | 掉落概率 | 物品ID |
|------|------|--------|---------|--------|
| 定老城 | 石工矿场、幻灵湖畔 | 黄阶进化石 | 30% | 3001 |
| 迷雾城 | 回音之谷、死亡沼泽 | 玄阶进化石 | 30% | 3002 |
| 飞龙港 | 日落海峡、聚灵孤岛 | 地阶进化石 | 30% | 3003 |
| 落龙镇 | 龙骨墓地、巨龙冰原 | 天阶进化石 | 30% | 3004 |
| 圣龙城 | 圣龙城郊、皇城迷宫 | 飞马进化石 | 30% | 3005 |
| 乌托邦 | 梦幻海湾、幻光公园 | 天龙进化石 | 30% | 3006 |

### Boss战利品完整奖励

**基础奖励（100%）：**
- 铜钱 × 600
- 随机结晶 × 1

**额外奖励（概率掉落）：**
- 骨魂 × 1（30%概率）
- 进化石 × 1（30%概率）

**双倍卡效果：**
- 使用双倍卡开启战利品时，所有奖励数量翻倍

## 实现方式

### 1. 新增函数

在 `interfaces/routes/dungeon_routes.py` 中添加了 `get_evolution_stone_item_id()` 函数：

```python
def get_evolution_stone_item_id(dungeon_name):
    """根据副本/地图获取对应的进化石 ID"""
    dungeon_config = load_dungeon_config()
    
    # 查找所属地图
    target_map = None
    for m in dungeon_config['maps']:
        for d in m['dungeons']:
            if d['name'] == dungeon_name:
                target_map = m
                break
        if target_map: break
        
    if not target_map:
        return None
        
    map_name = target_map['map_name']
    
    # 根据地图返回对应的进化石ID
    if map_name == "定老城": return 3001  # 黄阶进化石
    if map_name == "迷雾城": return 3002  # 玄阶进化石
    if map_name == "飞龙港": return 3003  # 地阶进化石
    if map_name == "落龙镇": return 3004  # 天阶进化石
    if map_name == "圣龙城": return 3005  # 飞马进化石
    if map_name == "乌托邦": return 3006  # 天龙进化石
        
    return None
```

### 2. 修改战利品发放逻辑

在 `open_loot()` 函数的Boss奖励部分添加了进化石掉落：

```python
# 30% 概率出进化石
if random.random() < 0.3:
    evolution_stone_id = get_evolution_stone_item_id(dungeon_name)
    if evolution_stone_id:
        evolution_stone_amount = 1 * multiplier
        services.inventory_service.add_item(user_id, evolution_stone_id, evolution_stone_amount)
        
        # 获取进化石名称
        evolution_stone_names = {
            3001: "黄阶进化石", 3002: "玄阶进化石", 3003: "地阶进化石",
            3004: "天阶进化石", 3005: "飞马进化石", 3006: "天龙进化石"
        }
        rewards["evolution_stone"] = {
            "id": evolution_stone_id,
            "name": evolution_stone_names.get(evolution_stone_id, "进化石"),
            "amount": evolution_stone_amount
        }
```

## 游戏流程

### 1. 挑战Boss

1. 玩家进入地图副本（例如：定老城的幻灵湖畔）
2. 使用骰子前进到第35层（Boss层）
3. 击败Boss

### 2. 开启战利品

1. 战斗胜利后，可以选择开启战利品
2. 消耗15点活力或1张双倍卡
3. 获得奖励

### 3. 奖励内容

**必得奖励：**
- 铜钱 × 600（双倍卡：1200）
- 随机结晶 × 1（双倍卡：2）

**可能获得（30%概率）：**
- 骨魂 × 1（双倍卡：2）
- 进化石 × 1（双倍卡：2）

## 示例场景

### 场景1：定老城幻灵湖畔

玩家在定老城的幻灵湖畔副本挑战35层Boss：

**必得奖励：**
- 铜钱 × 600
- 金之结晶 × 1（随机）

**幸运掉落（30%概率）：**
- 猎魔骨魂 × 1
- 黄阶进化石 × 1

### 场景2：乌托邦幻光公园（使用双倍卡）

玩家在乌托邦的幻光公园副本挑战35层Boss，使用双倍卡开启战利品：

**必得奖励：**
- 铜钱 × 1200
- 水之结晶 × 2（随机）

**幸运掉落（30%概率）：**
- 毁灭骨魂 × 2
- 天龙进化石 × 2

## 测试验证

### 测试脚本

```bash
python test_dungeon_boss_evolution_stone.py
```

### 测试结果

所有地图的进化石映射关系测试通过：

- ✓ 定老城 → 黄阶进化石
- ✓ 迷雾城 → 玄阶进化石
- ✓ 飞龙港 → 地阶进化石
- ✓ 落龙镇 → 天阶进化石
- ✓ 圣龙城 → 飞马进化石
- ✓ 乌托邦 → 天龙进化石

## 注意事项

1. **只有Boss层（35层）才掉落进化石**：普通层（1-34层）不掉落进化石
2. **概率独立**：骨魂和进化石的掉落概率是独立的，可能同时获得，也可能都不获得
3. **双倍卡效果**：使用双倍卡时，如果触发掉落，进化石数量会翻倍（1 → 2）
4. **地图对应**：进化石类型由地图决定，不是由副本决定（同一地图的所有副本掉落相同的进化石）

## 相关文件

### 修改的文件
- `interfaces/routes/dungeon_routes.py` - 添加进化石掉落逻辑

### 测试文件
- `test_dungeon_boss_evolution_stone.py` - 进化石掉落测试脚本

### 配置文件
- `configs/dungeon_config.json` - 地图副本配置
- `configs/items.json` - 物品配置（进化石定义）

## 总结

地图副本Boss进化石掉落功能已完整实现：

1. ✓ 根据地图掉落对应的进化石
2. ✓ 30%掉落概率
3. ✓ 支持双倍卡翻倍
4. ✓ 与骨魂掉落独立计算
5. ✓ 测试验证通过

玩家在挑战地图副本35层Boss时，有机会获得对应地图的进化石，为幻兽进化提供材料来源。
