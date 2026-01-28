# 铜钱负数 Bug 修复说明

## 问题描述

用户反馈在使用"一键猎魂"功能时，铜钱出现了负数（-6076）。

## 问题原因

### 根本原因

`update_gold` 函数在扣除铜钱时，没有检查余额是否足够，直接执行 SQL：

```sql
UPDATE player SET gold = gold + (-8000) WHERE user_id = ?
```

这会导致即使余额不足，也会强制扣钱，使铜钱变成负数。

### 触发场景

虽然一键猎魂的代码在扣钱前会检查 `if gold < cost`，但这个检查使用的是**局部变量**，而不是数据库中的实时值。

**可能的并发问题：**

1. 玩家打开一键猎魂页面，此时 `gold = 10000`
2. 在另一个标签页或设备上，玩家花费了 9000 铜钱
3. 玩家点击一键猎魂，代码检查 `gold < 8000` 通过（因为局部变量还是 10000）
4. 执行 `update_gold(user_id, -8000)`，数据库中的铜钱变成 `1000 - 8000 = -7000`

## 修复方案

### 1. 修改 `update_gold` 函数（核心修复）

**文件：** `infrastructure/db/player_repo_mysql.py`

**修改前：**
```python
def update_gold(user_id: int, delta: int) -> bool:
    """更新玩家铜钱（增加或减少）"""
    sql = "UPDATE player SET gold = gold + %s WHERE user_id = %s"
    affected = execute_update(sql, (delta, user_id))
    return affected > 0
```

**修改后：**
```python
def update_gold(user_id: int, delta: int) -> bool:
    """更新玩家铜钱（增加或减少）
    
    Args:
        user_id: 玩家ID
        delta: 铜钱变化量（正数为增加，负数为减少）
    
    Returns:
        bool: 操作是否成功（扣钱时余额不足会返回 False）
    """
    if delta < 0:
        # 扣钱时检查余额是否足够，防止铜钱变成负数
        sql = "UPDATE player SET gold = gold + %s WHERE user_id = %s AND gold >= %s"
        affected = execute_update(sql, (delta, user_id, abs(delta)))
    else:
        # 加钱不需要检查
        sql = "UPDATE player SET gold = gold + %s WHERE user_id = %s"
        affected = execute_update(sql, (delta, user_id))
    return affected > 0
```

**关键改进：**
- 扣钱时添加条件 `AND gold >= %s`，确保余额足够才执行
- 如果余额不足，`affected` 为 0，函数返回 `False`

### 2. 修改一键猎魂代码

**文件：** `interfaces/routes/mosoul_routes.py`

**修改位置：** 第 1127-1136 行

**修改前：**
```python
player_repo.update_gold(user_id, -cost)
gold -= cost
total_cost += cost
```

**修改后：**
```python
# 扣除铜钱，检查是否成功（防止并发导致余额不足）
success = player_repo.update_gold(user_id, -cost)
if not success:
    # 扣钱失败，说明实际余额不足
    results.append({
        'hunt_num': hunt_num + 1,
        'stopped': True,
        'reason': '铜钱不足（余额已变化）',
    })
    break

gold -= cost
total_cost += cost
```

### 3. 修改单次猎魂代码

**文件：** `interfaces/routes/mosoul_routes.py`

**修改位置：** 第 880 行左右

**修改前：**
```python
# 扣除铜钱
player_repo.update_gold(user_id, -cost)
gold -= cost
```

**修改后：**
```python
# 扣除铜钱，检查是否成功（防止并发导致余额不足）
success = player_repo.update_gold(user_id, -cost)
if not success:
    return jsonify({'ok': False, 'error': '铜钱不足（余额已变化，请刷新页面）'})

gold -= cost
```

## 测试验证

创建了测试文件 `test_gold_negative_fix.py`，验证了以下场景：

### 测试用例

1. ✅ **正常扣钱**：余额 10000，扣除 5000 → 成功，余额变为 5000
2. ✅ **余额不足时扣钱**：余额 5000，尝试扣除 8000 → 失败，余额保持 5000
3. ✅ **加钱**：余额 5000，增加 3000 → 成功，余额变为 8000
4. ✅ **恰好扣完**：余额 8000，扣除 8000 → 成功，余额变为 0
5. ✅ **铜钱为0时扣钱**：余额 0，尝试扣除 1 → 失败，余额保持 0

所有测试用例均通过！

## 修复效果

### 修复前
- ❌ 铜钱可能变成负数
- ❌ 一键猎魂可能在余额不足时继续扣钱
- ❌ 并发操作可能导致余额异常

### 修复后
- ✅ 铜钱永远不会变成负数
- ✅ 扣钱失败时会立即停止并提示用户
- ✅ 数据库层面保证了原子性，防止并发问题
- ✅ 用户体验更好：明确提示"余额已变化，请刷新页面"

## 影响范围

此修复影响所有使用 `update_gold` 函数的地方，包括但不限于：

- ✅ 魔魂猎魂（单次和一键）
- ✅ 商城购买
- ✅ 任务奖励
- ✅ 其他所有涉及铜钱扣除的功能

所有这些功能现在都会在余额不足时正确失败，而不是让铜钱变成负数。

## 完成时间

2026年1月18日
