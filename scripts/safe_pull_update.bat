@echo off
REM 安全拉取Git更新脚本
REM 确保本地修改不会被删除

echo ========================================
echo 安全拉取Git更新
echo ========================================
echo.

REM 1. 检查当前状态
echo [步骤1] 检查当前Git状态...
git status
echo.

REM 2. 保存本地更改（使用stash）
echo [步骤2] 保存本地未提交的更改...
git stash push -m "本地修改备份 - %date% %time%"
if %errorlevel% neq 0 (
    echo 警告: stash可能失败，请检查是否有未跟踪的文件
)

REM 3. 显示stash列表
echo.
echo [步骤3] 查看保存的更改列表...
git stash list
echo.

REM 4. 拉取远程更新
echo [步骤4] 拉取远程dev分支更新...
git pull origin dev
if %errorlevel% neq 0 (
    echo.
    echo 错误: 拉取失败，请检查网络连接或手动解决冲突
    echo 使用以下命令恢复本地更改:
    echo   git stash pop
    pause
    exit /b 1
)

REM 5. 恢复本地更改
echo.
echo [步骤5] 恢复本地更改...
git stash pop
if %errorlevel% neq 0 (
    echo.
    echo 警告: 恢复更改时可能有冲突，请手动解决
    echo 使用以下命令查看冲突:
    echo   git status
    echo   git diff
) else (
    echo.
    echo 成功: 本地更改已恢复
)

REM 6. 显示最终状态
echo.
echo [步骤6] 最终状态检查...
git status
echo.

echo ========================================
echo 操作完成！
echo ========================================
echo.
echo 如果有冲突，请手动解决后:
echo   1. 编辑冲突文件
echo   2. git add <冲突文件>
echo   3. git commit -m "解决合并冲突"
echo.
pause
