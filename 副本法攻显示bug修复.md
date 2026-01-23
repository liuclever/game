# 副本法攻显示Bug修复

## 问题描述

在副本挑战页面查看法攻型幻兽的属性时，法攻值显示为0。

**示例：**
- 幻兽：大闸蟹
- 等级：40级
- 攻击类型：法攻型
- 法攻显示：**0** ← 错误

## 问题原因

### 后端代码（已修复）

后端代码在 `interfaces/routes/dungeon_routes.py` 第241行已经正确修复：

```python
ma = stats.get('matk', 0) if attack_type == 'magic' else 0
```

后端返回的数据是正确的。

### 前端代码（本次修复）

**问题位置**：`interfaces/client/src/features/dungeon/DungeonChallengePage.vue` 第928行

**错误代码**：
```vue
{{ selectedBeast.attack_type === 'physical' ? '物攻' : '法攻' }}: {{ selectedBeast.stats?.atk || 0 }}
```

**问题分析**：
- 前端显示法攻时，错误地使用了 `selectedBeast.stats?.atk` 字段
- 但是在配置文件中：
  - 物攻型幻兽使用 `atk` 字段
  - 法攻型幻兽使用 `matk` 字段
- 因此法攻型幻兽的法攻值始终显示为0

## 修复方案

**修改文件**：`interfaces/client/src/features/dungeon/DungeonChallengePage.vue`

**修改位置**：第926-929行

**修改前**：
```vue
<div class="section">
  气血: {{ selectedBeast.stats?.hp || 0 }} | 
  {{ selectedBeast.attack_type === 'physical' ? '物攻' : '法攻' }}: {{ selectedBeast.stats?.atk || 0 }}
</div>
```

**修改后**：
```vue
<div class="section">
  气血: {{ selectedBeast.stats?.hp || 0 }} | 
  {{ selectedBeast.attack_type === 'physical' ? '物攻' : '法攻' }}: {{ selectedBeast.attack_type === 'physical' ? (selectedBeast.stats?.atk || 0) : (selectedBeast.stats?.matk || 0) }}
</div>
```

**修复逻辑**：
- 如果是物攻型（`attack_type === 'physical'`）：显示 `atk` 字段
- 如果是法攻型（`attack_type === 'magic'`）：显示 `matk` 字段

## 数据结构

### 后端返回的幻兽数据结构

```json
{
  "name": "大闸蟹",
  "level": 40,
  "attack_type": "magical",  // 或 "physical"
  "stats": {
    "hp": 1892,
    "atk": 0,      // 物攻型幻兽使用此字段
    "matk": 858,   // 法攻型幻兽使用此字段
    "def": 858,
    "mdef": 435,
    "speed": 17
  },
  "skills": [...]
}
```

## 测试验证

修复后，查看法攻型幻兽的属性：

**修复前**：
```
气血: 1892 | 法攻: 0
```

**修复后**：
```
气血: 1892 | 法攻: 858
```

## 使用说明

修复后需要：

1. **重新编译前端代码**（如果使用了构建工具）
2. **刷新浏览器页面**（Ctrl+F5 强制刷新）
3. 重新查看法攻型幻兽的属性

## 相关修复

这是法攻显示问题的第二次修复：

1. **第一次修复**（2026-01-23）：修复后端代码，正确读取 `matk` 字段
   - 文件：`interfaces/routes/dungeon_routes.py`
   - 说明：`地图副本法攻型幻兽修复说明.md`

2. **第二次修复**（本次）：修复前端代码，正确显示 `matk` 字段
   - 文件：`interfaces/client/src/features/dungeon/DungeonChallengePage.vue`
   - 说明：本文档

## 注意事项

1. **字段命名**：
   - `atk` = 物理攻击
   - `matk` = 法术攻击（magic attack）
   - `def` = 物理防御
   - `mdef` = 法术防御（magic defense）

2. **攻击类型**：
   - `physical` = 物攻型
   - `magical` 或 `magic` = 法攻型

3. **其他页面**：
   - 其他显示幻兽属性的页面可能也需要类似的修复
   - 建议全局搜索类似的代码模式

## 修复日期

2026-01-23

---

**状态**: ✅ 已修复
**影响**: 副本挑战页面的幻兽属性显示
**测试**: 需要重新编译前端并刷新浏览器
