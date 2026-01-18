@echo off
chcp 65001 >nul
echo ========================================
echo 自动同步 new/dev 分支脚本
echo ========================================
echo.

REM 检查当前分支
echo [1/6] 检查当前分支...
git branch --show-current > temp_branch.txt
set /p CURRENT_BRANCH=<temp_branch.txt
del temp_branch.txt
echo 当前分支: %CURRENT_BRANCH%

REM 如果不在 new/dev 分支，切换到 new/dev
if not "%CURRENT_BRANCH%"=="new/dev" (
    echo.
    echo [警告] 当前不在 new/dev 分支，正在切换...
    git checkout new/dev
    if errorlevel 1 (
        echo [错误] 切换分支失败！
        pause
        exit /b 1
    )
)

echo.
echo [2/6] 拉取远程 new/dev 最新代码...
git fetch origin new/dev
if errorlevel 1 (
    echo [错误] 拉取远程代码失败！
    pause
    exit /b 1
)

echo.
echo [3/6] 合并远程代码到本地...
git pull origin new/dev --rebase
if errorlevel 1 (
    echo [错误] 合并代码失败！可能有冲突需要手动解决。
    echo 请手动解决冲突后运行: git rebase --continue
    pause
    exit /b 1
)

echo.
echo [4/6] 检查本地修改...
git status --short
git diff --quiet
if errorlevel 1 (
    echo 发现本地修改，准备提交...
) else (
    git diff --cached --quiet
    if errorlevel 1 (
        echo 发现暂存的修改，准备提交...
    ) else (
        echo 没有需要提交的修改。
        goto :push
    )
)

echo.
echo [5/6] 提交本地修改...
set /p COMMIT_MSG="请输入提交信息 (直接回车使用默认信息): "
if "%COMMIT_MSG%"=="" (
    set COMMIT_MSG=feat: 更新代码
)

git add .
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
    echo [警告] 提交失败或没有需要提交的内容
)

:push
echo.
echo [6/6] 推送到远程 new/dev...
git push origin new/dev
if errorlevel 1 (
    echo [错误] 推送失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 同步完成！
echo ========================================
pause
