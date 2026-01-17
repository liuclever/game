@echo off
chcp 65001 >nul
echo ========================================
echo   游戏数据库初始化脚本
echo ========================================
echo.

:: 配置MySQL连接信息
set MYSQL_USER=root
set /p MYSQL_PASS=请输入MySQL root密码: 

echo.
echo 开始执行SQL文件...
echo.

:: 按顺序执行所有.sql文件
for %%f in (*.sql) do (
    echo 正在执行: %%f
    mysql -u %MYSQL_USER% -p%MYSQL_PASS% < "%%f"
    if %errorlevel% neq 0 (
        echo [错误] 执行 %%f 失败！
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   数据库初始化完成！
echo ========================================
echo.
echo   数据库名: game_tower
echo   用户名: root
echo   密  码: 123456
echo.
echo   请在代码中使用以上信息连接数据库
echo ========================================
pause
