# 幻兽属性与资质计算说明书

本文档详细说明幻兽各项属性和资质的完整计算流程，供AI后续修改计算逻辑时参考。

---

## 核心文件位置

| 文件 | 职责 |
|-----|-----|
| `interfaces/routes/beast_routes.py` | 主计算函数 `_calc_beast_stats()` (第818行) |
| `configs/growth_rate_multipliers.json` | 成长率倍率配置 |

---

## 输入参数（幻兽基础数据）

从图片中的幻兽为例：
- **本体**: 圣灵蚁-地界(虫族)
- **等级**: 1级
- **成长率**: 1440 (对应5星)
- **气血资质**: 1177
- **速度资质**: 1241
- **法攻资质**: 1425
- **物防资质**: 723
- **法防资质**: 1146
- **特性**: 法系善攻
- **性格**: 傻瓜

---

## 计算流程详解

### 第一步：获取境界倍率 (realm_mult)

**代码位置**: 第827-829行

```python
realm_multipliers = {"地界": 0.8, "灵界": 0.85, "神界": 0.9, "天界": 1.0}
realm_mult = realm_multipliers.get(beast.realm, 0.8)
```

| 境界 | 倍率 |
|-----|-----|
| 地界 | 0.8 |
| 灵界 | 0.85 |
| 神界 | 0.9 |
| 天界 | 1.0 |

**示例**: 地界 → `realm_mult = 0.8`

---

### 第二步：获取成长倍率 (growth_mult)

**代码位置**: 第831-833行, 第775-794行

```python
growth_score = beast.growth_rate or 840  # 成长率评分
growth_mult = _get_growth_multiplier(growth_score)
```

**成长率配置** (configs/growth_rate_multipliers.json):

| 成长率评分 | 倍率 | 星级 |
|-----------|-----|-----|
| 840 | 0.3 | ★☆☆☆☆ |
| 860 | 0.325 | ★☆☆☆☆ |
| 940 | 0.5 | ★★☆☆☆ |
| 960 | 0.525 | ★★☆☆☆ |
| 1040 | 0.575 | ★★★☆☆ |
| 1060 | 0.6 | ★★★☆☆ |
| 1140 | 0.65 | ★★★★☆ |
| 1160 | 0.675 | ★★★★☆ |
| 1240 | 0.725 | ★★★★★ |
| 1260 | 0.75 | ★★★★★ |
| 1340 | 0.8 | ★★★★★ |
| 1360 | 0.825 | ★★★★★ |
| 1440 | 0.875 | ★★★★★ |
| 1460 | 0.9 | ★★★★★ |
| 1540 | 1.0 | ★★★★★ |

**查找规则**: 找到不超过 growth_score 的最大键对应的倍率

**示例**: 成长率1440 → `growth_mult = 0.875`

---

### 第三步：计算等级加成 (level_bonus)

**代码位置**: 第835-837行

```python
level_bonus = (beast.level - 1) * 50 * realm_mult * growth_mult
```

**公式**: `等级加成 = (等级 - 1) × 50 × 境界倍率 × 成长倍率`

**示例** (1级): `(1 - 1) × 50 × 0.8 × 0.875 = 0`

---

### 第四步：判断攻击类型

**代码位置**: 第839-847行

```python
nature = getattr(beast, 'nature', '') or ''
if attack_type is None:
    if '物系' in nature:
        attack_type = "physical"
    else:
        attack_type = "magic"
```

**规则**: 特性包含"物系"则为物理攻击，否则为法术攻击

**示例**: 特性="法系善攻" → `attack_type = "magic"`

---

### 第五步：计算气血 (HP)

**代码位置**: 第850-853行

```python
hp_base = beast.hp_aptitude * 0.102 * realm_mult
beast.hp = int(hp_base + level_bonus)
```

**公式**:
```
气血初始值 = 气血资质 × 0.102 × 境界倍率
气血 = int(气血初始值 + 等级加成)
```

**示例**:
```
hp_base = 1177 × 0.102 × 0.8 = 96.0432
hp = int(96.0432 + 0) = 96
```

---

### 第六步：计算速度 (Speed)

**代码位置**: 第855-860行, 第807-815行

**步骤6.1**: 计算1级初始速度（资质分档）

```python
def _calc_level1_speed_from_aptitude(speed_aptitude: int) -> int:
    sa = int(speed_aptitude or 0)
    return max(1, (sa + 1099) // 1100)
```

**分档规则**:
| 速度资质范围 | 1级速度 |
|-------------|--------|
| 0-1100 | 1 |
| 1101-2200 | 2 |
| 2201-3300 | 3 |
| ... | ... |

**步骤6.2**: 计算速度等级加成

```python
base_speed_lv1 = _calc_level1_speed_from_aptitude(speed_aptitude)
speed_level_bonus = (beast.level - 1) * growth_mult * realm_mult * base_speed_lv1
beast.speed = max(1, int(base_speed_lv1 + speed_level_bonus))
```

**公式**:
```
1级速度 = ceil(速度资质 / 1100)
速度等级加成 = (等级 - 1) × 成长倍率 × 境界倍率 × 1级速度
速度 = max(1, int(1级速度 + 速度等级加成))
```

**示例**:
```
base_speed_lv1 = (1241 + 1099) // 1100 = 2
speed_level_bonus = (1 - 1) × 0.875 × 0.8 × 2 = 0
speed = max(1, int(2 + 0)) = 2
```

---

### 第七步：计算防御 (物防/法防)

**代码位置**: 第862-883行

**步骤7.1**: 判断是否高速系

```python
is_high_speed = nature in ("物系高速", "法系高速")
```

**步骤7.2**: 计算防御等级加成

```python
def_level_bonus = (beast.level - 1) * growth_mult * realm_mult * 22
```

**步骤7.3**: 计算1级防御初始值

```python
phys_def_lv1 = (beast.physical_defense_aptitude or 0) * 0.046 * realm_mult * growth_mult
magic_def_lv1 = (beast.magic_defense_aptitude or 0) * 0.046 * realm_mult * growth_mult
```

**步骤7.4**: 计算防御惩罚系数（非高速系）

```python
phys_mult = 1.0
magic_mult = 1.0
if not is_high_speed:
    phys_apt = int(beast.physical_defense_aptitude or 0)
    magic_apt = int(beast.magic_defense_aptitude or 0)
    if phys_apt < magic_apt:
        phys_mult = 0.85  # 物防资质较低，物防打85折
    elif magic_apt < phys_apt:
        magic_mult = 0.85  # 法防资质较低，法防打85折
```

**步骤7.5**: 计算最终防御

```python
beast.physical_defense = max(10, int((phys_def_lv1 + def_level_bonus) * phys_mult))
beast.magic_defense = max(10, int((magic_def_lv1 + def_level_bonus) * magic_mult))
```

**公式**:
```
防御等级加成 = (等级 - 1) × 成长倍率 × 境界倍率 × 22
防御初始值 = 防御资质 × 0.046 × 境界倍率 × 成长倍率
防御 = max(10, int((防御初始值 + 防御等级加成) × 惩罚系数))
```

**示例**:
```
def_level_bonus = (1 - 1) × 0.875 × 0.8 × 22 = 0

phys_def_lv1 = 723 × 0.046 × 0.8 × 0.875 = 23.2806
magic_def_lv1 = 1146 × 0.046 × 0.8 × 0.875 = 36.8844

物防资质(723) < 法防资质(1146)，所以 phys_mult = 0.85

physical_defense = max(10, int((23.2806 + 0) × 0.85)) = max(10, 19) = 19
magic_defense = max(10, int((36.8844 + 0) × 1.0)) = max(10, 36) = 36
```

---

### 第八步：计算攻击 (物攻/法攻)

**代码位置**: 第885-906行

**步骤8.1**: 判断是否善攻

```python
is_good_attack = str(nature).endswith('善攻')
```

**步骤8.2**: 计算1级攻击初始值

```python
base_attack_lv1 = max(10, int(beast.magic_attack_aptitude * 0.051 * realm_mult * growth_mult))
```

**步骤8.3**: 计算攻击值

```python
if is_good_attack:
    # 善攻特性：攻击 = 1级初始值 × 1.5 + 等级加成
    atk_level_bonus = (beast.level - 1) * growth_mult * realm_mult * 1.5 * 35
    atk_value = max(10, int(base_attack_lv1 * 1.5 + atk_level_bonus))
else:
    # 非善攻：攻击 = 资质 × 0.051 × 境界倍率 × 成长倍率 + 等级加成
    atk_value = max(10, int(beast.magic_attack_aptitude * 0.051 * realm_mult * growth_mult + level_bonus))
```

**步骤8.4**: 根据攻击类型分配

```python
if attack_type == "physical":
    beast.physical_attack = atk_value
    beast.magic_attack = 0
else:
    beast.magic_attack = atk_value
    beast.physical_attack = 0
```

**公式（善攻）**:
```
1级攻击初始值 = max(10, int(攻击资质 × 0.051 × 境界倍率 × 成长倍率))
攻击等级加成 = (等级 - 1) × 成长倍率 × 境界倍率 × 1.5 × 35
攻击 = max(10, int(1级攻击初始值 × 1.5 + 攻击等级加成))
```

**公式（非善攻）**:
```
攻击 = max(10, int(攻击资质 × 0.051 × 境界倍率 × 成长倍率 + 等级加成))
```

**示例（法系善攻）**:
```
base_attack_lv1 = max(10, int(1425 × 0.051 × 0.8 × 0.875)) = max(10, int(50.8725)) = 50
atk_level_bonus = (1 - 1) × 0.875 × 0.8 × 1.5 × 35 = 0
atk_value = max(10, int(50 × 1.5 + 0)) = max(10, 75) = 75

attack_type = "magic"
magic_attack = 75
physical_attack = 0
```

---

### 第九步：计算综合战力 (combat_power)

**代码位置**: 第908-917行

```python
beast.combat_power = (
    round(beast.hp / 9.0906) +
    round(beast.physical_attack / 8.0165) +
    round(beast.magic_attack / 8.0165) +
    round(beast.physical_defense / 4.7368) +
    round(beast.magic_defense / 4.7368) +
    round(beast.speed / 1)
)
```

**公式**:
```
战力 = round(气血 / 9.0906) 
     + round(物攻 / 8.0165) 
     + round(法攻 / 8.0165) 
     + round(物防 / 4.7368) 
     + round(法防 / 4.7368) 
     + round(速度 / 1)
```

**换算比例**:
| 属性 | 1点战力 = |
|-----|----------|
| 气血 | 9.0906点 |
| 攻击 | 8.0165点 |
| 防御 | 4.7368点 |
| 速度 | 1点 |

**示例**:
```
combat_power = round(96 / 9.0906) + round(0 / 8.0165) + round(75 / 8.0165) 
             + round(19 / 4.7368) + round(36 / 4.7368) + round(2 / 1)
             = 11 + 0 + 9 + 4 + 8 + 2 = 34
```

---

## 完整计算验证（圣灵蚁-地界 1级）

**输入**:
- 等级: 1
- 境界: 地界
- 成长率: 1440
- 特性: 法系善攻
- 气血资质: 1177
- 速度资质: 1241
- 法攻资质: 1425
- 物防资质: 723
- 法防资质: 1146

**计算**:
```
realm_mult = 0.8
growth_mult = 0.875
level_bonus = 0

气血 = int(1177 × 0.102 × 0.8 + 0) = 96
法攻 = int(max(10, int(1425 × 0.051 × 0.8 × 0.875)) × 1.5 + 0) = 75
物防 = max(10, int(723 × 0.046 × 0.8 × 0.875 × 0.85)) = 19
法防 = max(10, int(1146 × 0.046 × 0.8 × 0.875 × 1.0)) = 36
速度 = max(1, int(2 + 0)) = 2
战力 = 11 + 0 + 9 + 4 + 8 + 2 = 34
```

**输出**（与图片对比）:
| 属性 | 计算值 | 图片显示 | 匹配 |
|-----|-------|---------|-----|
| 气血 | 96 | 96 | ✓ |
| 法攻 | 75 | 75 | ✓ |
| 物防 | 19 | 19 | ✓ |
| 法防 | 36 | 36 | ✓ |
| 速度 | 2 | 2 | ✓ |
| 战力 | 34 | 34 | ✓ |

---

## 修改指南

### 如果要修改属性计算公式

1. 定位 `interfaces/routes/beast_routes.py` 第818-919行的 `_calc_beast_stats()` 函数
2. 找到对应属性的计算代码段
3. 修改公式中的系数或计算逻辑

### 如果要修改境界倍率

修改第827-828行的 `realm_multipliers` 字典

### 如果要修改成长率倍率

修改配置文件 `configs/growth_rate_multipliers.json`

### 如果要修改速度分档规则

修改第807-815行的 `_calc_level1_speed_from_aptitude()` 函数

### 如果要修改战力换算比例

修改第908-917行的战力计算公式中的系数（9.0906, 8.0165, 4.7368, 1）

---

## 资质星级对照（用于前端显示）

资质范围参考（需根据实际配置调整）:
| 资质范围 | 星级显示 |
|---------|---------|
| 0-400 | ★☆☆☆☆ |
| 401-700 | ★★☆☆☆ |
| 701-1000 | ★★★☆☆ |
| 1001-1300 | ★★★★☆ |
| 1301+ | ★★★★★ |
