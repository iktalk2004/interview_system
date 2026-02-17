# 代码题目模块使用指南

## 概述

代码题目模块是一个完整的在线编程练习系统，支持多种编程语言、代码编辑、自动测试和结果分析。

## 功能特性

### 1. 支持的编程语言
- Python
- Java
- JavaScript
- C++
- Go
- Rust

### 2. 核心功能
- 代码题目浏览和搜索
- 在线代码编辑器（基于 Monaco Editor）
- 代码提交和自动测试
- 测试用例管理（示例用例和隐藏用例）
- 题目收藏
- 题目笔记
- 提交历史记录
- 统计分析

### 3. 代码执行
- 安全的代码执行环境
- 时间限制控制
- 内存限制控制
- 多测试用例并行执行
- 详细的错误报告

## 数据模型

### CodeQuestion（代码题目）
```python
class CodeQuestion(models.Model):
    question = OneToOneField(Question)  # 关联基础题目
    language = CharField  # 编程语言
    template_code = TextField  # 代码模板
    starter_code = TextField  # 初始代码
    function_signature = CharField  # 函数签名
    time_limit = IntegerField  # 时间限制（毫秒）
    memory_limit = IntegerField  # 内存限制（MB）
    is_public = BooleanField  # 是否公开
```

### TestCase（测试用例）
```python
class TestCase(models.Model):
    code_question = ForeignKey(CodeQuestion)
    input_data = TextField  # 输入数据（JSON）
    expected_output = TextField  # 期望输出（JSON）
    is_hidden = BooleanField  # 是否隐藏
    is_sample = BooleanField  # 是否为示例用例
    order = IntegerField  # 排序
```

### CodeSubmission（代码提交）
```python
class CodeSubmission(models.Model):
    user = ForeignKey(User)
    code_question = ForeignKey(CodeQuestion)
    code = TextField  # 提交的代码
    language = CharField  # 编程语言
    status = CharField  # 状态
    runtime = IntegerField  # 运行时间（毫秒）
    memory = IntegerField  # 内存使用（KB）
    passed_test_cases = IntegerField  # 通过的测试用例数
    total_test_cases = IntegerField  # 总测试用例数
    error_message = TextField  # 错误信息
    test_case_results = JSONField  # 测试用例结果详情
```

### CodeBookmark（题目收藏）
```python
class CodeBookmark(models.Model):
    user = ForeignKey(User)
    code_question = ForeignKey(CodeQuestion)
    created_at = DateTimeField
```

### CodeNote（题目笔记）
```python
class CodeNote(models.Model):
    user = ForeignKey(User)
    code_question = ForeignKey(CodeQuestion)
    content = TextField  # 笔记内容
    created_at = DateTimeField
    updated_at = DateTimeField
```

## API 接口

### 代码题目接口

#### 获取题目列表
```
GET /api/code-questions/questions/
```

查询参数：
- `search`: 搜索关键词
- `language`: 编程语言
- `difficulty`: 难度（1-3）
- `category`: 分类ID
- `ordering`: 排序方式
- `page`: 页码
- `page_size`: 每页数量

#### 获取题目详情
```
GET /api/code-questions/questions/{id}/
```

#### 收藏/取消收藏题目
```
POST /api/code-questions/questions/{id}/bookmark/
```

#### 获取/创建/更新笔记
```
GET /api/code-questions/questions/{id}/note/
POST /api/code-questions/questions/{id}/note/
PUT /api/code-questions/questions/{id}/note/
```

#### 提交代码
```
POST /api/code-questions/questions/{id}/submit/
```

请求体：
```json
{
  "code": "your code here",
  "language": "python"
}
```

#### 获取收藏列表
```
GET /api/code-questions/questions/bookmarks/
```

#### 获取统计信息
```
GET /api/code-questions/questions/statistics/
```

### 测试用例接口

#### 获取测试用例列表
```
GET /api/code-questions/test-cases/
```

查询参数：
- `code_question`: 代码题目ID

#### 创建测试用例
```
POST /api/code-questions/test-cases/
```

请求体：
```json
{
  "code_question": 1,
  "input_data": "{\"nums\": [2, 7, 11, 15], \"target\": 9}",
  "expected_output": "[0, 1]",
  "is_sample": true,
  "is_hidden": false,
  "order": 1
}
```

### 提交记录接口

#### 获取提交记录列表
```
GET /api/code-questions/submissions/
```

查询参数：
- `code_question`: 代码题目ID
- `status`: 状态过滤
- `page`: 页码
- `page_size`: 每页数量

#### 获取最新提交记录
```
GET /api/code-questions/submissions/latest/
```

查询参数：
- `limit`: 返回数量（默认10）

## 代码执行

### 支持的执行状态

- `pending`: 等待中
- `running`: 运行中
- `accepted`: 通过
- `wrong_answer`: 答案错误
- `time_limit_exceeded`: 超时
- `memory_limit_exceeded`: 内存超限
- `runtime_error`: 运行时错误
- `compile_error`: 编译错误
- `system_error`: 系统错误

### 代码格式要求

#### Python
```python
import sys
import json

def solution(input_data):
    # Your code here
    return result

if __name__ == '__main__':
    input_data = json.loads(sys.stdin.read())
    result = solution(input_data)
    print(json.dumps(result))
```

#### Java
```java
import java.util.*;
import java.io.*;

public class Solution {
    public static Object solution(Map<String, Object> input) {
        // Your code here
        return result;
    }

    public static void main(String[] args) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            sb.append(line);
        }
        
        // Parse JSON and call solution
        // Print result
    }
}
```

#### JavaScript
```javascript
function solution(inputData) {
    // Your code here
    return result;
}

const input = require('fs').readFileSync(0, 'utf-8');
const inputData = JSON.parse(input);
const result = solution(inputData);
console.log(JSON.stringify(result));
```

#### C++
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <json/json.h> // or use nlohmann/json

using namespace std;

// Your solution function
// ...

int main() {
    // Read JSON input
    // Call solution
    // Print JSON output
    return 0;
}
```

#### Go
```go
package main

import (
    "encoding/json"
    "fmt"
    "os"
)

type InputData struct {
    // Define your input structure
}

func solution(input InputData) interface{} {
    // Your code here
    return result
}

func main() {
    var input InputData
    decoder := json.NewDecoder(os.Stdin)
    decoder.Decode(&input)
    
    result := solution(input)
    
    encoder := json.NewEncoder(os.Stdout)
    encoder.Encode(result)
}
```

#### Rust
```rust
use serde::{Deserialize, Serialize};
use std::io::{self, Read};

#[derive(Deserialize)]
struct InputData {
    // Define your input structure
}

#[derive(Serialize)]
struct OutputData {
    // Define your output structure
}

fn solution(input: InputData) -> OutputData {
    // Your code here
    OutputData {}
}

fn main() {
    let mut input_str = String::new();
    io::stdin().read_to_string(&mut input_str).unwrap();
    let input: InputData = serde_json::from_str(&input_str).unwrap();
    
    let result = solution(input);
    
    println!("{}", serde_json::to_string(&result).unwrap());
}
```

## 前端组件

### CodeEditor（代码编辑器）
```vue
<CodeEditor
  v-model="code"
  :language="'python'"
  :height="'500px'"
  @change="handleCodeChange"
/>
```

Props:
- `modelValue`: 代码内容（v-model）
- `language`: 编程语言
- `readonly`: 是否只读
- `height`: 编辑器高度

Events:
- `update:modelValue`: 代码更新
- `change`: 代码变化

### CodePractice（代码练习列表）
```vue
<CodePractice />
```

功能：
- 题目列表展示
- 搜索和过滤
- 分页
- 难度标签
- 语言标签

### CodePracticeDetail（代码练习详情）
```vue
<CodePracticeDetail />
```

功能：
- 题目描述
- 示例测试用例
- 代码编辑器
- 代码提交
- 结果展示
- 收藏功能
- 笔记功能

## 数据库迁移

```bash
# 创建迁移
python manage.py makemigrations code_questions

# 应用迁移
python manage.py migrate code_questions
```

## 生成测试数据

```bash
# 生成示例代码题目
python manage.py generate_code_questions
```

这将创建以下示例题目：
1. Two Sum（两数之和）
2. Reverse String（反转字符串）
3. Valid Parentheses（有效括号）
4. Maximum Subarray（最大子数组和）
5. Merge Two Sorted Lists（合并两个有序链表）

## 路由配置

### 后端路由
```python
# core/urls.py
urlpatterns = [
    path('api/code-questions/', include('code_questions.urls')),
]
```

### 前端路由
```javascript
// router/index.js
{
  path: '/code-practice',
  component: CodePractice
},
{
  path: '/code-practice/:id',
  component: CodePracticeDetail
},
{
  path: '/code-practice/bookmarks',
  component: CodeBookmarks
}
```

## 安全考虑

### 代码执行安全
1. 使用临时文件隔离
2. 设置时间限制
3. 设置内存限制
4. 限制文件系统访问
5. 禁用危险函数

### 输入验证
1. 验证代码长度
2. 验证输入数据格式
3. 验证输出数据格式
4. 防止注入攻击

## 性能优化

### 缓存策略
1. 缓存题目数据
2. 缓存测试用例
3. 缓存提交结果
4. 使用 Redis 缓存

### 异步处理
1. 异步执行代码
2. 异步发送通知
3. 使用 Celery 处理长时间任务

## 扩展功能

### 计划中的功能
1. 代码竞赛模式
2. 排行榜
3. 代码分享
4. 讨论区
5. 代码审查
6. AI 辅助编程
7. 代码模板库
8. 多语言翻译

## 常见问题

### Q1: 如何添加新的编程语言？
A: 在 `CodeQuestion` 模型的 `LANGUAGE_CHOICES` 中添加新语言，并在 `CodeExecutor` 类中实现对应的执行方法。

### Q2: 如何自定义代码编辑器主题？
A: 修改 `CodeEditor.vue` 组件中的 `theme` 属性，Monaco Editor 支持多种主题。

### Q3: 如何处理长时间运行的代码？
A: 设置合理的 `time_limit` 参数，并考虑使用异步任务队列（如 Celery）。

### Q4: 如何保护系统免受恶意代码攻击？
A: 使用容器化执行环境（如 Docker），限制资源访问，并定期更新安全补丁。

### Q5: 如何提高代码执行性能？
A: 使用缓存、异步处理、负载均衡等技术，并优化代码执行引擎。

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

### 代码执行
- Python 解释器
- Java 编译器和运行时
- Node.js（JavaScript）
- GCC（C++）
- Go 编译器和运行时
- Rust 编译器和运行时

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请联系项目维护者。
