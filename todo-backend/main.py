from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime, date as date_type
import json
import os
import uuid
from typing import List, Optional
from pathlib import Path
from fastapi.responses import FileResponse

# 创建FastAPI应用
app = FastAPI(title="待办事项API", description="待办事项应用的后端API服务", version="1.0.0")

# CORS配置 - 开发环境允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent

# 静态文件服务 - 提供前端HTML/CSS/JS文件
# 注意：静态文件目录设置为父目录，以便访问index.html和api.js
app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")

# 首页返回 index.html
@app.get("/")
def serve_index():
    return FileResponse(str(BASE_DIR / "index.html"))

# 数据模型
class TaskBase(BaseModel):
    text: str
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None

class Task(TaskBase):
    id: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True

# 工具函数
def ensure_logs_dir():
    """确保logs目录存在"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    return logs_dir

def get_file_path_for_date(date_str: str) -> Path:
    """根据日期获取文件路径"""
    ensure_logs_dir()
    return Path("logs") / f"{date_str}.json"

def get_today_file_path() -> Path:
    """获取今日数据文件路径"""
    today_str = datetime.now().strftime("%Y-%m-%d")
    return get_file_path_for_date(today_str)

def read_tasks_from_file(file_path: Path) -> List[Task]:
    """从文件读取任务列表"""
    if not file_path.exists():
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 验证数据格式
            if isinstance(data, list):
                return [Task(**task) for task in data]
            else:
                return []
    except (json.JSONDecodeError, IOError) as e:
        print(f"读取文件错误 {file_path}: {e}")
        return []

def generate_markdown_content(tasks: List[Task]) -> str:
    """生成markdown格式的任务列表"""
    if not tasks:
        return "# 今日任务\n\n暂无任务\n"

    # 按完成状态分组
    completed_tasks = [t for t in tasks if t.completed]
    pending_tasks = [t for t in tasks if not t.completed]

    lines = []
    lines.append("# 今日任务\n")
    lines.append(f"**统计**：共 {len(tasks)} 个任务，已完成 {len(completed_tasks)} 个，待完成 {len(pending_tasks)} 个\n")
    lines.append(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if pending_tasks:
        lines.append("\n## 待完成任务\n")
        for i, task in enumerate(pending_tasks, 1):
            created = datetime.fromisoformat(task.createdAt).strftime('%H:%M')
            lines.append(f"{i}. [ ] {task.text} _(添加于 {created})_\n")

    if completed_tasks:
        lines.append("\n## 已完成任务\n")
        for i, task in enumerate(completed_tasks, 1):
            created = datetime.fromisoformat(task.createdAt).strftime('%H:%M')
            completed_time = datetime.fromisoformat(task.updatedAt).strftime('%H:%M')
            lines.append(f"{i}. [x] ~~{task.text}~~ _(添加于 {created}, 完成于 {completed_time})_\n")

    lines.append("\n---\n*使用待办事项应用生成*")
    return "".join(lines)


def write_markdown_file(json_file_path: Path, tasks: List[Task]):
    """根据JSON文件路径生成对应的markdown文件"""
    if json_file_path.suffix != '.json':
        return

    # 将.json替换为.md
    md_file_path = json_file_path.with_suffix('.md')
    try:
        content = generate_markdown_content(tasks)
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Markdown文件已生成: {md_file_path}")
    except IOError as e:
        print(f"写入Markdown文件错误 {md_file_path}: {e}")


def write_tasks_to_file(file_path: Path, tasks: List[Task]):
    """将任务列表写入文件"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            # 转换为字典列表
            tasks_dict = [task.model_dump() for task in tasks]
            json.dump(tasks_dict, f, ensure_ascii=False, indent=2)

        # 同时生成markdown文件
        write_markdown_file(file_path, tasks)
    except IOError as e:
        print(f"写入文件错误 {file_path}: {e}")
        raise HTTPException(status_code=500, detail="保存数据失败")

def find_task_by_id(tasks: List[Task], task_id: str) -> Optional[int]:
    """在任务列表中查找任务索引"""
    for i, task in enumerate(tasks):
        if task.id == task_id:
            return i
    return None

# API端点
@app.get("/api")
async def root():
    """API信息"""
    return {
        "name": "待办事项API",
        "version": "1.0.0",
        "description": "待办事项应用的后端服务",
        "docs": "/docs",
        "endpoints": {
            "获取任务": "GET /api/tasks",
            "创建任务": "POST /api/tasks",
            "更新任务": "PUT /api/tasks/{id}",
            "删除任务": "DELETE /api/tasks/{id}"
        }
    }

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks(date: Optional[str] = None):
    """
    获取任务列表

    - **date**: 可选，日期字符串（格式：YYYY-MM-DD），默认为今天
    """
    try:
        if date:
            # 验证日期格式
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="日期格式无效，请使用YYYY-MM-DD格式")
            file_path = get_file_path_for_date(date)
        else:
            file_path = get_today_file_path()

        tasks = read_tasks_from_file(file_path)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务失败: {str(e)}")

@app.post("/api/tasks", response_model=Task)
async def create_task(task_create: TaskCreate):
    """创建新任务"""
    try:
        file_path = get_today_file_path()
        tasks = read_tasks_from_file(file_path)

        # 创建新任务
        now = datetime.now().isoformat()
        new_task = Task(
            id=str(uuid.uuid4()),
            text=task_create.text,
            completed=task_create.completed,
            createdAt=now,
            updatedAt=now
        )

        tasks.append(new_task)
        write_tasks_to_file(file_path, tasks)

        return new_task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

@app.put("/api/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """更新任务"""
    try:
        file_path = get_today_file_path()
        tasks = read_tasks_from_file(file_path)

        task_index = find_task_by_id(tasks, task_id)
        if task_index is None:
            raise HTTPException(status_code=404, detail="任务未找到")

        # 更新任务字段
        task = tasks[task_index]
        if task_update.text is not None:
            task.text = task_update.text
        if task_update.completed is not None:
            task.completed = task_update.completed

        task.updatedAt = datetime.now().isoformat()
        tasks[task_index] = task

        write_tasks_to_file(file_path, tasks)

        return task
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新任务失败: {str(e)}")

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    try:
        file_path = get_today_file_path()
        tasks = read_tasks_from_file(file_path)

        task_index = find_task_by_id(tasks, task_id)
        if task_index is None:
            raise HTTPException(status_code=404, detail="任务未找到")

        # 删除任务
        deleted_task = tasks.pop(task_index)
        write_tasks_to_file(file_path, tasks)

        return {
            "message": "任务删除成功",
            "deleted_task": deleted_task.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)