# 游戏对战/对局功能代码汇总

本文档汇总了游戏中所有对战/对局相关的功能代码位置和说明。

## 核心战斗引擎

### 1. PVP战斗引擎
**文件**: `domain/services/pvp_battle_engine.py`
- **主要函数**: `run_pvp_battle(attacker_player, defender_player, max_log_turns=50)`
- **功能**: 执行玩家vs玩家的幻兽战斗
- **特点**: 
  - 支持多只幻兽依次上场
  - 先手规则：速度 > 品质 > 星数总和 > 资质总和 > 属性总和
  - 支持技能系统（主动技能、被动技能）
  - 生成详细战报（最多50条攻击记录）

### 2. 统一战斗引擎
**文件**: `domain/services/battle_engine.py`
- **主要类**: `BattleEngine`
- **主要方法**: `fight(attacker_beasts, defender_beasts, attacker_name, defender_name)`
- **功能**: 通用的战斗引擎，支持自定义伤害计算器

---

## 对战功能列表

### 1. 擂台挑战 ⚔️
**路由文件**: `interfaces/routes/arena_routes.py`
- **API端点**: `POST /api/arena/challenge`
- **函数**: `challenge_arena()`
- **功能**: 挑战擂台擂主
- **特点**:
  - 支持普通场和黄金场
  - 消耗对应场次的球（道具）
  - 有VIP等级限制挑战次数
  - 连胜10场可领取奖池并下台
  - 保存战斗记录到 `arena_battle_log` 表
- **相关代码位置**: 第378-578行

### 2. 玩家切磋 🤝
**路由文件**: `interfaces/routes/player_routes.py`
- **API端点**: `POST /api/player/spar`
- **函数**: `spar_battle()`
- **功能**: 与其他玩家进行友谊赛
- **特点**:
  - 不消耗资源
  - 不保存战斗记录（仅返回战报）
  - 用于测试和友好对战
- **相关代码位置**: 第502-560行

### 3. 镇妖挑战 🏰
**路由文件**: `interfaces/routes/tower_routes.py`
- **API端点**: `POST /api/tower/zhenyao/challenge`
- **函数**: `challenge_zhenyao_floor()`
- **功能**: 挑战镇妖塔的某一层
- **特点**:
  - 挑战其他玩家占领的层数
  - 有等级限制（不同阶位可挑战不同层数范围）
  - 保存战斗记录到 `zhenyao_battle_log` 表
- **相关代码位置**: 第429-460行

### 4. 闯塔挑战 🗼
**路由文件**: `interfaces/routes/tower_routes.py`
- **API端点**: `POST /api/tower/challenge`
- **函数**: `tower_challenge()`
- **功能**: 挑战闯塔的某一层
- **特点**:
  - 挑战NPC守护的层数
  - 支持自动闯塔
  - 保存战斗记录
- **相关代码位置**: 第84-145行

### 5. 召唤之王挑战 👑
**路由文件**: `interfaces/routes/king_routes.py`
- **API端点**: `POST /api/king/challenge`
- **函数**: `king_challenge()`
- **功能**: 挑战召唤之王
- **特点**:
  - 挑战当前召唤之王
  - 胜利后成为新的召唤之王
  - 召唤之王有世界聊天置顶特权
- **相关代码位置**: 第141行开始

### 6. 副本挑战 🎮
**路由文件**: `interfaces/routes/dungeon_routes.py`
- **API端点**: `POST /api/dungeon/challenge_beasts`
- **函数**: `challenge_beasts()`
- **功能**: 挑战副本中的幻兽
- **特点**:
  - 挑战副本中的NPC幻兽
  - 有等级限制
  - 消耗活力
- **相关代码位置**: 第951行开始

### 7. 古战场对战 🏟️
**路由文件**: `interfaces/routes/battlefield_routes.py`
- **API端点**: `POST /api/battlefield/run_tournament` (管理员)
- **函数**: `run_battlefield_tournament()`
- **功能**: 运行古战场锦标赛
- **特点**:
  - 支持猛虎战场和飞鹤战场
  - 自动匹配对战
  - 保存战斗记录到 `battlefield_battle_log` 表
- **相关代码位置**: 第276行开始

### 8. 联盟对战 ⚡
**路由文件**: `interfaces/routes/alliance_routes.py`
- **API端点**: `GET /api/alliance/battle/overview`、`GET /api/alliance/war/round-duels`
- **函数**: `get_battle_overview()`、`get_round_duels()`
- **功能**: 联盟之间的对战
- **特点**:
  - 联盟领地争夺战
  - 多轮对战
  - 保存对战记录到 `alliance_land_battle_duel` 表
- **相关代码位置**: 第482-493行

---

## 战斗记录查询

### 1. 擂台战报
- **API**: `GET /api/arena/battle/<battle_id>`
- **函数**: `get_arena_battle_detail()`
- **文件**: `interfaces/routes/arena_routes.py` 第581行

### 2. 镇妖战报
- **API**: `GET /api/tower/zhenyao/battle/<battle_id>`
- **函数**: `get_zhenyao_battle()`
- **文件**: `interfaces/routes/tower_routes.py` 第460行

### 3. 古战场战报
- **API**: `GET /api/battlefield/battle/<battle_id>`
- **函数**: `get_battlefield_battle_detail()`
- **文件**: `interfaces/routes/battlefield_routes.py` 第258行

---

## 战斗数据结构

所有战斗都使用统一的 `PvpBattleResult` 结构：
```python
@dataclass
class PvpBattleResult:
    attacker_player_id: int
    defender_player_id: int
    winner_player_id: int
    loser_player_id: int
    total_turns: int
    logs: List[AttackLog]  # 战斗日志
```

战报数据格式：
```json
{
    "is_victory": bool,
    "attacker_wins": 0/1,
    "defender_wins": 0/1,
    "battles": [
        {
            "battle_num": 1,
            "rounds": [
                {
                    "round": 1,
                    "action": "战斗动作描述",
                    "a_hp": 1000,
                    "d_hp": 800
                }
            ],
            "result": "战斗结果描述"
        }
    ]
}
```

---

## 数据库表

1. **arena_battle_log** - 擂台战斗记录
2. **zhenyao_battle_log** - 镇妖战斗记录
3. **battlefield_battle_log** - 古战场战斗记录
4. **alliance_land_battle_duel** - 联盟对战记录

---

## 前端页面

1. **擂台战报**: `interfaces/client/src/features/arena/ArenaBattlePage.vue`
2. **镇妖战报**: `interfaces/client/src/features/tower/ZhenYaoBattlePage.vue`
3. **古战场战报**: `interfaces/client/src/features/battlefield/BattlefieldBattlePage.vue`
4. **切磋战报**: `interfaces/client/src/features/player/SparBattleReportPage.vue`
5. **副本战报**: `interfaces/client/src/features/dungeon/DungeonDetailReportPage.vue`

---

## 总结

游戏中共有 **8种对战类型**：
1. ✅ 擂台挑战（最常用）
2. ✅ 玩家切磋
3. ✅ 镇妖挑战
4. ✅ 闯塔挑战
5. ✅ 召唤之王挑战
6. ✅ 副本挑战
7. ✅ 古战场对战
8. ✅ 联盟对战

所有对战功能都使用统一的 `run_pvp_battle()` 引擎，确保战斗规则一致。
