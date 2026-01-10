# 镇妖功能说明文档

## 功能概述

镇妖（Zhenyao）是一个 PVP 玩法，玩家可以占领"聚魂阵"层数，其他玩家可以挑战并抢夺占领权。

- 玩家等级 ≥ 30 级才能参与镇妖
- 根据等级段分配可镇妖的层数范围（玄阶 30-39 级对应 1-20 层，地阶 40-49 级对应 21-40 层，依此类推）
- 可镇妖层数受通天塔进度限制
- 每层分为"试炼层"（前 10 层）和"炼狱层"（后 10 层），每种每日有次数限制

---

## 核心文件路径及功能

### 1. 路由入口

| 文件 | 功能 |
|------|------|
| `interfaces/routes/tower_routes.py` | 镇妖相关的 HTTP API 路由，包含 `/zhenyao/info`、`/zhenyao/floors`、`/zhenyao/occupy`、`/zhenyao/challenge`、`/zhenyao/dynamics`、`/zhenyao/battle/<id>` |

### 2. 应用层服务（业务逻辑）

| 文件 | 功能 |
|------|------|
| `application/services/zhenyao_service.py` | **镇妖核心服务**：镇妖资格检查、层数列表、占领/挑战逻辑、战斗执行（调用 PVP 引擎）、动态记录 |
| `application/services/tower_service.py` | 闯塔服务，镇妖依赖其 `TowerBattleService` 获取通天塔进度 |

### 3. 领域层（核心规则与引擎）

| 文件 | 功能 |
|------|------|
| `domain/entities/player.py` | 定义 `Player` 实体的镇妖相关方法：`can_zhenyao()`、`get_zhenyao_range()`、`get_trial_and_hell_floors()`；定义 `ZhenyaoFloor` 层占领数据结构；`RANK_CONFIG` 等级段配置 |
| `domain/repositories/player_repo.py` | 定义 `IZhenyaoRepo` 接口（层占领数据访问） |
| `domain/services/pvp_battle_engine.py` | **PVP 战斗引擎**：镇妖挑战战斗使用此引擎，包含 `PvpBeast`、`PvpPlayer`、`run_pvp_battle()` 等，实现先手规则、伤害公式、战报生成 |
| `domain/services/skill_system.py` | **技能系统**：主动/被动/增益/负面技能的判定与效果计算，战斗中调用 `apply_buff_debuff_skills()`、`try_trigger_active_skill()`、`try_trigger_passive_skill()` |
| `domain/services/battle_engine.py` | 通用战斗引擎（用于闯塔 PVE），镇妖战斗不直接使用此引擎，但结构可参考 |

### 4. 基础设施层（数据持久化）

| 文件 | 功能 |
|------|------|
| `infrastructure/db/zhenyao_battle_repo_mysql.py` | 镇妖战斗记录仓库：`MySQLZhenyaoBattleRepo`（保存/查询战斗记录）、`MySQLZhenyaoDailyCountRepo`（每日次数统计） |
| `infrastructure/db/player_repo_mysql.py` | 玩家数据仓库 `MySQLPlayerRepo`；镇妖层占领仓库 `MySQLZhenyaoRepo`（层占领/释放/查询） |
| `infrastructure/db/player_beast_repo_mysql.py` | 玩家幻兽数据仓库 `MySQLPlayerBeastRepo`：获取出战幻兽 `get_team_beasts()` |
| `infrastructure/db/tower_state_repo_mysql.py` | 通天塔进度仓库，用于获取玩家通天塔最高层 |
| `infrastructure/db/bone_repo_mysql.py` | 战骨数据仓库，战斗时计算幻兽属性加成 |
| `infrastructure/db/spirit_repo_mysql.py` | 战灵数据仓库，战斗时计算幻兽属性加成 |

### 5. 前端页面

| 文件 | 功能 |
|------|------|
| `interfaces/client/src/features/tower/ZhenYaoPage.vue` | 镇妖主页面：层列表、占领/挑战操作、动态展示 |
| `interfaces/client/src/features/tower/ZhenYaoBattlePage.vue` | 镇妖战报详情页面 |
| `interfaces/client/src/features/tower/TowerPage.vue` | 闯塔主页，包含进入镇妖的入口链接 |

### 6. 配置文件

| 文件 | 功能 |
|------|------|
| `configs/skills.json` | 技能配置：主动/被动/增益/负面技能的触发率、伤害倍率、效果 |
| `configs/bone_config.json` | 战骨属性配置 |

### 7. 测试文件

| 文件 | 功能 |
|------|------|
| `tests/Demon_suppression/create_zhenyao_test_player.py` | 镇妖测试玩家创建脚本 |

---

## 数据流简述

```
前端 ZhenYaoPage.vue
    ↓ HTTP 请求
tower_routes.py (/zhenyao/*)
    ↓
ZhenyaoService (zhenyao_service.py)
    ├── 检查资格 → PlayerRepo, TowerStateRepo
    ├── 层列表 → ZhenyaoRepo
    ├── 占领 → ZhenyaoRepo.occupy_floor()
    └── 挑战 →
        ├── 获取双方幻兽 → PlayerBeastRepo.get_team_beasts()
        ├── 属性加成 → BoneRepo, SpiritRepo
        ├── 执行战斗 → run_pvp_battle() (pvp_battle_engine.py)
        │   └── 技能判定 → skill_system.py
        ├── 保存战报 → ZhenyaoBattleRepo
        └── 更新占领 → ZhenyaoRepo
```

---

## 关键接口说明

### ZhenyaoService 主要方法

| 方法 | 功能 |
|------|------|
| `get_zhenyao_info(user_id)` | 获取玩家镇妖资格、层数范围等信息 |
| `get_floor_list(user_id, floor_type)` | 获取试炼层/炼狱层列表及占领状态 |
| `occupy_floor(user_id, floor)` | 占领空层 |
| `challenge_floor(user_id, floor)` | 挑战已占领的层，执行 PVP 战斗 |
| `get_dynamics(user_id, dynamic_type, limit)` | 获取全服/个人动态 |
| `get_battle_log(battle_id)` | 获取战报详情 |

### Player 实体镇妖相关方法

| 方法 | 功能 |
|------|------|
| `can_zhenyao()` | 判断是否可参与镇妖（等级 ≥ 30） |
| `get_zhenyao_range()` | 获取当前等级段对应的镇妖层数范围 |
| `get_trial_and_hell_floors(tower_max_floor)` | 根据通天塔进度计算可用的试炼层和炼狱层列表 |
| `get_rank_name()` | 获取阶位名称（黄阶/玄阶/地阶/天阶/飞马/玄武/战神） |

---

## 等级段与镇妖层对应关系

| 等级段 | 阶位名称 | 镇妖层范围 |
|--------|----------|-----------|
| 1-29   | 黄阶     | 不能镇妖   |
| 30-39  | 玄阶     | 1-20 层    |
| 40-49  | 地阶     | 21-40 层   |
| 50-59  | 天阶     | 41-60 层   |
| 60-69  | 飞马     | 61-80 层   |
| 70-79  | 玄武     | 81-100 层  |
| 80-100 | 战神     | 101-120 层 |

---

## 修改指南

- **调整等级段/层数对应**：修改 `domain/entities/player.py` 中的 `RANK_CONFIG`
- **修改每日次数限制**：修改 `application/services/zhenyao_service.py` 中的 `TRIAL_DAILY_LIMIT`、`HELL_DAILY_LIMIT`
- **修改占领时长**：修改 `application/services/zhenyao_service.py` 中的 `OCCUPY_DURATION_MINUTES`
- **调整战斗规则**：修改 `domain/services/pvp_battle_engine.py`
- **调整技能效果**：修改 `configs/skills.json` 和 `domain/services/skill_system.py`
- **修改前端界面**：修改 `interfaces/client/src/features/tower/ZhenYaoPage.vue`
