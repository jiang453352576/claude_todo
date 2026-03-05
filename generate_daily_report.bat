@echo off
REM 生成日报记录
REM 使用方法: generate_daily_report.bat [日期]
REM 日期格式: YYYY-MM-DD，默认为今天

setlocal

REM 设置Python路径和脚本路径
set PYTHON_SCRIPT=scripts\generate_daily_report.py

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 执行Python脚本
if "%~1"=="" (
    python "%PYTHON_SCRIPT%"
) else (
    python "%PYTHON_SCRIPT%" %1
)

endlocal