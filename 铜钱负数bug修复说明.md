# 铜钱负数 Bug 修复说明

## 问题描述

玩家在使用"一键猎魂"功能时，如果铜钱不足以完成10次猎魂，可能会出现铜钱变成负数的情况。

## 根本原因

1. **数据库层面缺少约束**：`update_gold()` 函数直接执行 `UPDATE player SET gold = gold + delta`，没有检查更新后的金额是否为负数

2. **并发问题**：虽然代码在扣除前检查了余额，但检查使用的是内存中的变量，如果有并发请求同时扣除铜钱，可能导致实际数据库中的金额不足

3. **多处直接操作**：除了 `update_gold()` 函数，还有多处代码直接使用 SQL 更新铜钱，没有防护措施

## 修复方案

### 1. 修复 `update_gold()` 函数（核心修复）

**文件**：`infrastructure/db/player_repo_mysql.py`

**修改**：在扣除操作时，添加余额检查条件

```python
def update_gold(user_id: int, delta: int) -> bool:
    """更新玩家铜钱（增加或减少）
    
    如果是扣除操作（delta < 0），会检查余额是否足够，不足则返回 False
    """
    if delta < 0:
        # 扣除操作：确保不会变成负数
        sql = "UPDATE player SET gold = gold + %s WHERE user_id = %s AND gold >= %s"
        affected = execute_update(sql, (delta, user_id, -delta))
    else:
        # 增加操作：直接更新
        sql = "UPDATE player SET gold = gold + %s WHERE user_id = %s"
        affected = execute_update(sql, (delta, user_id))
    return affected > 0
```

### 2. 修复一键猎魂功能

**文件**：`interfaces/routes/mosoul_routes.py`

**修改**：
- 单次猎魂（第922行）：检查 `update_gold()` 返回值
- 一键猎魂（第1176行）：检查 `update_gold()` 返回值

### 3. 修复化仙池升级

**文件**：`application/services/immortalize_pool_service.py`

**修改**：检查 `update_gold()` 返回值，失败时抛出异常

### 4. 修复商城购买

**文件**：`interfaces/routes/shop_routes.py`

**修改**：使用带余额检查的 SQL 更新语句

```python
cursor.execute(
    "UPDATE player SET gold = gold - %s WHERE user_id = %s AND gold >= %s", 
    (total_price, user_id, total_price)
)
if cursor.rowcount == 0:
    error_msg = "铜钱不足"
    raise Exception(error_msg)
```

## 修复已存在的负数账号

运行修复脚本：

```bash
python fix_negative_gold.py
```

该脚本会：
1. 查询所有铜钱为负数的账号
2. 显示详细信息
3. 询问确认后将这些账号的铜钱重置为 0

## 测试建议

1. 测试一键猎魂功能，确保铜钱不足时正确停止
2. 测试商城购买，确保铜钱不足时无法购买
3. 测试化仙池升级，确保铜钱不足时无法升级
4. 检查数据库，确认没有新的负数铜钱账号

## 后续优化建议

1. 考虑在数据库层面添加 CHECK 约束：`ALTER TABLE player ADD CONSTRAINT check_gold_positive CHECK (gold >= 0)`
2. 统一所有货币操作，都使用 `update_gold()` 函数，避免直接写 SQL
3. 添加货币操作日志，便于追踪问题
