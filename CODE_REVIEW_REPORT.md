# 项目代码审查报告

## 项目概述
**项目名称**: 基于协同过滤的程序员八股文答题训练系统  
**技术栈**: Django REST Framework + Vue 3 + Element Plus  
**审查日期**: 2026-02-17  

---

## 一、高优先级问题

### 1. 安全性问题

#### 1.1 敏感信息泄露
**问题**: [settings.py](file:///e:\04_Interview_system\backend\core\settings.py#L31) 中 SECRET_KEY 使用了默认值
```python
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-sg$bxu71otf1y9$5dyvy2@j*@3w4ev@2w_j*60g7*o+p_b4)ro')
```

**影响**: 生产环境存在严重安全风险  
**建议**:
- 确保生产环境使用环境变量设置 SECRET_KEY
- 使用强随机密钥生成器生成密钥
- 不要在代码中硬编码密钥

**修复方案**:
```python
# .env 文件
SECRET_KEY=your-very-long-random-secret-key-here

# settings.py
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in environment variables")
```

#### 1.2 DEBUG 模式
**问题**: [settings.py](file:///e:\04_Interview_system\backend\core\settings.py#L34) 中 DEBUG=True
```python
DEBUG = True
```

**影响**: 生产环境会暴露敏感信息  
**建议**:
```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

#### 1.3 CORS 配置
**问题**: [settings.py](file:///e:\04_Interview_system\backend\core\settings.py#L120) 中 CORS 配置过于宽松
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

**建议**: 生产环境应该使用更严格的 CORS 配置
```python
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True
```

#### 1.4 密码验证
**问题**: [settings.py](file:///e:\04_Interview_system\backend\core\settings.py#L76-87) 中密码验证器配置过于宽松
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
```

**建议**: 添加自定义密码验证器，要求更复杂的密码
```python
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "max_similarity": 0.7,
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]
```

#### 1.5 JWT Token 过期时间
**问题**: [settings.py](file:///e:\04_Interview_system\backend\core\settings.py#L145-150) 中 ACCESS_TOKEN_LIFETIME 过长
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # token 有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # refresh token 有效期
}
```

**建议**: 缩短访问令牌有效期
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### 2. 代码质量问题

#### 2.1 缺少类型注解
**问题**: 后端代码中缺少类型注解，影响代码可读性和 IDE 支持

**建议**: 在所有函数中添加类型注解
```python
# 修改前
def calculate_user_similarity(user_a, user_b, min_common_questions=2):
    pass

# 修改后
from typing import Optional
from django.contrib.auth.models import User

def calculate_user_similarity(
    user_a: User,
    user_b: User,
    min_common_questions: int = 2
) -> float:
    pass
```

#### 2.2 缺少文档字符串
**问题**: 部分函数缺少详细的文档字符串

**建议**: 使用 Google 风格的文档字符串
```python
def calculate_user_similarity(
    user_a: User,
    user_b: User,
    min_common_questions: int = 2
) -> float:
    """
    计算两个用户之间的相似度（基于余弦相似度）

    Args:
        user_a: 用户 A
        user_b: 用户 B
        min_common_questions: 最小共同答题数量，低于此值返回 0

    Returns:
        float: 相似度分数 (0-1)

    Raises:
        ValueError: 当用户参数无效时

    Examples:
        >>> similarity = calculate_user_similarity(user1, user2)
        >>> print(similarity)
        0.85
    """
```

#### 2.3 前端组件过大
**问题**: [CodePracticeDetail.vue](file:///e:\04_Interview_system\frontend\src\components\CodePracticeDetail.vue) 组件代码行数过多（超过 300 行）

**建议**: 拆分为更小的组件
```vue
<!-- CodePracticeDetail.vue -->
<template>
  <CodeDetailHeader :question="question" />
  <CodeDescription :question="question" />
  <CodeEditor v-model="code" />
  <CodeResult :result="submissionResult" />
</template>

<script setup>
import CodeDetailHeader from './CodeDetailHeader.vue'
import CodeDescription from './CodeDescription.vue'
import CodeEditor from './CodeEditor.vue'
import CodeResult from './CodeResult.vue'
</script>
```

#### 2.4 代码重复
**问题**: 前端组件中存在重复的代码逻辑

**建议**: 提取公共逻辑到 composables
```javascript
// composables/useQuestion.js
export function useQuestion() {
  const question = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchQuestion = async (id) => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/questions/${id}/`)
      question.value = response.data
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return { question, loading, error, fetchQuestion }
}
```

### 3. 性能问题

#### 3.1 N+1 查询问题
**问题**: [algorithms.py](file:///e:\04_Interview_system\backend\recommender\algorithms.py#L75-95) 中存在 N+1 查询问题
```python
for interaction in similar_user_interactions:
    question_id = interaction.question_id
    score = interaction.score
    # 这里可能导致 N+1 查询
```

**建议**: 使用 select_related 或 prefetch_related 优化查询
```python
similar_user_interactions = Interaction.objects.filter(
    user=similar_user,
    score__isnull=False,
    is_submitted=True,
    score__gte=60
).exclude(question_id__in=answered_questions).select_related('question')
```

#### 3.2 缺少数据库索引
**问题**: 部分模型缺少必要的数据库索引

**建议**: 添加索引以提升查询性能
```python
class Interaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.FloatField(null=True)
    is_submitted = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_submitted']),
            models.Index(fields=['question', 'is_submitted']),
            models.Index(fields=['score']),
            models.Index(fields=['created_at']),
        ]
```

#### 3.3 前端性能优化
**问题**: 前端组件未使用虚拟滚动处理大量数据

**建议**: 对于列表组件使用虚拟滚动
```vue
<template>
  <el-table-v2
    :columns="columns"
    :data="questions"
    :width="700"
    :height="400"
    fixed
  />
</template>
```

#### 3.4 缺少缓存机制
**问题**: 推荐系统计算结果未缓存

**建议**: 添加缓存层
```python
from django.core.cache import cache

def get_recommendations(user_id):
    cache_key = f'recommendations_{user_id}'
    recommendations = cache.get(cache_key)
    
    if recommendations is None:
        recommendations = CollaborativeFiltering.hybrid_recommend(user_id)
        cache.set(cache_key, recommendations, timeout=3600)  # 缓存 1 小时
    
    return recommendations
```

---

## 二、中优先级问题

### 4. 数据库设计问题

#### 4.1 缺少软删除
**问题**: 所有删除操作都是硬删除，数据无法恢复

**建议**: 添加软删除功能
```python
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

class Question(SoftDeleteModel):
    title = models.CharField(max_length=200)
```

#### 4.2 缺少审计日志
**问题**: 没有记录数据变更历史

**建议**: 添加审计日志模型
```python
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changes = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user', 'created_at']),
        ]
```

#### 4.3 JSON 字段使用
**问题**: [UserPreference](file:///e:\04_Interview_system\backend\recommender\models.py#L88-95) 模型中大量使用 JSONField

**建议**: 考虑使用关系型模型替代 JSONField，以便更好地查询和验证
```python
class UserPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference_profile')
    avg_score = models.FloatField(default=0.0)
    total_answered = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

class UserCategoryPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_preferences')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    avg_score = models.FloatField(default=0.0)
    count = models.IntegerField(default=0)
    weight = models.FloatField(default=0.0)
```

### 5. API 设计问题

#### 5.1 缺少 API 版本控制
**问题**: API 路径没有版本控制

**建议**: 添加版本控制
```python
# urls.py
urlpatterns = [
    path("api/v1/users/", include("users.urls")),
    path("api/v1/questions/", include("questions.urls")),
]
```

#### 5.2 缺少分页参数验证
**问题**: API 分页参数未验证，可能导致性能问题

**建议**: 添加分页参数验证
```python
class CodeQuestionViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        page_size = int(self.request.query_params.get('page_size', 20))
        page_size = min(page_size, 100)  # 限制最大每页数量
        
        queryset = CodeQuestion.objects.all()
        # ...
```

#### 5.3 缺少请求限流
**问题**: API 没有请求限流机制

**建议**: 添加请求限流
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
```

#### 5.4 错误响应不统一
**问题**: API 错误响应格式不统一

**建议**: 统一错误响应格式
```python
# utils/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': {
                'code': response.status_code,
                'message': str(exc),
                'details': response.data
            }
        }
        response.data = custom_response_data
    
    return response

# settings.py
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
}
```

### 6. 错误处理和日志

#### 6.1 缺少日志记录
**问题**: 代码中缺少日志记录

**建议**: 添加日志记录
```python
import logging

logger = logging.getLogger(__name__)

def calculate_user_similarity(user_a, user_b, min_common_questions=2):
    logger.info(f"Calculating similarity between user {user_a.id} and {user_b.id}")
    try:
        # ...
        logger.info(f"Similarity calculated: {similarity}")
        return similarity
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}", exc_info=True)
        raise
```

#### 6.2 异常处理不完善
**问题**: 部分代码缺少异常处理

**建议**: 添加完善的异常处理
```python
def execute(self, code, language, test_cases, time_limit=1000, memory_limit=256):
    try:
        # 执行代码
        result = self._run_test_case(code, language, test_cases)
        return result
    except subprocess.TimeoutExpired:
        logger.warning(f"Code execution timeout for {language}")
        return {
            'status': 'time_limit_exceeded',
            'error': 'Execution timeout'
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Code execution failed: {e}")
        return {
            'status': 'runtime_error',
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'status': 'system_error',
            'error': 'Internal system error'
        }
```

#### 6.3 缺少监控和告警
**问题**: 没有系统监控和告警机制

**建议**: 添加监控和告警
```python
# middleware/monitoring.py
import time
import logging

logger = logging.getLogger(__name__)

class MonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration = time.time() - start_time
        
        if duration > 1.0:  # 超过 1 秒的请求
            logger.warning(f"Slow request: {request.path} took {duration:.2f}s")
        
        return response

# settings.py
MIDDLEWARE = [
    'middleware.monitoring.MonitoringMiddleware',
    # ...
]
```

---

## 三、低优先级问题

### 7. 测试覆盖率

#### 7.1 缺少单元测试
**问题**: 项目中几乎没有单元测试

**建议**: 添加单元测试
```python
# tests/test_algorithms.py
from django.test import TestCase
from recommender.algorithms import CollaborativeFiltering
from users.models import User

class CollaborativeFilteringTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
    
    def test_calculate_user_similarity(self):
        similarity = CollaborativeFiltering.calculate_user_similarity(
            self.user1, self.user2
        )
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
```

#### 7.2 缺少集成测试
**问题**: 没有 API 集成测试

**建议**: 添加集成测试
```python
# tests/test_api.py
from rest_framework.test import APITestCase
from users.models import User

class QuestionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.client.force_authenticate(user=self.user)
    
    def test_get_questions(self):
        response = self.client.get('/api/questions/')
        self.assertEqual(response.status_code, 200)
```

### 8. 文档问题

#### 8.1 缺少 API 文档
**问题**: API 文档不完整

**建议**: 完善 API 文档
```python
# views.py
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    operation_description="获取代码题目列表",
    responses={200: CodeQuestionListSerializer(many=True)},
    manual_parameters=[
        openapi.Parameter(
            'search',
            openapi.IN_QUERY,
            description="搜索关键词",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'language',
            openapi.IN_QUERY,
            description="编程语言",
            type=openapi.TYPE_STRING,
            enum=['python', 'java', 'javascript', 'cpp', 'go', 'rust']
        ),
    ]
)
def list(self, request):
    pass
```

#### 8.2 缺少部署文档
**问题**: 没有详细的部署文档

**建议**: 创建部署文档
```markdown
# DEPLOYMENT.md

## 生产环境部署

### 环境要求
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+

### 部署步骤
1. 配置环境变量
2. 安装依赖
3. 数据库迁移
4. 收集静态文件
5. 配置 Nginx
6. 配置 Supervisor
```

#### 8.3 缺少开发文档
**问题**: 缺少开发规范和贡献指南

**建议**: 创建开发文档
```markdown
# CONTRIBUTING.md

## 开发规范

### 代码风格
- Python: 遵循 PEP 8
- JavaScript: 遵循 ESLint 规则
- Vue: 遵循 Vue 风格指南

### 提交规范
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具
```

### 9. 用户体验问题

#### 9.1 缺少加载状态
**问题**: 部分页面缺少加载状态提示

**建议**: 添加加载状态
```vue
<template>
  <div v-loading="loading" element-loading-text="Loading...">
    <!-- 内容 -->
  </div>
</template>
```

#### 9.2 缺少错误提示
**问题**: 错误提示不够友好

**建议**: 改进错误提示
```javascript
try {
  await api.submitCode(code)
} catch (error) {
  if (error.response?.status === 400) {
    ElMessage.error('代码格式错误，请检查')
  } else if (error.response?.status === 500) {
    ElMessage.error('服务器错误，请稍后重试')
  } else {
    ElMessage.error('提交失败，请重试')
  }
}
```

#### 9.3 缺少离线支持
**问题**: 应用不支持离线使用

**建议**: 添加离线支持
```javascript
// 使用 Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js')
}
```

---

## 四、优化建议

### 10. 架构优化

#### 10.1 微服务化
**建议**: 考虑将推荐系统、代码执行等独立为微服务

#### 10.2 消息队列
**建议**: 使用 Celery + Redis 处理异步任务
```python
# tasks.py
from celery import shared_task

@shared_task
def execute_code_async(submission_id):
    submission = CodeSubmission.objects.get(id=submission_id)
    executor = CodeExecutor()
    result = executor.execute(...)
    # 更新提交记录
```

#### 10.3 CDN 加速
**建议**: 使用 CDN 加速静态资源
```python
# settings.py
STATIC_URL = 'https://cdn.example.com/static/'
```

### 11. 功能增强

#### 11.1 实时通知
**建议**: 添加 WebSocket 实时通知
```python
# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        # 处理消息
```

#### 11.2 数据导出
**建议**: 添加数据导出功能
```python
@action(detail=False, methods=['get'])
def export(self, request):
    data = self.get_queryset()
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    # 写入数据
    return response
```

#### 11.3 国际化
**建议**: 添加多语言支持
```python
# settings.py
LANGUAGE_CODE = 'zh-hans'
USE_I18N = True

# 前端
import { createI18n } from 'vue-i18n'
```

---

## 五、总结

### 优先级排序

1. **立即修复**（高优先级）
   - 安全性问题（SECRET_KEY、DEBUG、CORS）
   - 密码验证
   - JWT Token 过期时间

2. **尽快修复**（中优先级）
   - N+1 查询问题
   - 数据库索引
   - 错误处理和日志
   - API 版本控制

3. **逐步改进**（低优先级）
   - 单元测试
   - 文档完善
   - 用户体验优化

### 代码质量评分

| 类别 | 评分 | 说明 |
|------|------|------|
| 安全性 | 6/10 | 存在多个安全隐患 |
| 性能 | 7/10 | 有优化空间 |
| 可维护性 | 7/10 | 代码结构清晰但缺少文档 |
| 测试覆盖率 | 3/10 | 几乎没有测试 |
| 用户体验 | 8/10 | 界面友好但缺少细节 |

### 整体评价

项目整体架构合理，功能完整，但在安全性、性能优化和测试方面还有较大改进空间。建议优先解决高优先级的安全问题，然后逐步优化性能和完善测试。

---

## 附录

### A. 推荐工具

- 代码质量: pylint, black, isort
- 测试: pytest, pytest-django, pytest-cov
- 性能分析: django-debug-toolbar, silk
- 文档: Sphinx, MkDocs
- 监控: Sentry, Prometheus

### B. 参考资源

- Django 最佳实践: https://docs.djangoproject.com/
- Vue 风格指南: https://vuejs.org/style-guide/
- REST API 设计: https://restfulapi.net/
- 安全最佳实践: https://owasp.org/
