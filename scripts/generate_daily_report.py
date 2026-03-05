#!/usr/bin/env python3
"""
生成日报记录的脚本

从logs目录下的markdown文件读取已完成任务，生成简洁的日报总结，
保存到dingding_logs目录。

使用方法:
    python generate_daily_report.py [日期]

参数:
    日期: 可选，格式为YYYY-MM-DD，默认为今天

示例:
    python generate_daily_report.py
    python generate_daily_report.py 2026-03-05
"""

import sys
import os
from datetime import datetime, date
from pathlib import Path
import re

def parse_markdown_file(file_path):
    """解析markdown文件，提取已完成任务"""
    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}")
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"错误: 读取文件失败: {e}")
        return []

    completed_tasks = []

    # 查找"已完成任务"部分
    lines = content.split('\n')
    in_completed_section = False

    for line in lines:
        # 检测"已完成任务"标题
        if line.strip().startswith('## 已完成任务'):
            in_completed_section = True
            continue

        # 如果进入已完成任务部分，并且遇到下一个标题，则结束
        if in_completed_section and line.strip().startswith('##'):
            break

        # 在已完成任务部分中查找任务行
        if in_completed_section and line.strip():
            # 匹配格式: "数字. [x] 任务内容 _(添加于 时间, 完成于 时间)_"
            # 或 "数字. [x] ~~任务内容~~ _(添加于 时间, 完成于 时间)_"
            match = re.match(r'^\d+\.\s+\[x\]\s+(?:~~)?(.+?)(?:~~)?\s*_\(添加于\s+(.+?)(?:,\s*完成于\s+(.+?))?\)_', line.strip())
            if match:
                task_text = match.group(1).strip()
                added_time = match.group(2).strip()
                completed_time = match.group(3) if match.group(3) else added_time

                completed_tasks.append({
                    'text': task_text,
                    'added_time': added_time,
                    'completed_time': completed_time
                })

    return completed_tasks

def generate_summary(completed_tasks, max_items=3):
    """从已完成任务生成简洁的总结"""
    if not completed_tasks:
        return []

    # 如果任务数量超过限制，选择最重要的或最新的任务
    if len(completed_tasks) > max_items:
        # 这里简单选择前max_items个任务
        # 可以改为更复杂的逻辑，比如根据任务关键词排序
        selected_tasks = completed_tasks[:max_items]
    else:
        selected_tasks = completed_tasks

    # 生成简洁的总结条目
    summary_items = []
    for task in selected_tasks:
        # 从任务文本中提取关键信息，简化表达
        text = task['text']

        # 移除可能的技术细节或冗长描述
        # 这里可以根据需要添加更多的文本处理逻辑
        if len(text) > 50:
            text = text[:47] + "..."

        summary_items.append(text)

    return summary_items

def save_daily_report(date_str, summary_items, output_dir):
    """保存日报到dingding_logs目录"""
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)

    # 生成文件名
    output_file = output_dir / f"日报_{date_str}.txt"

    # 生成日报内容 - 使用简洁的钉钉格式
    if summary_items:
        report_content = ""
        for i, item in enumerate(summary_items, 1):
            report_content += f"{i}. {item}\n"
        # 移除最后一个换行符
        report_content = report_content.rstrip()
    else:
        report_content = "今日无已完成任务记录。"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"日报已生成: {output_file}")
        return True
    except Exception as e:
        print(f"错误: 保存日报失败: {e}")
        return False

def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        # 验证日期格式
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("错误: 日期格式无效，请使用YYYY-MM-DD格式")
            print(__doc__)
            return 1
    else:
        # 使用今天日期
        date_str = datetime.now().strftime("%Y-%m-%d")

    # 设置路径
    base_dir = Path(__file__).parent.parent
    logs_dir = base_dir / "logs"
    md_file = logs_dir / f"{date_str}.md"
    dingding_logs_dir = base_dir / "dingding_logs"

    print(f"正在处理 {date_str} 的日志文件...")
    print(f"Markdown文件: {md_file}")

    # 解析markdown文件
    completed_tasks = parse_markdown_file(md_file)

    if not completed_tasks:
        print(f"警告: {date_str} 没有找到已完成任务")

    print(f"找到 {len(completed_tasks)} 个已完成任务")

    # 生成总结
    summary_items = generate_summary(completed_tasks, max_items=3)

    # 保存日报
    if save_daily_report(date_str, summary_items, dingding_logs_dir):
        print("日报生成成功!")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())