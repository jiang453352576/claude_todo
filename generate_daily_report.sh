#!/bin/bash
# 生成日报记录
# 使用方法: ./generate_daily_report.sh [日期]
# 日期格式: YYYY-MM-DD，默认为今天

PYTHON_SCRIPT="scripts/generate_daily_report.py"

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "错误: 未找到Python，请确保Python已安装并添加到PATH"
        exit 1
    else
        PYTHON="python"
    fi
else
    PYTHON="python3"
fi

# 执行Python脚本
if [ $# -eq 0 ]; then
    $PYTHON "$PYTHON_SCRIPT"
else
    $PYTHON "$PYTHON_SCRIPT" "$1"
fi