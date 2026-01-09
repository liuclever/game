# 镇妖测试工具

## 功能说明

本目录包含用于测试镇妖功能的工具脚本。

## 文件说明

### 1. `create_zhenyao_test_player.py`

创建镇妖测试玩家，包括：
- 创建一个测试玩家（user_id: 3000）
- 玩家等级：100级（战神阶，可镇妖101-120层）
- 创建两只出战幻兽（is_in_team=1）
- 为每只幻兽随机分配技能（从技能配置中随机选择）
- 设置通天塔进度为120层

**运行方式：**
```bash
python tests/Demon_suppression/create_zhenyao_test_player.py
```

### 2. `occupy_floor_101.py`

让测试玩家占领试炼层第101层。

**运行方式：**
```bash
python tests/Demon_suppression/occupy_floor_101.py
```

**前置条件：**
- 需要先运行 `create_zhenyao_test_player.py` 创建测试玩家

## 使用流程

1. **创建测试玩家和幻兽：**
   ```bash
   python tests/Demon_suppression/create_zhenyao_test_player.py
   ```

2. **让测试玩家占领第101层：**
   ```bash
   python tests/Demon_suppression/occupy_floor_101.py
   ```

3. **使用其他玩家账号登录，挑战第101层测试镇妖功能**

## 测试玩家信息

- **user_id**: 3000
- **账号**: zhenyao_test
- **密码**: 123456
- **昵称**: 镇妖测试玩家
- **等级**: 100级（战神阶）
- **通天塔进度**: 120层
- **出战幻兽**: 2只（随机技能）

## 注意事项

⚠️ **本工具会删除 user_id=3000 的现有数据**

请勿在生产环境运行！

## 技能分配说明

每只幻兽会随机分配：
- 1-3个主动技能（必杀、连击、破甲、致盲、麻痹、迷惑、虚弱、雷击、撕咬、冲撞、水攻、吸血、毒攻等）
- 0-2个被动技能（闪避、反震、反击等）
- 0-2个增益技能（强力、智慧、魔抗、防御、敏捷、体魄、幸运、偷袭、抗性增强等）

技能从 `configs/skills.json` 中随机选择，包括高级和普通版本。
