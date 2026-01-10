# 战斗系统实现说明文档

本文档旨在抽象并记录项目中 **PVP 战斗功能** 的核心实现细节，方便 AI 后续在开发相关功能时快速定位文件和理解规则。

## 1. 核心文件路径

### 1.1 战斗引擎与规则 (Domain Layer)
| 文件路径 | 说明 |
|----------|------|
| `domain/services/pvp_battle_engine.py` | **核心 PVP 引擎**：实现 1v1 顺位对战、先手规则、伤害公式、单次攻击日志 (`AttackLog`) 生成。 |
| `domain/services/skill_system.py` | **技能触发系统**：实现技能触发概率判定、主动/被动技能效果、Buff/Debuff 属性加成计算。 |
| `configs/skills.json` | **技能配置**：包含所有技能的基础触发概率、伤害倍率、持续时间、效果数值等。 |

### 1.2 业务逻辑与集成 (Application Layer)
| 文件路径 | 说明 |
|----------|------|
| `application/services/zhenyao_service.py` | **镇妖集成**：负责获取双方幻兽快照，调用战斗引擎，并将引擎生成的 `PvpBattleResult` 转换为前端所需的战报格式。 |
| `interfaces/routes/arena_routes.py` | **擂台集成**：包含擂台挑战逻辑，手动实现了将 `PvpBattleResult` 转换为战报 JSON 的逻辑 (`_build_arena_battle_data`)。 |

### 1.3 数据持久化 (Infrastructure Layer)
| 文件路径 | 说明 |
|----------|------|
| `infrastructure/db/zhenyao_battle_repo_mysql.py` | 存储镇妖模式的战斗日志 JSON。 |
| `infrastructure/db/arena_battle_repo_mysql.py` | 存储擂台模式的战斗日志 JSON。 |

### 1.4 前端展示 (Interface Layer)
| 文件路径 | 说明 |
|----------|------|
| `interfaces/client/src/features/tower/ZhenYaoBattlePage.vue` | 镇妖战报播放页面。 |
| `interfaces/client/src/features/pvp/PvpBattleReportPage.vue` | 通用 PVP 战报播放页面。 |

---

## 2. 核心规则摘要

### 2.1 先手判定规则
优先级由高到低：
1. **速度值**：考虑 Buff 后的有效速度。
2. **品质 (Grade)**：神兽 > 精英 > 普通。
3. **星数总和**：气血、主攻、双防、速度的星数之和。
4. **资质总和**：上述五项资质之和。
5. **属性总和**：最终数值之和。
6. **随机**：若完全一致则 50% 概率。

### 2.2 伤害计算公式
- **破防情况 (攻 > 防)**：`伤害 = (攻 - 防) * 随机(0.069~0.071) * 防御档位倍数`
- **未破防情况 (攻 < 防)**：基于攻防差绝对值，落入固定区间 `[250~300]` 或 `[20~40]` 并乘以衰减系数。
- **保护机制**：攻击者等级在 20-39 级时，未破防伤害额外 `*0.3`。
- **保底伤害**：至少为 1。

### 2.3 技能触发规则
- **攻击时**：从幻兽技能库中随机打乱，逐一判定触发概率，最多触发 **一个** 主动技能。
- **受击时**：判定闪避、反震、反击，最多触发 **一个** 被动技能。
- **克制关系**：
    - `偷袭` 免疫 `反震/反击`。
    - `幸运` 大幅降低对手 `必杀` 触发率。
    - `抗性增强` 有概率免疫 `中毒`。

---

## 3. 战报生成过程 (Battle Report Generation)

战报的生成分为两个阶段：

1. **引擎日志生成 (`domain/services/pvp_battle_engine.py`)**
   - `run_pvp_battle` 函数在模拟对战时，会生成 `List[AttackLog]`。
   - 每个 `AttackLog` 包含 `description` 字段，这是一句完整的中文描述（例如：“『玩家A』的幻兽使用必杀攻击『玩家B』的幻兽，气血-500”）。

2. **前端格式转换 (`Application/Route Layer`)**
   - 为了适配前端的“战斗序列”展示（如 1号幻兽 vs 1号幻兽，2号 vs 1号 等），业务层会将连续的 `AttackLog` 按照幻兽对阵关系切分为多个 `battles` 段落。
   - **擂台转换逻辑**：见 `interfaces/routes/arena_routes.py` 中的 `_build_arena_battle_data`。
   - **镇妖转换逻辑**：见 `application/services/zhenyao_service.py` 中的 `_format_battle_result`。

---

## 4. 后续开发建议

- **新增技能**：在 `configs/skills.json` 添加配置，并在 `domain/services/skill_system.py` 的 `try_trigger_active_skill` 或 `try_trigger_passive_skill` 中实现对应的效果逻辑。
- **调整平衡性**：优先修改 `domain/services/pvp_battle_engine.py` 中的 `_defense_multiplier`（防御档位倍数）或 `calc_damage` 中的随机系数。
- **新增战斗模式**：获取双方幻兽列表后，直接调用 `run_pvp_battle` 即可获得标准战报。
