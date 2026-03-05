# 日报生成脚本

从待办事项应用的日志文件生成钉钉格式的日报记录。

## 功能

- 读取 `logs/` 目录下的markdown日志文件
- 解析已完成的任务
- 生成简洁的日报总结（最多3条）
- 保存到 `dingding_logs/` 目录

## 使用方法

### 命令行方式

```bash
# 生成今天的日报
python scripts/generate_daily_report.py

# 生成指定日期的日报
python scripts/generate_daily_report.py 2026-03-05
```

### Windows批处理文件

```bash
# 生成今天的日报
generate_daily_report.bat

# 生成指定日期的日报
generate_daily_report.bat 2026-03-05
```

### Shell脚本 (Linux/macOS/Git Bash)

```bash
# 首先给脚本执行权限
chmod +x generate_daily_report.sh

# 生成今天的日报
./generate_daily_report.sh

# 生成指定日期的日报
./generate_daily_report.sh 2026-03-05
```

## 输出格式

生成的日报文件保存在 `dingding_logs/日报_YYYY-MM-DD.txt`，格式为：

```
1. 任务一描述
2. 任务二描述
3. 任务三描述
```

如果没有已完成任务，则输出：
```
今日无已完成任务记录。
```

## 要求

- Python 3.6+
- 待办事项应用生成的markdown日志文件（格式如 `logs/2026-03-05.md`）

## 示例

假设 `logs/2026-03-05.md` 包含以下已完成任务：

```markdown
## 已完成任务
1. [x] ~~完成用户登录模块开发~~ _(添加于 09:15, 完成于 11:30)_
2. [x] ~~修复首页加载速度问题~~ _(添加于 10:00, 完成于 12:45)_
3. [x] ~~与产品经理讨论需求变更~~ _(添加于 14:00, 完成于 15:30)_
```

运行 `python scripts/generate_daily_report.py 2026-03-05` 会生成 `dingding_logs/日报_2026-03-05.txt`：

```
1. 完成用户登录模块开发
2. 修复首页加载速度问题
3. 与产品经理讨论需求变更
```

## 集成到待办事项应用

这个脚本也可以集成到FastAPI后端中，作为API端点提供。但目前以独立脚本的形式提供，便于命令行使用。

## 注意事项

1. 只会提取markdown文件中"已完成任务"部分的任务
2. 默认最多提取3个任务生成日报
3. 如果任务数量超过3个，只取前3个
4. 日志文件必须符合待办事项应用生成的格式