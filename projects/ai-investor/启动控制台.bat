@echo off
chcp 65001 >nul
title AI Investment Agent Console
cd /d %~dp0

:restart
echo ============================================================
echo         AI Investment Agent Console
echo ============================================================
echo.
echo [%date% %time%] Starting server...
echo.

REM 设置环境变量
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM 启动服务器
python web_console.py

echo.
echo [%date% %time%] Server stopped unexpectedly!
echo Restarting in 3 seconds...
timeout /t 3 /nobreak >nul
echo.
goto restart
