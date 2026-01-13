# 幻兽属性计算重构指南

## 目标文件
`interfaces/routes/beast_routes.py`

## 当前问题
1. **重复代码**：`_calc_beast_stats()` 和 `obtain_beast()` 中属性计算逻辑重复
2. **违反DDD分层**：计算逻辑应在 domain 层，不应在 interface 层
3. **函数过长**：`obtain_beast()` 约200行，`get_beast_detail()` 约170行

## 重构步骤

### 第一步：创建领域规则文件
**位置**：`domain/rules/beast_stats_rules.py`

提取以下纯函数：
- `calc_realm_multiplier(realm: str) -> float` - 境界倍率
- `calc_growth_multiplier(growth_score: int) -> float` - 成长倍率（从配置读取）
- `calc_level1_speed(speed_aptitude: int) -> int` - 1级速度
- `calc_hp(hp_aptitude, level, realm_mult, growth_mult) -> int`
- `calc_speed(speed_aptitude, level, realm_mult, growth_mult) -> int`
- `calc_defense(def_aptitude, level, realm_mult, growth_mult, is_high_speed, is_lower) -> int`
- `calc_attack(atk_aptitude, level, realm_mult, growth_mult, is_good_attack) -> int`
- `calc_combat_power(hp, phys_atk, magic_atk, phys_def, magic_def, speed) -> int`

### 第二步：创建领域服务
**位置**：`domain/services/beast_stats_service.py`

封装完整计算流程：
```python
class BeastStatsCalculator:
    def calculate_stats(self, beast_data: dict) -> dict:
        """计算幻兽完整属性"""
        pass
    
    def calculate_stats_for_new_beast(self, template, realm, level, aptitudes) -> dict:
        """为新幻兽计算初始属性"""
        pass
```

### 第三步：修改路由文件
1. 删除 `_calc_beast_stats()` 函数
2. 删除 `_get_growth_multiplier()` 等辅助函数
3. 从 domain service 导入计算器
4. 在 `get_beast_list()`、`get_battle_team()`、`get_beast_detail()`、`obtain_beast()` 中调用 domain service

### 第四步：测试验证
运行现有测试确保属性计算结果不变：
```bash
python -m pytest tests/ -v -k beast
```

## 涉及的属性计算公式

### 气血
```
hp_base = hp_aptitude * 0.102 * realm_mult
hp = hp_base + level_bonus
level_bonus = (level - 1) * 50 * realm_mult * growth_mult
```

### 速度
```
base_speed_lv1 = ceil(speed_aptitude / 1100)  # 分档：0-1100=>1, 1101-2200=>2...
speed_level_bonus = (level - 1) * growth_mult * realm_mult * base_speed_lv1
speed = base_speed_lv1 + speed_level_bonus
```

### 防御
```
def_lv1 = def_aptitude * 0.046 * realm_mult * growth_mult
def_level_bonus = (level - 1) * growth_mult * realm_mult * 22
defense = (def_lv1 + def_level_bonus) * mult  # mult=0.85 如果是较低防御
```

### 攻击（善攻）
```
base_attack_lv1 = atk_aptitude * 0.051 * realm_mult * growth_mult
atk_level_bonus = (level - 1) * growth_mult * realm_mult * 1.5 * 35
attack = base_attack_lv1 * 1.5 + atk_level_bonus
```

### 战力
```
combat_power = (
    hp / 9.0906 +
    physical_attack / 8.0165 +
    magic_attack / 8.0165 +
    physical_defense / 4.7368 +
    magic_defense / 4.7368 +
    speed / 1
)
```

## 境界倍率
| 境界 | 倍率 |
|-----|-----|
| 地界 | 0.8 |
| 灵界 | 0.85 |
| 神界 | 0.9 |
| 天界 | 1.0 |

## 相关配置文件
- `configs/growth_rate_multipliers.json` - 成长率倍率映射
- `configs/beast_templates.json` - 幻兽模板
- `configs/beast_level_up_exp.json` - 升级经验

## 重构后的文件结构
```
domain/
  rules/
    beast_stats_rules.py    # 新建：纯计算函数
  services/
    beast_stats_service.py  # 新建：计算流程封装
interfaces/
  routes/
    beast_routes.py         # 精简：只做HTTP处理
```
