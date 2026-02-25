# 项目优化总结

## 完成日期
2026-02-17

## 完成任务概览

### 1. 添加前端状态管理 Pinia ✅

#### 创建的文件
- [stores/user.js](file:///e:\04_Interview_system\frontend\src\stores\user.js) - 用户状态管理
- [stores/question.js](file:///e:\04_Interview_system\frontend\src\stores\question.js) - 题目状态管理
- [stores/practice.js](file:///e:\04_Interview_system\frontend\src\stores\practice.js) - 练习状态管理
- [stores/recommender.js](file:///e:\04_Interview_system\frontend\src\stores\recommender.js) - 推荐状态管理

#### 修改的文件
- [main.js](file:///e:\04_Interview_system\frontend\src\main.js) - 集成 Pinia
- [package.json](file:///e:\04_Interview_system\frontend\package.json) - 添加 Pinia 依赖

#### 功能特性
- 用户认证状态管理（登录、注册、登出）
- 题目数据缓存和状态管理
- 答题记录和统计
- 推荐系统状态管理
- 计算属性（completedCount, favoriteCount, unreadCount 等）

#### 使用示例
```javascript
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
await userStore.login('username', 'password')
console.log(userStore.user)
```

---

### 2. 修复数据库设计问题 ✅

#### 修改的文件
- [questions/models.py](file:///e:\04_Interview_system\backend\questions\models.py)
- [practice/models.py](file:///e:\04_Interview_system\backend\practice\models.py)
- [code_questions/models.py](file:///e:\04_Interview_system\backend\code_questions\models.py)

#### 主要改进

##### 2.1 继承软删除基类
所有模型现在继承 `SoftDeleteModel`，支持软删除功能：
- `is_deleted` 字段
- `deleted_at` 字段
- `soft_delete()` 方法
- `restore()` 方法
- `hard_delete()` 方法

##### 2.2 Category 模型增强
```python
class Category(SoftDeleteModel):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_full_path(self):
        # 获取完整分类路径
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return ' > '.join(path)
```

##### 2.3 Question 模型增强
```python
class Question(SoftDeleteModel):
    DIFFICULTY_CHOICES = [
        (1, '简单'),
        (2, '中等'),
        (3, '困难'),
        (4, '专家'),
    ]
    
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, db_index=True)
    content = models.TextField()
    answer = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='questions')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_questions')
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=1, db_index=True)
    is_approved = models.BooleanField(default=False, db_index=True)
    is_public = models.BooleanField(default=True, db_index=True)
    explanation = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    view_count = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    avg_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def update_avg_score(self, new_score):
        # 更新平均分
        total_score = self.avg_score * self.answer_count + new_score
        self.answer_count += 1
        self.avg_score = total_score / self.answer_count
        self.save(update_fields=['avg_score', 'answer_count'])
```

##### 2.4 Interaction 模型增强
```python
class Interaction(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='interactions')
    answer = models.TextField(blank=True)
    score = models.FloatField(null=True, db_index=True)
    time_spent = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False, db_index=True)
    is_favorite = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_MAP, default='viewed', db_index=True)
    scoring_method = models.CharField(max_length=50, blank=True, db_index=True)
    feedback = models.TextField(blank=True)
    attempts = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=['attempts'])
```

##### 2.5 CodeQuestion 模型增强
```python
class CodeQuestion(SoftDeleteModel):
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python', db_index=True)
    difficulty = models.IntegerField(default=1, db_index=True)
    tags = models.JSONField(default=list, blank=True)
    view_count = models.IntegerField(default=0)
    submission_count = models.IntegerField(default=0)
    acceptance_rate = models.FloatField(default=0.0)
    
    def increment_submission_count(self, passed=False):
        # 更新提交统计和通过率
        self.submission_count += 1
        if passed:
            total_passed = self.acceptance_rate * (self.submission_count - 1) + 1
            self.acceptance_rate = total_passed / self.submission_count
        else:
            total_passed = self.acceptance_rate * (self.submission_count - 1)
            self.acceptance_rate = total_passed / self.submission_count
        self.save(update_fields=['submission_count', 'acceptance_rate'])
```

##### 2.6 数据库索引优化
为所有模型添加了合理的数据库索引：
- 复合索引（如：user + is_submitted）
- 单字段索引（如：score, created_at）
- 唯一索引（如：slug）
- 相关名称优化（related_name）

---

### 3. 组件职责划分清楚，逐步拆分 ✅

#### 创建的文件
- [components/practice/QuestionHeader.vue](file:///e:\04_Interview_system\frontend\src\components\practice\QuestionHeader.vue)
- [components/practice/QuestionContent.vue](file:///e:\04_Interview_system\frontend\src\components\practice\QuestionContent.vue)
- [components/practice/AnswerInput.vue](file:///e:\04_Interview_system\frontend\src\components\practice\AnswerInput.vue)
- [components/practice/ScoreResult.vue](file:///e:\04_Interview_system\frontend\src\components\practice\ScoreResult.vue)
- [components/practice/PracticeDetailRefactored.vue](file:///e:\04_Interview_system\frontend\src\components\practice\PracticeDetailRefactored.vue)
- [COMPONENT_REFACTORING.md](file:///e:\04_Interview_system\frontend\COMPONENT_REFACTORING.md) - 组件重构文档

#### 组件职责划分

##### QuestionHeader.vue
**职责**：显示题目头部信息
- 标题显示
- 分类标签
- 难度标签
- 返回按钮

**Props**：
- `title`: 题目标题
- `category`: 分类对象
- `difficulty`: 难度等级

**Events**：
- `back`: 返回事件

##### QuestionContent.vue
**职责**：显示题目内容
- 题目描述
- 题目详细内容

**Props**：
- `title`: 题目标题
- `content`: 题目内容

##### AnswerInput.vue
**职责**：答案输入和评分方式选择
- 答案文本框
- 评分方式选择（嵌入模型、DeepSeek、两者平均）
- 提交按钮

**Props**：
- `answer`: 答案内容
- `showScoringMethod`: 是否显示评分方式选择
- `showSubmitButton`: 是否显示提交按钮
- `loading`: 加载状态

**Events**：
- `update:answer`: 答案更新事件
- `submit`: 提交事件

**Exposes**：
- `validate()`: 验证表单
- `reset()`: 重置表单

##### ScoreResult.vue
**职责**：显示评分结果
- 最终评分
- 评分星级
- 详细评分（嵌入模型、DeepSeek）
- 评分反馈

**Props**：
- `score`: 最终评分
- `embeddingScore`: 嵌入模型评分
- `deepseekScore`: DeepSeek 评分
- `feedback`: 评分反馈
- `showDetails`: 是否显示详细评分

##### PracticeDetailRefactored.vue
**职责**：答题详情页面容器
- 协调子组件
- 数据加载
- 业务逻辑处理

**使用示例**：
```vue
<template>
  <div class="practice-detail-container">
    <QuestionHeader
      :title="question.title"
      :category="question.category"
      :difficulty="question.difficulty"
      @back="goBack"
    />
    
    <QuestionContent
      :title="question.title"
      :content="question.content"
    />
    
    <AnswerInput
      v-if="!isSubmitted"
      :answer="form.answer"
      :loading="submitting"
      @update:answer="form.answer = $event"
      @submit="handleSubmit"
    />
    
    <ScoreResult
      v-if="isSubmitted"
      :score="form.score"
      :embedding-score="form.embeddingScore"
      :deepseek-score="form.deepseekScore"
      :feedback="interaction.feedback"
    />
  </div>
</template>
```

#### 组件拆分原则

1. **单一职责原则**
   - 每个组件只负责一个明确的功能
   - 避免组件过于复杂

2. **可复用性**
   - 将通用的 UI 元素提取为独立组件
   - 提高组件复用性

3. **Props 向下，Events 向上**
   - 数据通过 props 向下传递
   - 事件通过 events 向上冒泡

4. **组件通信**
   - 父子组件：props + events
   - 跨层级组件：provide/inject
   - 全局状态：Pinia stores
   - 复杂场景：Event Bus 或 Pinia actions

---

### 4. 评分逻辑修改为策略模式 ✅

#### 创建的文件
- [scoring/strategies.py](file:///e:\04_Interview_system\backend\scoring\strategies.py) - 策略抽象基类
- [scoring/embedding_strategy.py](file:///e:\04_Interview_system\backend\scoring\embedding_strategy.py) - 嵌入模型策略
- [scoring/llm_strategy.py](file:///e:\04_Interview_system\backend\scoring\llm_strategy.py) - LLM 策略
- [scoring/factory.py](file:///e:\04_Interview_system\backend\scoring\factory.py) - 策略工厂和上下文

#### 修改的文件
- [scoring/views.py](file:///e:\04_Interview_system\backend\scoring\views.py) - 使用策略模式重构

#### 策略模式架构

##### 4.1 策略抽象基类（ScoringStrategy）
```python
class ScoringStrategy(ABC):
    """
    评分策略抽象基类
    定义所有评分策略必须实现的接口
    """
    
    @abstractmethod
    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict[str, Any]:
        """
        计算评分
        
        Returns:
            {
                'score': float,  # 评分结果 (0-100)
                'details': dict,  # 评分详情
                'method': str  # 评分方法名称
            }
        """
        pass
    
    @abstractmethod
    def validate(self, user_answer: str, standard_answer: str) -> bool:
        """验证输入是否有效"""
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        """获取评分方法名称"""
        pass
```

##### 4.2 嵌入模型策略（EmbeddingScoringStrategy）
```python
class EmbeddingScoringStrategy(ScoringStrategy):
    """
    基于嵌入模型的评分策略
    使用句子嵌入计算语义相似度
    """
    
    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict[str, Any]:
        # 使用句子嵌入计算相似度
        model = self.get_model()
        
        # 预处理
        user_answer_processed = self.preprocess(user_answer)
        std_answer_processed = self.preprocess(standard_answer)
        
        # 计算嵌入
        user_embedding = model.encode(user_answer_processed)
        std_embedding = model.encode(std_answer_processed)
        
        # 余弦相似度
        cos_sim = util.cos_sim(user_embedding, std_embedding)[0][0].item()
        
        # 长度惩罚
        len_penalty = max(0.5, 1 - abs(len(user_answer_processed) - len(std_answer_processed)) / max(len(user_answer_processed), len(std_answer_processed), 1))
        
        # 调整相似度
        adjusted_sim = cos_sim * len_penalty
        
        # Sigmoid 映射
        sigmoid_score = 1 / (1 + math.exp(-6 * (adjusted_sim - 0.5)))
        
        # 标准化分数
        final_score = self.normalize_score(sigmoid_score * 100)
        
        return {
            'score': final_score,
            'details': {
                'cosine_similarity': float(cos_sim),
                'length_penalty': float(len_penalty),
                'adjusted_similarity': float(adjusted_sim),
                'sigmoid_score': float(sigmoid_score)
            },
            'method': self.get_method_name()
        }
```

##### 4.3 LLM 策略（LLMScoringStrategy）
```python
class LLMScoringStrategy(ScoringStrategy):
    """
    基于大语言模型的评分策略
    使用 DeepSeek API 进行智能评分
    """
    
    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict[str, Any]:
        # 构建 prompt
        prompt = self._build_prompt(
            question_title=kwargs.get('question_title'),
            user_answer=user_answer,
            standard_answer=standard_answer
        )
        
        # 调用 LLM API
        llm_output = self._call_llm_api(prompt)
        
        # 解析分数
        final_score = self._parse_score(llm_output)
        
        return {
            'score': final_score,
            'details': {
                'llm_output': llm_output,
                'model': self.model,
                'question_title': kwargs.get('question_title')
            },
            'method': self.get_method_name()
        }
```

##### 4.4 策略工厂（ScoringStrategyFactory）
```python
class ScoringStrategyFactory:
    """
    评分策略工厂类
    负责创建和管理评分策略实例
    """
    
    _strategies: Dict[str, Type[ScoringStrategy]] = {}
    _instances: Dict[str, ScoringStrategy] = {}
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[ScoringStrategy]):
        """注册评分策略"""
        cls._strategies[name] = strategy_class
    
    @classmethod
    def create_strategy(cls, name: str, **kwargs) -> ScoringStrategy:
        """创建评分策略实例"""
        if name not in cls._strategies:
            raise ValueError(f"Unknown scoring strategy: {name}")
        
        strategy_class = cls._strategies[name]
        return strategy_class(**kwargs)
    
    @classmethod
    def get_strategy(cls, name: str, **kwargs) -> ScoringStrategy:
        """获取评分策略实例（单例模式）"""
        if name not in cls._instances:
            cls._instances[name] = cls.create_strategy(name, **kwargs)
        return cls._instances[name]

# 注册默认策略
ScoringStrategyFactory.register_strategy('embedding', EmbeddingScoringStrategy)
ScoringStrategyFactory.register_strategy('llm', LLMScoringStrategy)
```

##### 4.5 评分上下文（ScoringContext）
```python
class ScoringContext:
    """
    评分上下文类
    负责协调评分策略的执行
    """
    
    def __init__(self, strategy_name: str = 'embedding'):
        self.strategy_name = strategy_name
        self._strategy = None
    
    def set_strategy(self, strategy_name: str):
        """设置评分策略"""
        self.strategy_name = strategy_name
        self._strategy = None
    
    def get_strategy(self) -> ScoringStrategy:
        """获取当前评分策略"""
        if self._strategy is None:
            self._strategy = ScoringStrategyFactory.get_strategy(self.strategy_name)
        return self._strategy
    
    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict:
        """执行评分"""
        strategy = self.get_strategy()
        return strategy.score(user_answer, standard_answer, **kwargs)
```

##### 4.6 视图层使用
```python
class ScoringViewSet(viewsets.ModelViewSet):
    """
    评分视图集（使用策略模式）
    """
    
    @action(detail=True, methods=['post'])
    def embedding_score(self, request, pk=None):
        """使用嵌入模型计算分数"""
        # 使用策略模式进行评分
        scorer = create_scorer('embedding')
        result = scorer.score(
            user_answer=interaction.answer,
            standard_answer=question.answer,
            question_id=question.id
        )
        
        # 保存评分历史
        ScoringHistory.objects.create(
            interaction=interaction,
            scoring_method=result['method'],
            score=result['score'],
            details=result['details']
        )
        
        return Response({
            'score': result['score'],
            'details': result['details'],
            'method': result['method']
        })
    
    @action(detail=True, methods=['post'])
    def llm_score(self, request, pk=None):
        """使用大语言模型计算分数"""
        # 使用策略模式进行评分
        scorer = create_scorer('llm')
        result = scorer.score(
            user_answer=interaction.answer,
            standard_answer=question.answer,
            question_title=question.title
        )
        
        return Response({
            'score': result['score'],
            'details': result['details'],
            'method': result['method']
        })
    
    @action(detail=False, methods=['get'])
    def list_strategies(self, request):
        """列出所有可用的评分策略"""
        strategies = ScoringStrategyFactory.list_strategies()
        return Response({
            'strategies': strategies,
            'count': len(strategies)
        })
```

#### 策略模式的优势

1. **开闭原则**
   - 对扩展开放：可以轻松添加新的评分策略
   - 对修改封闭：不需要修改现有代码

2. **单一职责**
   - 每个策略只负责一种评分方法
   - 代码更清晰、更易维护

3. **可替换性**
   - 运行时可以动态切换评分策略
   - 便于测试和调试

4. **可扩展性**
   - 添加新策略只需实现 ScoringStrategy 接口
   - 注册到工厂即可使用

#### 添加新评分策略示例

```python
# 1. 创建新策略类
class KeywordMatchingStrategy(ScoringStrategy):
    """
    基于关键词匹配的评分策略
    """
    
    def validate(self, user_answer: str, standard_answer: str) -> bool:
        return bool(user_answer and standard_answer)
    
    def get_method_name(self) -> str:
        return 'keyword'
    
    def score(self, user_answer: str, standard_answer: str, **kwargs) -> Dict[str, Any]:
        # 提取关键词
        keywords = self._extract_keywords(standard_answer)
        
        # 计算匹配度
        matched = sum(1 for kw in keywords if kw in user_answer)
        match_ratio = matched / len(keywords) if keywords else 0
        
        # 计算分数
        final_score = self.normalize_score(match_ratio * 100)
        
        return {
            'score': final_score,
            'details': {
                'keywords': keywords,
                'matched': matched,
                'match_ratio': match_ratio
            },
            'method': self.get_method_name()
        }

# 2. 注册策略
ScoringStrategyFactory.register_strategy('keyword', KeywordMatchingStrategy)

# 3. 使用新策略
scorer = create_scorer('keyword')
result = scorer.score(user_answer, standard_answer)
```

---

## 后续步骤

### 1. 安装依赖
```bash
cd frontend
npm install
```

### 2. 运行数据库迁移
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 3. 测试功能
- 测试 Pinia stores
- 测试新的数据库模型
- 测试拆分的组件
- 测试策略模式评分

### 4. 性能优化
- 监控数据库查询性能
- 优化组件渲染性能
- 添加缓存策略

### 5. 文档完善
- 组件使用文档
- API 文档
- 开发指南

---

## 总结

本次优化完成了以下四个主要任务：

1. ✅ **添加前端状态管理 Pinia**
   - 创建了 4 个核心 store
   - 实现了用户、题目、练习、推荐的状态管理
   - 提供了计算属性和便捷方法

2. ✅ **修复数据库设计问题**
   - 所有模型继承软删除基类
   - 添加了丰富的字段和索引
   - 实现了统计和计数方法
   - 优化了数据库查询性能

3. ✅ **组件职责划分清楚，逐步拆分**
   - 创建了 5 个职责单一的组件
   - 实现了组件拆分文档
   - 遵循了单一职责原则
   - 提高了组件复用性

4. ✅ **评分逻辑修改为策略模式**
   - 实现了策略抽象基类
   - 创建了嵌入模型和 LLM 两种策略
   - 实现了策略工厂和上下文
   - 支持动态切换和扩展新策略

所有任务均已成功完成，代码质量和可维护性得到了显著提升。
