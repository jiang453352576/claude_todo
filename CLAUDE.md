# CLAUDE.md

本文档为 Claude Code (claude.ai/code) 在本代码库中工作提供指导。

## 项目结构

此仓库包含两个独立的待办事项列表应用程序：

1. **简单HTML待办应用** (`index.html`)
   - 单个HTML文件包含所有HTML、CSS和JavaScript代码
   - 无需构建步骤 - 直接在浏览器中打开即可
   - 使用浏览器localStorage进行数据持久化
   - 响应式设计，具有现代化UI

## 开发命令

### 简单HTML应用

无需构建命令。只需在任何现代浏览器中打开 `index.html`：

```bash
# 在Windows上：
start index.html

# 在macOS上：
open index.html

# 在Linux上：
xdg-open index.html
```

## 架构说明

### 简单HTML应用
- **结构**：一体化HTML文件，包含嵌入式CSS和JavaScript
- **数据持久化**：使用 `localStorage`，键为 `dailyTasks`
- **功能**：添加、完成、编辑、删除任务，带统计跟踪
- **UI**：响应式设计，使用CSS Grid/Flexbox，渐变背景

## 处理每个项目

### 修改HTML应用时：
- 直接编辑 `index.html`
- 所有代码都在一个文件中：CSS在 `<style>` 中，JavaScript在 `<script>` 中
- 数据结构：`{id: number, text: string, completed: boolean, createdAt: number}`
- 应用在首次运行时包含示例任务

## 文件组织

```
.
├── index.html                 # 简单HTML待办应用（完整实现）
├── README.md                  # HTML应用文档
├── CLAUDE.md                  # 本文件
├── package.json               # Node.js项目配置和脚本
├── scripts/
│   └── export_logs.mjs        # 日志导出脚本
├── logs/                      # 导出的日志文件目录
└── todo-app/                  # React TypeScript应用（可选）
```

## 重要注意事项

- HTML应用功能完整，可作为功能实现的参考
- 两个应用都设计为完全在浏览器中运行，使用localStorage

## 日志导出脚本

项目包含一个用于导出localStorage中工作日志的Node.js脚本：

### 脚本功能
- `scripts/export_logs.mjs`：使用Playwright启动静态服务器并智能检测localStorage数据源
- 支持的数据源：优先`work_logs`（向后兼容），然后`dailyTasks`（待办事项）
- `dailyTasks`数据自动转换为可读的Markdown格式（任务列表、统计信息）
- 根据数据源自动命名文件：`todos-YYYY-MM-DD.md`、`logs-YYYY-MM-DD.md`或`empty-YYYY-MM-DD.md`
- 自动创建logs目录，提供清晰的错误信息，便于调试

### 使用方法
```bash
# 安装依赖
npm install

# 运行日志导出（默认使用服务器模式）
npm run export:logs

# 使用file://协议（可能受浏览器安全限制）
node scripts/export_logs.mjs --file

# 使用指定端口的服务器模式
node scripts/export_logs.mjs --port 3000

# 显示帮助信息
node scripts/export_logs.mjs --help
```

### 命令行选项
- `--file`, `-f`: 使用file://协议直接打开HTML文件（可能受浏览器安全限制）
- `--server`, `-s`: 使用本地HTTP服务器（默认）
- `--port <port>`, `-p`: HTTP服务器端口（默认: 8080）
- `--help`, `-h`: 显示帮助信息

### 要求
- Node.js >= 18.0.0
- Playwright会自动安装，但可能需要运行`npx playwright install`安装浏览器

### 工作原理
1. 启动本地静态服务器（端口8080）
2. 使用Playwright无头浏览器访问应用
3. 智能检测localStorage数据源：优先`work_logs`，然后`dailyTasks`
4. 格式化数据：`dailyTasks`转换为Markdown任务列表，`work_logs`保持原样
5. 按数据源和日期格式保存到Markdown文件

### 故障排除
- 智能检测：脚本优先查找`work_logs`，然后`dailyTasks`，如果都不存在会显示所有可用键
- `dailyTasks`数据格式：应为JSON数组，否则会显示解析错误和原始数据
- 确保index.html文件存在于项目根目录
- 检查localStorage：在浏览器开发者工具中确认有数据
- Windows用户：脚本已测试兼容，使用标准Node.js路径处理