// 待办事项 API 服务
const API_BASE = ''; // 使用相对路径，假设前端和后端在同一域名下

/**
 * 获取任务列表
 * @param {string|null} date - 日期字符串 (YYYY-MM-DD)，默认为今天
 * @returns {Promise<Array>} 任务数组
 */
export async function getTasks(date = null) {
    const url = date ? `${API_BASE}/api/tasks?date=${date}` : `${API_BASE}/api/tasks`;
    const response = await fetch(url);

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`获取任务失败 (${response.status}): ${errorText}`);
    }

    return await response.json();
}

/**
 * 创建新任务
 * @param {string} text - 任务内容
 * @param {boolean} completed - 完成状态，默认为 false
 * @returns {Promise<Object>} 创建的任务对象
 */
export async function createTask(text, completed = false) {
    const response = await fetch(`${API_BASE}/api/tasks`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({ text, completed })
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`创建任务失败 (${response.status}): ${errorText}`);
    }

    return await response.json();
}

/**
 * 更新任务
 * @param {string} taskId - 任务ID
 * @param {Object} updates - 更新字段
 * @param {string} [updates.text] - 任务文本（可选）
 * @param {boolean} [updates.completed] - 完成状态（可选）
 * @returns {Promise<Object>} 更新后的任务对象
 */
export async function updateTask(taskId, updates) {
    const response = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(updates)
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`更新任务失败 (${response.status}): ${errorText}`);
    }

    return await response.json();
}

/**
 * 删除任务
 * @param {string} taskId - 任务ID
 * @returns {Promise<Object>} 删除结果
 */
export async function deleteTask(taskId) {
    const response = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
            'Accept': 'application/json'
        }
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`删除任务失败 (${response.status}): ${errorText}`);
    }

    return await response.json();
}

/**
 * 导入本地存储的任务数据到后端
 * @returns {Promise<{total: number, imported: number}>} 导入统计
 */
export async function importLocalStorageTasks() {
    // 从localStorage读取现有数据
    const localData = localStorage.getItem('dailyTasks');
    if (!localData) {
        throw new Error('没有找到本地数据');
    }

    const tasks = JSON.parse(localData);
    let importedCount = 0;
    let errors = [];

    // 批量导入到后端
    for (const task of tasks) {
        try {
            await createTask(task.text, task.completed || false);
            importedCount++;
        } catch (error) {
            errors.push({ task: task.text, error: error.message });
            console.warn(`导入任务失败: ${task.text}`, error);
        }
    }

    // 如果有错误，提供详细信息
    if (errors.length > 0) {
        console.warn('导入过程中部分任务失败:', errors);
    }

    return {
        total: tasks.length,
        imported: importedCount,
        errors: errors.length > 0 ? errors : undefined
    };
}

/**
 * 批量更新任务状态
 * @param {Array<string>} taskIds - 任务ID数组
 * @param {boolean} completed - 目标完成状态
 * @returns {Promise<Array>} 更新结果数组
 */
export async function batchUpdateTasks(taskIds, completed) {
    const results = [];

    for (const taskId of taskIds) {
        try {
            const result = await updateTask(taskId, { completed });
            results.push({ taskId, success: true, task: result });
        } catch (error) {
            results.push({ taskId, success: false, error: error.message });
        }
    }

    return results;
}

/**
 * 检查后端服务是否可用
 * @returns {Promise<boolean>} 服务是否可用
 */
export async function checkServerHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

/**
 * 获取今天的日期字符串 (YYYY-MM-DD)
 * @returns {string} 日期字符串
 */
export function getTodayDateString() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * 格式化日期时间
 * @param {string} isoString - ISO 8601 时间字符串
 * @returns {string} 格式化后的时间
 */
export function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// 导出默认API配置
export default {
    API_BASE,
    getTasks,
    createTask,
    updateTask,
    deleteTask,
    importLocalStorageTasks,
    batchUpdateTasks,
    checkServerHealth,
    getTodayDateString,
    formatDateTime
};