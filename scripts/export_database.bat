@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 数据库配置
set DB_HOST=localhost
set DB_PORT=3306
set DB_USER=root
set DB_PASSWORD=1234
set DB_NAME=game_tower
set DB_CHARSET=utf8mb4

REM 获取脚本所在目录的父目录（项目根目录）
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

REM 生成输出文件名（带时间戳）
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set OUTPUT_FILE=%PROJECT_ROOT%\game_tower_%TIMESTAMP%.sql

echo 正在导出数据库 %DB_NAME% 到 %OUTPUT_FILE%...
echo 数据库配置: %DB_HOST%:%DB_PORT%

REM 执行 mysqldump 导出
REM 参数说明:
REM --default-character-set=utf8mb4: 指定字符集为utf8mb4
REM --single-transaction: 使用单事务模式，确保数据一致性
REM --routines: 导出存储过程和函数
REM --triggers: 导出触发器
REM --events: 导出事件
REM --add-drop-table: 添加DROP TABLE语句
REM --add-locks: 添加锁表语句
REM --complete-insert: 使用完整的INSERT语句，包含列名
REM --skip-extended-insert: 使用多行INSERT语句

mysqldump ^
  -h %DB_HOST% ^
  -P %DB_PORT% ^
  -u %DB_USER% ^
  -p%DB_PASSWORD% ^
  --default-character-set=%DB_CHARSET% ^
  --single-transaction ^
  --routines ^
  --triggers ^
  --events ^
  --add-drop-table ^
  --add-locks ^
  --complete-insert ^
  --skip-extended-insert ^
  %DB_NAME% > "%OUTPUT_FILE%" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo 导出成功！
    echo 文件路径: %OUTPUT_FILE%
    for %%A in ("%OUTPUT_FILE%") do set SIZE=%%~zA
    set /a SIZE_MB=!SIZE!/1024/1024
    echo 文件大小: !SIZE_MB! MB
) else (
    echo 导出失败！请检查错误信息。
    echo.
    echo 如果提示"mysqldump 不是内部或外部命令"，请确保:
    echo 1. MySQL客户端工具已安装
    echo 2. MySQL的bin目录已添加到系统PATH环境变量
    echo.
    echo 或者，您可以手动执行以下命令:
    echo mysqldump -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p%DB_PASSWORD% --default-character-set=%DB_CHARSET% --single-transaction %DB_NAME% ^> "%OUTPUT_FILE%"
    exit /b 1
)

endlocal
