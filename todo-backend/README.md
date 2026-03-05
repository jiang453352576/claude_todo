# 待办事项后端服务

基于 FastAPI 的待办事项应用后端服务，提供 RESTful API 接口。

## 功能特性

- ✅ **RESTful API**：标准的 CRUD 操作
- ✅ **按日期存储**：每天的任务存储在独立的 JSON 文件中
- ✅ **CORS 支持**：前端跨域访问
- ✅ **数据持久化**：文件系统存储，无需数据库
- ✅ **自动生成ID**：使用 UUID 作为任务唯一标识
- ✅ **完整文档**：自动生成的 OpenAPI 文档

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行服务

```bash
# 开发模式（自动重载）
uvicorn main:app --reload --port 8000

# 或直接运行
python main.py
```

### 访问 API 文档

服务启动后，访问以下地址：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 获取任务列表
```
GET /api/tasks
GET /api/tasks?date=2026-03-04
```

### 创建任务
```
POST /api/tasks
Content-Type: application/json

{
  "text": "任务内容",
  "completed": false
}
```

### 更新任务
```
PUT /api/tasks/{task_id}
Content-Type: application/json

{
  "text": "更新后的内容",
  "completed": true
}
```

### 删除任务
```
DELETE /api/tasks/{task_id}
```

## 数据存储

数据按日期存储在 `logs/` 目录下：
```
logs/
├── 2026-03-03.json
├── 2026-03-04.json
└── 2026-03-05.json
```

每个文件包含当天的所有任务，格式为 JSON 数组：
```json
[
  {
    "id": "uuid-string",
    "text": "任务内容",
    "completed": false,
    "createdAt": "2026-03-04T10:30:00Z",
    "updatedAt": "2026-03-04T10:30:00Z"
  }
]
```

## 项目结构

```
todo-backend/
├── main.py              # FastAPI 应用入口
├── requirements.txt     # Python 依赖
├── README.md           # 本文件
└── logs/               # 数据存储目录（自动创建）
```

## 开发说明

### 环境要求
- Python 3.8+
- FastAPI 0.104+
- Uvicorn 0.24+

### 测试 API
```bash
# 获取任务列表
curl http://localhost:8000/api/tasks

# 创建新任务
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"text":"测试任务","completed":false}'
```

### 生产环境注意事项
1. 修改 CORS 配置，限制允许的域名
2. 添加身份验证（如 JWT）
3. 配置日志记录
4. 设置文件备份策略

## 许可证

MIT