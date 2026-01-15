# 地图副本系统 (Dungeon System)

## 功能概述

地图副本是一个类似爬塔的玩法，玩家通过掷骰子前进，在不同楼层遭遇幻兽进行战斗。

- 总共 35 层，BOSS 层为 5、10、15、20、25、30 层
- 掷骰子（1-6点）决定前进层数
- 每层遭遇幻兽需挑战，胜利后才能继续前进
- 可使用迷踪符指定前进层数

---

## 核心文件路径及功能

### 1. 路由入口

| 文件 | 功能 |
|------|------|
| `interfaces/routes/dungeon_routes.py` | 副本相关 HTTP API 路由，包含 `/progress`、`/advance`、`/floor/beasts`、`/challenge`、`/mizong/info`、`/mizong/use` |

### 2. 领域层（战斗引擎）

| 文件 | 功能 |
|------|------|
| `domain/services/pvp_battle_engine.py` | **PVP 战斗引擎**：副本战斗使用此引擎，包含 `PvpBeast`、`PvpPlayer`、`run_pvp_battle()` |
| `domain/services/skill_system.py` | **技能系统**：战斗中调用 `apply_buff_debuff_skills()` 计算技能加成 |

### 3. 基础设施层（数据持久化）

| 文件 | 功能 |
|------|------|
| `infrastructure/db/connection.py` | 数据库连接，`execute_query()`、`execute_update()`、`get_connection()` |
| `infrastructure/db/player_repo_mysql.py` | 玩家数据仓库 `MySQLPlayerRepo` |
| `infrastructure/db/player_beast_repo_mysql.py` | 玩家幻兽数据仓库：获取出战幻兽 `get_team_beasts()` |
| `infrastructure/db/bone_repo_mysql.py` | 战骨数据仓库，战斗时计算幻兽属性加成 |
| `infrastructure/db/spirit_repo_mysql.py` | 战灵数据仓库，战斗时计算幻兽属性加成 |
| `infrastructure/config/bone_system_config.py` | 战骨系统配置，`get_bone_system_config()` |

### 4. 应用层服务

| 文件 | 功能 |
|------|------|
| `application/services/inventory_service.py` | 背包服务：迷踪符物品的获取和消耗 `get_item_count()`、`remove_item()` |

### 5. 前端页面

| 文件 | 功能 |
|------|------|
| `interfaces/client/src/features/dungeon/DungeonChallengePage.vue` | 副本主页面：显示当前层、掷骰子前进、挑战幻兽 |
| `interfaces/client/src/features/dungeon/DungeonBattleResultPage.vue` | 战斗结果页面：显示战斗评价、胜负、操作选项 |
| `interfaces/client/src/features/dungeon/DungeonDetailReportPage.vue` | 详细战报页面：显示每回合战斗细节 |
| `interfaces/client/src/features/dungeon/MizongPage.vue` | 迷踪符页面：使用迷踪符指定前进层数 |

### 6. 配置文件

| 文件 | 功能 |
|------|------|
| `configs/dungeon_beasts.json` | 副本幻兽属性配置：各副本的普通怪、精英怪、BOSS 属性 |

---

## 数据库表

| 表名 | 功能 |
|------|------|
| `player_dungeon_progress` | 玩家副本进度：`user_id`、`dungeon_name`、`current_floor`、`total_floors`、`floor_cleared` |

---

## API 接口说明

| 接口 | 方法 | 功能 |
|------|------|------|
| `/api/dungeon/progress` | GET | 获取玩家副本进度 |
| `/api/dungeon/advance` | POST | 掷骰子前进 |
| `/api/dungeon/floor/beasts` | GET | 获取当前层幻兽信息 |
| `/api/dungeon/challenge` | POST | 挑战幻兽，执行战斗 |
| `/api/dungeon/mizong/info` | GET | 获取迷踪符数量 |
| `/api/dungeon/mizong/use` | POST | 使用迷踪符前进 |

---

## 修改指南

- **调整副本幻兽属性**：修改 `configs/dungeon_beasts.json`
- **调整战斗规则**：修改 `domain/services/pvp_battle_engine.py`
- **调整技能效果**：修改 `domain/services/skill_system.py`
- **修改前端界面**：修改 `interfaces/client/src/features/dungeon/` 下的 Vue 文件
- **修改 API 逻辑**：修改 `interfaces/routes/dungeon_routes.py`
