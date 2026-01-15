# Git安全更新操作指南

## 当前状态

根据检查，你有以下本地修改：

### 已修改的文件：
- `application/services/alliance_battle_service.py` - 盟战对战服务
- `infrastructure/scheduler.py` - 定时任务调度器
- `interfaces/client/package-lock.json` - 前端依赖
- `interfaces/routes/alliance_routes.py` - 联盟路由

### 新文件：
- `scripts/run_alliance_war_battle.py` - 对战执行脚本
- `scripts/盟战对战对接说明.md` - 对接说明文档

## 安全更新方法

### 方法1：使用脚本（推荐）

**Windows:**
```bash
scripts\safe_pull_update.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/safe_pull_update.sh
./scripts/safe_pull_update.sh
```

### 方法2：手动操作（更安全）

#### 步骤1：提交本地更改（推荐）

```bash
# 添加所有更改
git add .

# 提交更改
git commit -m "添加盟战对战功能和对接说明"
```

#### 步骤2：拉取远程更新

```bash
# 拉取远程dev分支
git pull origin dev
```

#### 步骤3：如果有冲突

如果出现冲突，Git会提示哪些文件有冲突：

```bash
# 查看冲突文件
git status

# 查看冲突内容
git diff

# 手动编辑冲突文件，解决冲突后：
git add <冲突文件>
git commit -m "解决合并冲突"
```

### 方法3：使用Stash（临时保存）

如果你不想立即提交，可以使用stash：

```bash
# 1. 保存本地更改
git stash push -m "本地修改备份"

# 2. 拉取更新
git pull origin dev

# 3. 恢复本地更改
git stash pop

# 4. 如果有冲突，手动解决后提交
git add .
git commit -m "合并远程更新和本地修改"
```

## 冲突处理

### 如果出现冲突

1. **查看冲突文件**
   ```bash
   git status
   ```

2. **打开冲突文件**
   - 冲突标记：
     ```
     <<<<<<< HEAD
     你的本地代码
     =======
     远程的代码
     >>>>>>> origin/dev
     ```

3. **解决冲突**
   - 保留你的代码
   - 保留远程代码
   - 或者合并两者

4. **标记为已解决**
   ```bash
   git add <冲突文件>
   git commit -m "解决合并冲突"
   ```

## 推荐流程

### 最安全的流程：

1. **先提交本地更改**
   ```bash
   git add .
   git commit -m "添加盟战对战功能：配对、对战、占领土地"
   ```

2. **拉取远程更新**
   ```bash
   git pull origin dev
   ```

3. **如果有冲突，解决后再次提交**
   ```bash
   # 解决冲突后
   git add .
   git commit -m "合并远程更新"
   ```

4. **推送到远程（如果需要）**
   ```bash
   git push origin dev
   ```

## 注意事项

1. **备份重要文件**
   - 在操作前，可以手动复制重要文件到其他位置

2. **查看远程更改**
   ```bash
   git fetch origin
   git log HEAD..origin/dev --oneline
   ```

3. **创建备份分支**
   ```bash
   git branch backup-$(date +%Y%m%d)
   ```

4. **如果拉取失败**
   - 检查网络连接
   - 检查远程仓库地址：`git remote -v`
   - 尝试使用SSH：`git remote set-url origin git@github.com:liuclever/game.git`

## 常用命令

```bash
# 查看当前状态
git status

# 查看本地和远程的差异
git fetch origin
git log HEAD..origin/dev --oneline

# 查看本地更改
git diff

# 查看stash列表
git stash list

# 查看stash内容
git stash show -p

# 放弃本地更改（危险！）
git restore <文件>
git restore .

# 放弃所有未提交的更改（危险！）
git reset --hard HEAD
```

## 你的本地修改说明

### 核心功能文件：
- `alliance_battle_service.py` - 对战核心逻辑
- `alliance_routes.py` - API接口
- `scheduler.py` - 自动触发任务

### 新增文件：
- `run_alliance_war_battle.py` - 执行脚本
- `盟战对战对接说明.md` - 文档

这些文件包含了完整的盟战对战功能，建议在拉取前先提交，避免丢失。
