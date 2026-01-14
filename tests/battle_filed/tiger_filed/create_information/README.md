# 测试数据创建工具

## 功能

`create_31_test_players.py` 用于创建31个测试玩家和幻兽，满足古战场测试的前置条件。

## 使用方法

在项目根目录运行：

```bash
python tests/battle_filed/create_information/create_31_test_players.py
```

## 创建的数据

- **31个测试玩家**（user_id: 2000-2030）
  - 账号：`battlefield_test_1` 到 `battlefield_test_31`
  - 密码：`123456`（测试用）
  - 昵称：`测试玩家1` 到 `测试玩家31`
  - 等级：20-39级之间随机（猛虎战场范围）
  - 初始金币：10000

- **每个玩家至少1只出战幻兽**
  - 属性根据玩家等级生成
  - `is_in_team=1`（在战斗队伍中）
  - 包含必要的资质和星数数据（用于PVP先手判定）
  - 可能还有0-2只备用幻兽（不在队伍中）

## 注意事项

⚠️ **本脚本会删除 user_id 在 2000-2030 范围内的现有玩家和幻兽数据**

请勿在生产环境运行！

## 验证

运行脚本后，会自动验证：
- 所有玩家都已创建
- 所有玩家都有至少1只出战幻兽
- 所有玩家等级都在20-39范围内

## 运行测试

创建完成后，可以运行古战场测试：

```bash
python -m pytest tests/battle_filed/test_battlefield_signup.py -vv
```
