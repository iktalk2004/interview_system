# 代码题目模块设置指南

## 问题修复

### 导入错误已修复

修复了 `codeQuestions.js` 中的导入路径错误：
- **原路径**: `import request from '@/utils/request'`
- **新路径**: `import api from '@/api'`

同时修复了 API URL 格式：
- **原格式**: `/code-questions/questions/`
- **新格式**: `code-questions/questions/`

## 快速设置

### 方法1：使用自动脚本（推荐）

#### 步骤1：安装 Monaco Editor
```bash
# 双击运行
install_monaco.bat
```

#### 步骤2：设置数据库和生成测试数据
```bash
# 双击运行
setup_code_questions.bat
```

### 方法2：手动设置

#### 步骤1：安装 Monaco Editor
```bash
cd frontend
npm install monaco-editor
```

#### 步骤2：创建数据库迁移
```bash
cd backend
python manage.py makemigrations code_questions
```

#### 步骤3：应用数据库迁移
```bash
python manage.py migrate code_questions
```

#### 步骤4：生成示例题目
```bash
python manage.py generate_code_questions
```

#### 步骤5：启动服务器
```bash
# 后端
cd backend
python manage.py runserver

# 前端（新终端）
cd frontend
npm run dev
```

## 访问应用

### 前端地址
- 代码练习列表：http://localhost:5173/code-practice
- 代码题目详情：http://localhost:5173/code-practice/1
- API 文档：http://localhost:8000/swagger/

### 后端管理
- Django Admin：http://localhost:8000/admin/

## 功能说明

### 代码题目列表
- 查看所有代码题目
- 按语言、难度、分类筛选
- 搜索题目
- 分页浏览

### 代码题目详情
- 查看题目描述
- 查看示例测试用例
- 在线代码编辑器
- 提交代码
- 查看运行结果
- 收藏题目
- 添加笔记

### 代码编辑器
- 基于 Monaco Editor
- 语法高亮
- 代码自动补全
- 多语言支持
- 深色/浅色主题

### 代码执行
- 实时代码运行
- 多测试用例验证
- 性能指标（运行时间、内存使用）
- 详细的错误报告

### 支持的编程语言
- Python
- Java
- JavaScript
- C++
- Go
- Rust

## 示例题目

系统包含 5 个示例算法题目：

1. **Two Sum**（两数之和）
   - 难度：Easy
   - 语言：Python
   - 测试用例：3 个

2. **Reverse String**（反转字符串）
   - 难度：Easy
   - 语言：Python
   - 测试用例：3 个

3. **Valid Parentheses**（有效括号）
   - 难度：Medium
   - 语言：Python
   - 测试用例：5 个

4. **Maximum Subarray**（最大子数组和）
   - 难度：Medium
   - 语言：Python
   - 测试用例：4 个

5. **Merge Two Sorted Lists**（合并两个有序链表）
   - 难度：Medium
   - 语言：Python
   - 测试用例：3 个

## API 接口

### 代码题目
- `GET /api/code-questions/questions/` - 获取题目列表
- `GET /api/code-questions/questions/{id}/` - 获取题目详情
- `POST /api/code-questions/questions/{id}/submit/` - 提交代码
- `POST /api/code-questions/questions/{id}/bookmark/` - 收藏/取消收藏
- `GET /api/code-questions/questions/{id}/note/` - 获取笔记
- `POST /api/code-questions/questions/{id}/note/` - 创建笔记
- `PUT /api/code-questions/questions/{id}/note/` - 更新笔记
- `GET /api/code-questions/questions/bookmarks/` - 获取收藏列表
- `GET /api/code-questions/questions/statistics/` - 获取统计信息

### 测试用例
- `GET /api/code-questions/test-cases/` - 获取测试用例列表
- `POST /api/code-questions/test-cases/` - 创建测试用例

### 提交记录
- `GET /api/code-questions/submissions/` - 获取提交记录列表
- `GET /api/code-questions/submissions/latest/` - 获取最新提交记录

## 代码执行状态

- `pending` - 等待中
- `running` - 运行中
- `accepted` - 通过
- `wrong_answer` - 答案错误
- `time_limit_exceeded` - 超时
- `memory_limit_exceeded` - 内存超限
- `runtime_error` - 运行时错误
- `compile_error` - 编译错误
- `system_error` - 系统错误

## 常见问题

### Q1: Monaco Editor 无法加载？
A: 确保已安装 `monaco-editor` 依赖：
```bash
cd frontend
npm install monaco-editor
```

### Q2: 代码提交后没有响应？
A: 检查后端服务器是否正常运行，查看浏览器控制台是否有错误信息。

### Q3: 代码执行超时？
A: 检查题目设置的时间限制，确保代码在限制时间内完成。

### Q4: 如何添加新的编程语言？
A: 在 `CodeQuestion` 模型的 `LANGUAGE_CHOICES` 中添加新语言，并在 `CodeExecutor` 类中实现对应的执行方法。

### Q5: 测试用例如何编写？
A: 测试用例的输入和输出必须是 JSON 格式：
```json
{
  "input_data": "{\"nums\": [2, 7, 11, 15], \"target\": 9}",
  "expected_output": "[0, 1]"
}
```

## 技术栈

### 后端
- Django REST Framework
- Python 3.x
- SQLite/PostgreSQL
- subprocess（代码执行）

### 前端
- Vue 3
- Element Plus
- Monaco Editor
- Axios

## 下一步

1. 安装 Monaco Editor
2. 运行数据库迁移
3. 生成示例题目
4. 启动服务器
5. 访问代码练习页面

## 文档

详细文档请查看：[CODE_QUESTIONS_GUIDE.md](CODE_QUESTIONS_GUIDE.md)

## 支持

如有问题，请查看：
- 浏览器控制台错误
- 后端服务器日志
- API 文档：http://localhost:8000/swagger/
