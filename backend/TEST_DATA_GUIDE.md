# 测试数据生成脚本使用指南

本项目提供了两个Django管理命令来生成测试数据，用于测试推荐系统和数据分析功能。

## 前置条件

1. 确保已安装所有依赖：
```bash
pip install -r requirements.txt
```

2. 确保数据库已迁移：
```bash
python manage.py migrate
```

## 命令说明

### 1. 生成测试题目和分类

生成测试题目和分类数据，包括各种技术领域的题目和标准答案。

```bash
python manage.py generate_test_questions [选项]
```

**选项：**
- `--categories`: 生成的分类数量（默认：10）
- `--questions`: 生成的题目数量（默认：100）
- `--clear`: 清除现有题目和分类数据

**示例：**
```bash
# 生成默认数量的题目和分类
python manage.py generate_test_questions

# 生成200道题目和15个分类
python manage.py generate_test_questions --questions 200 --categories 15

# 清除现有数据并重新生成
python manage.py generate_test_questions --clear
```

**生成的数据包括：**
- 主分类：Python、Java、JavaScript、Vue、React、Django、Flask、Spring Boot、MySQL、PostgreSQL、MongoDB、算法与数据结构
- 子分类：各主分类下的基础、进阶、专题分类
- 题目：包含标题、标准答案、难度等级、解析等
- 难度分布：易(1)、中(2)、难(3)随机分配

### 2. 生成测试用户和交互数据

生成测试用户和他们的答题交互记录，用于测试推荐算法和数据分析功能。

```bash
python manage.py generate_test_data [选项]
```

**选项：**
- `--users`: 生成的用户数量（默认：50）
- `--interactions`: 生成的交互记录数量（默认：500）
- `--clear`: 清除现有用户和交互数据

**示例：**
```bash
# 生成默认数量的用户和交互
python manage.py generate_test_data

# 生成100个用户和1000条交互记录
python manage.py generate_test_data --users 100 --interactions 1000

# 清除现有数据并重新生成
python manage.py generate_test_data --clear
```

**生成的数据包括：**
- 用户：包含用户名、邮箱、密码、个人简介、技术偏好、管理员权限等
- 技术偏好：用户对各种技术栈的偏好设置（支持二级标签）
- 交互记录：用户的答题记录，包括答案、分数、用时、收藏状态等
- 答题状态：已提交、仅浏览、草稿等
- 分数分布：基于题目难度和随机因素生成合理的分数

## 完整测试流程

### 步骤1：生成题目和分类

首先需要生成题目数据，因为交互记录依赖于题目：

```bash
python manage.py generate_test_questions --questions 200 --categories 15
```

### 步骤2：生成用户和交互数据

生成用户和他们的答题记录：

```bash
python manage.py generate_test_data --users 100 --interactions 2000
```

### 步骤3：更新推荐系统相似度矩阵

生成数据后，必须更新推荐系统的相似度矩阵才能正常工作：

```bash
# 更新所有相似度矩阵（用户相似度 + 题目相似度）
python manage.py update_similarity_matrix --type all --min-common 1

# 只更新用户相似度
python manage.py update_similarity_matrix --type user --min-common 1

# 只更新题目相似度
python manage.py update_similarity_matrix --type question --min-common 1
```

**重要说明：**
- `--min-common` 参数指定最小共同答题数/用户数，默认为2
- 如果数据量较少，可以设置为1以获得更多相似度记录
- 每次生成新的交互数据后，都需要重新运行此命令

### 步骤4：检查推荐系统状态

检查推荐系统是否就绪：

```bash
python manage.py check_recommender_status
```

此命令会显示：
- 基础数据统计（用户数、题目数、答题记录数）
- 分数统计（最低分、最高分、平均分）
- 相似度矩阵状态（用户相似度记录数、题目相似度记录数）
- 用户和题目的答题情况
- 推荐系统就绪状态

### 步骤5：验证数据

检查生成的数据：

```bash
# 检查题目数量
python manage.py shell -c "from questions.models import Question; print(f'题目总数: {Question.objects.count()}')"

# 检查用户数量
python manage.py shell -c "from users.models import User; print(f'用户总数: {User.objects.count()}')"

# 检查交互记录数量
python manage.py shell -c "from practice.models import Interaction; print(f'交互记录总数: {Interaction.objects.count()}')"

# 检查已提交的答题数量
python manage.py shell -c "from practice.models import Interaction; print(f'已提交答题: {Interaction.objects.filter(is_submitted=True).count()}')"
```

### 步骤6：测试推荐系统

使用生成的数据测试推荐功能：

1. 登录系统
2. 访问智能推荐页面
3. 查看基于协同过滤的推荐结果
4. 点击"刷新推荐"按钮生成新的推荐

### 步骤7：测试数据分析

使用生成的数据测试数据分析功能：

1. 访问数据分析页面
2. 查看用户统计、性能趋势等
3. 访问排行榜查看用户排名

### 步骤8：测试管理后台

使用管理员账号测试后台管理功能：

1. 使用管理员账号登录（is_staff=True的用户）
2. 访问 `/dashboard` 路由
3. 查看数据概览、用户管理、题目管理等功能

## 数据特点

### 用户数据
- 用户名和邮箱使用Faker库生成中文数据
- 密码统一为 `password123`
- 约10%的用户被设置为管理员
- 技术偏好包含1-5个技术栈，支持二级标签

### 交互数据
- 约70%的交互记录为已提交状态
- 约20%的交互记录为收藏状态
- 答题时长在30秒到30分钟之间随机分布
- 分数基于题目难度调整，难度越高分数可能越低
- 每个用户对同一题目只生成一条已提交的记录

### 题目数据
- 包含13个主分类和对应的子分类
- 题目内容覆盖Python、Java、JavaScript、Vue、React、Django等多个技术栈
- 每个技术栈包含10道左右的典型面试题
- 难度均匀分布在易、中、难三个等级

## 清除测试数据

如需清除所有测试数据：

```bash
# 清除题目和分类
python manage.py generate_test_questions --clear

# 清除用户和交互
python manage.py generate_test_data --clear
```

**注意：** 清除操作会删除所有相关数据，请谨慎使用！

## 自定义数据生成

如需自定义生成的数据，可以修改相应的管理命令文件：

### 修改题目生成

编辑 `questions/management/commands/generate_test_questions.py`：
- 修改 `question_templates` 字典添加新的题目模板
- 修改 `answer_templates` 字典添加新的答案模板
- 调整难度分布逻辑

### 修改用户和交互生成

编辑 `practice/management/commands/generate_test_data.py`：
- 修改 `tech_preferences` 列表添加新的技术偏好
- 调整用户生成逻辑
- 修改分数计算算法
- 调整交互状态分布

## 性能建议

1. **小规模测试**：生成50个用户、200道题目、500条交互记录
2. **中等规模测试**：生成100个用户、500道题目、2000条交互记录
3. **大规模测试**：生成500个用户、1000道题目、10000条交互记录

根据测试目的选择合适的数据规模，避免生成过多数据影响性能。

## 常见问题

### Q1: 命令找不到
**A:** 确保已运行 `python manage.py migrate` 创建管理命令所需的目录结构。

### Q2: 生成的数据不符合预期
**A:** 可以使用 `--clear` 选项清除现有数据后重新生成，或修改脚本中的参数。

### Q3: 推荐系统没有结果
**A:** 这是推荐系统最常见的故障，请按以下步骤排查：

1. **检查相似度矩阵是否已更新**
   ```bash
   python manage.py check_recommender_status
   ```
   如果用户相似度记录和题目相似度记录都为0，说明相似度矩阵未更新。

2. **更新相似度矩阵**
   ```bash
   python manage.py update_similarity_matrix --type all --min-common 1
   ```

3. **检查分数范围**
   推荐算法要求分数在0-100范围内，且只推荐高分题目（>=60分）。
   如果生成的数据分数过低，需要重新生成数据。

4. **检查共同答题数**
   用户之间需要有共同答题才能计算相似度。如果数据量较少，可以降低`--min-common`参数。

### Q4: 数据分析页面没有数据
**A:** 检查是否已生成用户统计数据，可以使用Django shell手动触发统计更新。

### Q5: 相似度矩阵更新后仍然没有推荐
**A:** 可能的原因：
- 用户之间共同答题数太少（尝试降低`--min-common`参数）
- 所有用户分数都低于60分（推荐算法只推荐高分题目）
- 用户已经答完了所有题目

可以运行以下命令检查：
```bash
python manage.py check_recommender_status
```

### Q6: 如何重置推荐系统
**A:** 清除相似度矩阵和推荐记录：
```python
from recommender.models import UserSimilarity, QuestionSimilarity, Recommendation
UserSimilarity.objects.all().delete()
QuestionSimilarity.objects.all().delete()
Recommendation.objects.all().delete()
```

然后重新运行：
```bash
python manage.py update_similarity_matrix --type all --min-common 1
```

## 推荐系统工作原理

推荐系统基于协同过滤算法，分为三个步骤：

### 1. 计算用户相似度
- 比较两个用户的答题记录
- 计算余弦相似度
- 只考虑有共同答题的用户对

### 2. 计算题目相似度
- 比较两个题目的用户评分
- 计算余弦相似度
- 只考虑有共同答题用户的题目对

### 3. 生成推荐
- **基于用户**：推荐相似用户答得好的题目
- **基于物品**：推荐与用户已答题目相似的题目
- **混合推荐**：结合两种方法

**重要：** 每次生成新的交互数据后，都必须重新计算相似度矩阵！

## 相关文件

- `questions/management/commands/generate_test_questions.py`: 题目和分类生成脚本
- `practice/management/commands/generate_test_data.py`: 用户和交互生成脚本
- `requirements.txt`: 包含Faker依赖

## 技术栈

- Django管理命令框架
- Faker库：生成模拟数据
- Django ORM：数据库操作
