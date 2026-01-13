# 战斗系统实现说明书

本文档用于帮助 AI 快速定位战斗系统相关文件，理解战斗流程的实现架构。

---

## 核心文件总览

| 文件路径 | 职责 | 修改场景 |
|---------|------|---------|
| `domain/services/pvp_battle_engine.py` | **核心战斗引擎** - 计算伤害、先手判定、战斗流程 | 修改伤害公式、先手规则、战斗流程 |
| `domain/services/skill_system.py` | **技能系统** - 技能触发、效果计算、增益/负面应用 | 修改技能逻辑、触发概率、效果数值 |
| `configs/skills.json` | **技能配置** - 所有技能的参数定义 | 调整技能数值、添加新技能 |
| `application/services/zhenyao_service.py` | **镇妖塔服务** - 调用战斗引擎处理镇妖战斗 | 修改镇妖战斗流程 |
| `application/services/tower_service.py` | **通天塔服务** - 调用战斗引擎处理通天塔战斗 | 修改通天塔战斗流程 |
| `application/services/battlefield_service.py` | **远古战场服务** - 调用战斗引擎处理战场战斗 | 修改远古战场战斗流程 |
| `interfaces/routes/arena_routes.py` | **擂台路由** - 直接调用战斗引擎处理擂台战斗 | 修改擂台战斗流程 |

---

## 架构分层

```
┌─────────────────────────────────────────────────────────────────┐
│                    接口层 (interfaces/routes/)                   │
│  tower_routes.py / arena_routes.py / battlefield_routes.py      │
│  - 接收HTTP请求，参数校验，调用应用服务                            │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  依赖注入 (interfaces/web_api/bootstrap.py)      │
│  - 创建和管理所有服务实例                                         │
│  - 注入仓储和配置到各服务                                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                应用服务层 (application/services/)                │
│  zhenyao_service.py / tower_service.py / battlefield_service.py │
│  - 业务逻辑编排                                                   │
│  - 幻兽数据转换为 PvpBeast                                        │
│  - 调用战斗引擎                                                   │
│  - 处理战斗结果（奖励发放、状态更新等）                             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   领域服务层 (domain/services/)                  │
│  pvp_battle_engine.py + skill_system.py                         │
│  - 纯战斗逻辑计算                                                 │
│  - 不依赖数据库/Flask                                             │
│  - 可独立测试                                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 调用链示例：镇妖塔挑战

```
POST /api/zhenyao/challenge
        │
        ▼
interfaces/routes/tower_routes.py
  └─> services.zhenyao_service.challenge_floor()
        │
        ▼
application/services/zhenyao_service.py
  └─> _do_battle()
      └─> _to_pvp_beasts()      # 转换幻兽数据
      └─> run_pvp_battle()      # 调用战斗引擎
        │
        ▼
domain/services/pvp_battle_engine.py
  └─> _first_striker_is_attacker()  # 先手判定
  └─> calc_damage()                  # 伤害计算
  └─> skill_system.try_trigger_active_skill()   # 主动技能
  └─> skill_system.try_trigger_passive_skill()  # 被动技能
```

---

## 核心文件详解

### 1. `domain/services/pvp_battle_engine.py` (战斗引擎核心)

**主要数据结构：**

```python
@dataclass
class PvpBeast:
    """PVP战斗用的幻兽快照"""
    id: int
    name: str
    hp_max: int
    hp_current: int
    physical_attack: int      # 物理攻击
    magic_attack: int         # 法术攻击
    physical_defense: int     # 物理防御
    magic_defense: int        # 法术防御
    speed: int                # 速度
    attack_type: AttackType   # "physical" / "magic"
    grade: int                # 品质（神兽/精英/普通）
    skills: List[str]         # 技能列表
    # 星数、资质等用于先手判定

@dataclass
class PvpPlayer:
    """PVP战斗用的玩家快照"""
    player_id: int
    level: int
    beasts: List[PvpBeast]
    name: str

@dataclass
class PvpBattleResult:
    """战斗结果"""
    attacker_player_id: int
    defender_player_id: int
    winner_player_id: int
    loser_player_id: int
    total_turns: int
    logs: List[AttackLog]  # 战报
```

**核心函数：**

| 函数名 | 作用 | 行号 |
|-------|------|------|
| `run_pvp_battle()` | 主战斗入口，执行完整战斗流程 | ~359 |
| `calc_damage()` | 计算单次攻击伤害 | ~217 |
| `_first_striker_is_attacker()` | 先手判定（速度>品质>星数>资质>属性） | ~268 |
| `_pick_attack_and_defense()` | 根据攻击类型选择攻防数值 | ~170 |
| `_defense_multiplier()` | 防御档位倍数计算 | ~192 |
| `_build_attack_description()` | 生成战报文本 | ~568 |

**伤害公式：**

```python
# 攻 - 防 >= 0 时：
damage = (攻 - 防) * random(0.069, 0.071) * 防御档位倍数

# 攻 - 防 < 0 时（使用固定区间伤害）：
if |差值| <= 1000: damage = random(250, 300)
elif |差值| <= 2000: damage = random(250, 300) * 0.7
elif |差值| <= 3000: damage = random(250, 300) * 0.5
elif |差值| <= 4000: damage = random(250, 300) * 0.3
else: damage = random(20, 40)

# 低阶玩家（20-39级）额外 * 0.3
```

**防御档位倍数：**

| 防御值 | 倍数 |
|--------|------|
| < 1000 | 3.8 |
| < 2000 | 2.0 |
| < 3000 | 1.6 |
| < 4000 | 1.3 |
| < 5000 | 1.1 |
| >= 5000 | 1.0 |

---

### 2. `domain/services/skill_system.py` (技能系统)

**技能分类：**

| 类型 | 说明 | 触发时机 |
|------|------|---------|
| 主动技能 | 必杀/连击/破甲/毒攻等 | 攻击时，每回合最多1个 |
| 被动技能 | 闪避/反震/反击 | 被攻击时，每回合最多1个 |
| 增益技能 | 永久加成裸属性 | 战斗前应用 |
| 负面技能 | 永久减少裸属性 | 战斗前应用 |

**核心函数：**

| 函数名 | 作用 |
|-------|------|
| `try_trigger_active_skill()` | 判定主动技能触发 |
| `try_trigger_passive_skill()` | 判定被动技能触发 |
| `apply_buff_debuff_skills()` | 应用增益/负面技能到裸属性 |
| `check_poison_resist()` | 检查毒抗免疫 |
| `get_skill_info()` | 获取技能详细信息 |
| `classify_skills()` | 技能分类 |

**技能触发结果：**

```python
@dataclass
class SkillTriggerResult:
    triggered: bool              # 是否触发
    skill_name: str              # 技能名
    damage_multiplier: float     # 伤害倍数
    effects: List[SkillEffect]   # 附加效果（破甲/中毒等）
    is_critical: bool            # 是否必杀类
    lifesteal_ratio: float       # 吸血比例

@dataclass
class PassiveSkillResult:
    triggered: bool
    skill_name: str
    effect_type: str      # "dodge" / "reflect" / "counter"
    effect_value: float   # 反震/反击比例
```

---

### 3. `configs/skills.json` (技能配置)

**结构：**

```json
{
  "active_skills": {
    "advanced": { "高级必杀": {...}, "高级连击": {...} },
    "normal": { "必杀": {...}, "连击": {...} }
  },
  "passive_skills": {
    "advanced": { "高级闪避": {...}, "高级反震": {...} },
    "normal": { "闪避": {...}, "反震": {...} }
  },
  "buff_skills": {
    "advanced": { "强身": {...}, "幸运": {...} },
    "normal": { "体质": {...} }
  },
  "debuff_skills": {
    "愚蠢": {...}, "迟钝": {...}
  }
}
```

**主动技能参数：**
- `trigger_rate`: 触发概率
- `damage_multiplier`: 伤害倍数
- `attack_type`: 攻击类型限制 ("physical"/"magic"/"all")
- `effects`: 附加效果列表
- `is_critical`: 是否必杀类（受幸运技能影响）

**被动技能参数：**
- `trigger_rate`: 触发概率
- `effect_type`: 效果类型 ("dodge"/"reflect"/"counter")
- `reflect_ratio` / `counter_ratio`: 反弹比例

---

### 4. 应用服务层 (application/services/)

**共同模式：**

所有调用战斗引擎的服务都遵循相同模式：

```python
# 1. 从数据库获取幻兽数据
beasts_data = self.beast_repo.get_beasts_by_player(player_id)

# 2. 转换为 PvpBeast（应用技能增益）
def _to_pvp_beasts(raw_beasts: List) -> List[PvpBeast]:
    beasts: List[PvpBeast] = []
    for beast in raw_beasts:
        # 应用增益/负面技能
        final_hp, final_pa, final_ma, final_pd, final_md, final_spd, special_effects = \
            apply_buff_debuff_skills(
                skills=skills_list,
                attack_type=attack_type,
                raw_hp=raw_hp,
                raw_physical_attack=raw_pa,
                ...
            )
        beasts.append(PvpBeast(...))
    return beasts

# 3. 构建 PvpPlayer
attacker_player = PvpPlayer(
    player_id=...,
    level=...,
    beasts=_to_pvp_beasts(attacker_beasts),
    name=...
)

# 4. 调用战斗引擎
pvp_result = run_pvp_battle(attacker_player, defender_player, max_log_turns=50)

# 5. 处理结果（奖励发放、状态更新等）
```

---

## 常见修改场景对应文件

| 修改需求 | 需要修改的文件 |
|---------|---------------|
| 修改伤害计算公式 | `domain/services/pvp_battle_engine.py` → `calc_damage()` |
| 修改防御档位倍数 | `domain/services/pvp_battle_engine.py` → `_defense_multiplier()` |
| 修改先手判定规则 | `domain/services/pvp_battle_engine.py` → `_first_striker_is_attacker()` |
| 修改技能触发概率 | `configs/skills.json` |
| 修改技能伤害倍数 | `configs/skills.json` |
| 添加新技能 | `configs/skills.json` + 可能需要修改 `skill_system.py` |
| 修改技能触发逻辑 | `domain/services/skill_system.py` |
| 修改战报文本格式 | `domain/services/pvp_battle_engine.py` → `_build_attack_description()` |
| 修改镇妖塔战斗奖励 | `application/services/zhenyao_service.py` |
| 修改通天塔战斗流程 | `application/services/tower_service.py` |
| 修改擂台战斗流程 | `interfaces/routes/arena_routes.py` |
| 修改战场战斗流程 | `application/services/battlefield_service.py` |

---

## 战斗流程伪代码

```python
def run_pvp_battle(attacker_player, defender_player):
    logs = []
    turn = 0
    
    while 双方都还有存活幻兽:
        a_beast = 攻方当前幻兽
        d_beast = 守方当前幻兽
        
        while 两只幻兽都存活:
            # 先手判定
            attacker_first = _first_striker_is_attacker(a_beast, d_beast)
            order = 根据先手决定攻击顺序
            
            for atk_beast, def_beast in order:
                turn += 1
                
                # 1. 结算状态效果
                _tick_status_effects_before_action(atk_beast)
                
                # 2. 主动技能判定
                skill_result = try_trigger_active_skill(atk_beast.skills, ...)
                
                # 3. 被动技能判定（闪避/反震/反击）
                passive_result = try_trigger_passive_skill(def_beast.skills, ...)
                
                # 4. 计算伤害
                base_damage = calc_damage(atk_beast, def_beast, level)
                final_damage = base_damage * skill_result.damage_multiplier
                
                # 5. 处理闪避
                if passive_result.effect_type == "dodge":
                    final_damage = 0
                
                # 6. 扣血
                def_beast.hp_current -= final_damage
                
                # 7. 吸血
                if skill_result.lifesteal_ratio > 0:
                    atk_beast.hp_current += final_damage * lifesteal_ratio
                
                # 8. 反震/反击
                if passive_result.effect_type in ("reflect", "counter"):
                    reflect_damage = final_damage * passive_result.effect_value
                    atk_beast.hp_current -= reflect_damage
                
                # 9. 应用技能附加效果（破甲/中毒等）
                for effect in skill_result.effects:
                    _apply_or_refresh_effect(def_beast, effect)
                
                # 10. 生成战报
                logs.append(AttackLog(...))
        
        # 更新出战幻兽索引
        a_idx = attacker_player.first_alive_index()
        d_idx = defender_player.first_alive_index()
    
    # 判定胜负
    winner_id = 有存活幻兽的一方
    return PvpBattleResult(...)
```

---

## 关键数据类型速查

```python
# 攻击类型
AttackType = Literal["physical", "magic"]

# 状态效果类型
effect_types = [
    "poison",               # 中毒
    "physical_defense_down", # 物防降低
    "magic_defense_down",    # 法防降低
    "speed_down",            # 减速
    "physical_attack_down",  # 物攻降低
    "magic_attack_down",     # 法攻降低
]

# 被动效果类型
passive_effect_types = [
    "dodge",    # 闪避
    "reflect",  # 反震
    "counter",  # 反击
]
```

---

## 测试建议

战斗系统修改后，建议通过以下方式验证：

1. **单元测试**：直接调用 `run_pvp_battle()` 验证战斗结果
2. **接口测试**：curl 调用 `/api/zhenyao/challenge` 等接口
3. **日志检查**：查看战报 `logs` 中的伤害数值和描述

---

## 文件位置快速索引

```
game/
├── domain/services/
│   ├── pvp_battle_engine.py   ← 核心战斗引擎
│   └── skill_system.py        ← 技能系统
├── configs/
│   └── skills.json            ← 技能配置
├── application/services/
│   ├── zhenyao_service.py     ← 镇妖塔战斗
│   ├── tower_service.py       ← 通天塔战斗
│   └── battlefield_service.py ← 远古战场战斗
├── interfaces/routes/
│   ├── tower_routes.py        ← 镇妖/通天塔路由
│   └── arena_routes.py        ← 擂台路由
└── interfaces/web_api/
    └── bootstrap.py           ← 服务依赖注入
```
