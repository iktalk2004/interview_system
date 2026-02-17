@echo off
REM 快速启动脚本 - 禁用智能评分功能

echo ========================================
echo Interview System - Quick Start
echo ========================================
echo.

REM 检查 .env 文件是否存在
if not exist ".env" (
    echo [错误] .env 文件不存在
    echo 请先创建 .env 文件
    pause
    exit /b 1
)

REM 检查是否已经禁用了智能评分
findstr /C:"DISABLE_LLM_SCORING=True" .env >nul
if %errorlevel% == 0 (
    echo [信息] 智能评分功能已禁用
) else (
    echo [信息] 正在禁用智能评分功能...
    
    REM 添加配置到 .env 文件
    echo. >> .env
    echo # 智能评分配置 >> .env
    echo DISABLE_LLM_SCORING=True >> .env
    
    echo [成功] 智能评分功能已禁用
)

echo.
echo ========================================
echo 启动 Django 服务器...
echo ========================================
echo.

REM 启动 Django 服务器
python manage.py runserver

pause
