# 地图副本随机事件Bug修复说明

## 修复时间
2026年1月17日

## 问题描述
地图副本中，玩家扔骰子遇到随机事件（声望之塔、活力之泉、猜拳）时：
1. 随机事件没有怪物需要打
2. 但是事件失败后，`floor_cleared` 状态保持为 `FALSE`
3. 虽然扔骰子时不会提示"请先击败本层幻兽"（因为检查逻辑只针对 `beast` 和 `boss` 类型）
4. 但是 `floor_cleared = FALSE` 会导致前端显示混乱，玩家看到的提示和实际情况不符
5. 玩家体验：遇到随机事件后感觉卡住了，不知道该怎么继续

## 问题分析

### 随机事件类型
地图副本在特定楼层（5、10、15、20、25、30层）会触发随机事件：
1. **声望之塔（climb）**：消耗骰子攀登高塔，33.3%概率获得声望
2. **活力之泉（vitality_spring）**：消耗骰子浸泡泉水，25%概率补满活力
3. **猜拳（rps）**：与神秘人猜拳，赢了前进，输了后退

### 原有逻辑问题

#### 1. 声望之塔和活力之泉
```python
# 原有代码
if success:
    # 只有成功时才标记本层已通关
    execute_update("""
        UPDATE player_dungeon_progress 
        SET floor_cleared = TRUE, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND dungeon_name = %s
    """, (user_id, dungeon_name))
```

**问题**：失败时不设置 `floor_cleared = TRUE`，导致状态保持为 `FALSE`

#### 2. 猜拳
```python
# 原有代码
execute_update("""
    UPDATE player_dungeon_progress 
    SET current_floor = %s, floor_cleared = FALSE, floor_event_type = %s, updated_at = CURRENT_TIMESTAMP
    WHERE user_id = %s AND dungeon_name = %s
""", (new_floor, floor_event_type, user_id, dungeon_name))
```

**问题**：无论输赢都设置 `floor_cleared = FALSE`，导致玩家无法继续

#### 3. 扔骰子检查逻辑
```python
if not floor_cleared and floor_event_type in ('beast', 'boss'):
    return jsonify({"ok": False, "error": "请先击败本层幻兽才能前进"}), 400
```

**说明**：这个检查只针对 `beast` 和 `boss` 类型，所以随机事件类型不会被阻止扔骰子。但是 `floor_cleared = FALSE` 会导致前端显示混乱，玩家看到的界面状态不正确。

## 修复方案

### 核心原则
**随机事件不需要打怪，无论成功失败，都应该允许玩家继续前进**

### 修复内容

#### 1. 声望之塔（climb）
```python
# 修复后
# 无论成功失败，都标记本层已通关，允许继续前进
execute_update("""
    UPDATE player_dungeon_progress 
    SET floor_cleared = TRUE, updated_at = CURRENT_TIMESTAMP
    WHERE user_id = %s AND dungeon_name = %s
""", (user_id, dungeon_name))
```

**修改说明**：移除了 `if success:` 条件，无论攀登成功或失败，都设置 `floor_cleared = TRUE`

#### 2. 活力之泉（vitality_spring）
```python
# 修复后
# 无论成功失败，都标记本层已通关，允许继续前进
execute_update("""
    UPDATE player_dungeon_progress 
    SET floor_cleared = TRUE, updated_at = CURRENT_TIMESTAMP
    WHERE user_id = %s AND dungeon_name = %s
""", (user_id, dungeon_name))
```

**修改说明**：移除了 `if success:` 条件，无论浸泡成功或失败，都设置 `floor_cleared = TRUE`

#### 3. 猜拳（rps）
```python
# 修复后
# 猜拳后无论输赢平局，都标记本层已通关，允许继续前进
execute_update("""
    UPDATE player_dungeon_progress 
    SET current_floor = %s, floor_cleared = TRUE, floor_event_type = %s, updated_at = CURRENT_TIMESTAMP
    WHERE user_id = %s AND dungeon_name = %s
""", (new_floor, floor_event_type, user_id, dungeon_name))
```

**修改说明**：将 `floor_cleared = FALSE` 改为 `floor_cleared = TRUE`

## 修改文件
`interfaces/routes/dungeon_routes.py`

## 修复效果

### 修复前
1. 玩家扔骰子到第5层，触发声望之塔
2. 玩家尝试攀登，失败
3. `floor_cleared` 保持为 `FALSE`
4. 前端显示混乱，玩家看到的状态不正确
5. 玩家体验：感觉卡住了，不知道该怎么继续

### 修复后
1. 玩家扔骰子到第5层，触发声望之塔
2. 玩家尝试攀登，失败
3. `floor_cleared` 设置为 `TRUE`
4. 前端显示正常，玩家可以继续扔骰子
5. 玩家体验：流畅，随机事件不会阻碍前进

## 游戏逻辑说明

### 随机事件的设计意图
随机事件是地图副本的趣味性元素，不应该成为阻碍玩家前进的障碍：
- **声望之塔**：给玩家额外获得声望的机会，失败也不影响前进
- **活力之泉**：给玩家恢复活力的机会，失败也不影响前进
- **猜拳**：增加趣味性，输了会后退，但不会卡住玩家

### 与战斗事件的区别
- **战斗事件（beast/boss）**：必须击败幻兽才能继续前进
- **随机事件（climb/vitality_spring/rps）**：参与后即可继续前进，不需要"通关"
- **宝箱事件（giant_chest/mystery_chest）**：开启后即可继续前进

## 测试验证

### 测试步骤
1. 进入地图副本
2. 扔骰子到第5层（声望之塔）
3. 尝试攀登，无论成功失败
4. 再次扔骰子，验证是否可以正常前进
5. 重复测试第10、15、20、25、30层的随机事件

### 预期结果
- ✅ 声望之塔：攀登失败后可以继续扔骰子
- ✅ 活力之泉：浸泡失败后可以继续扔骰子
- ✅ 猜拳：无论输赢平局，都可以继续扔骰子
- ✅ 前端显示正常，不会出现混乱
- ✅ 不会出现"请先击败本层幻兽"的错误提示

## 注意事项

1. **不影响战斗事件**：战斗事件（beast/boss）仍然需要击败幻兽才能继续
2. **不影响猜拳逻辑**：猜拳输了仍然会后退，赢了会前进
3. **保持游戏平衡**：随机事件的成功概率不变，只是失败后不会卡住玩家
4. **宝箱事件正常**：宝箱开启后也会设置 `floor_cleared = TRUE`

---

**修复完成时间**: 2026年1月17日
**修复人**: Kiro AI Assistant
**修复状态**: ✅ 完成
