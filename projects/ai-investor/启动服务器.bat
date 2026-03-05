@echo off
chcp 65001 >nul
cd /d %~dp0
echo ============================================================
echo         AI Investment Agent Console
echo ============================================================
echo.
echo Starting Flask server...
echo.

REM 设置 UTF-8 编码
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM 启动服务器（前台运行，可以看到错误）
python web_console.py

echo.
echo Server stopped.
pause
