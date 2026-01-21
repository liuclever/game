@echo off
echo ========================================
echo 重启Flask服务
echo ========================================
echo.

echo [步骤1] 清除Python缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%f in (*.pyc) do @if exist "%%f" del /f /q "%%f"
echo 缓存已清除
echo.

echo [步骤2] 启动Flask服务...
echo 请确保之前的Flask服务已完全停止（Ctrl+C）
echo.
python -m interfaces.web_api.app

pause
