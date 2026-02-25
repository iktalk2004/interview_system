# 前端组件重构说明

## 组件职责划分

### 1. 公共组件 (components/common/)

#### LoadingSpinner.vue
- 职责：显示加载状态
- Props: loading, text
- Events: 无

#### EmptyState.vue
- 职责：显示空状态
- Props: description, icon
- Events: 无

#### ErrorState.vue
- 职责：显示错误状态
- Props: message, actionText
- Events: retry

### 2. 题目练习组件 (components/practice/)

#### QuestionHeader.vue
- 职责：显示题目头部信息（标题、分类、难度）
- Props: title, category, difficulty
- Events: back

#### QuestionContent.vue
- 职责：显示题目内容
- Props: title, content
- Events: 无

#### AnswerInput.vue
- 职责：答案输入和评分方式选择
- Props: answer, showScoringMethod, showSubmitButton, loading
- Events: update:answer, submit
- Exposes: validate(), reset()

#### ScoreResult.vue
- 职责：显示评分结果
- Props: score, embeddingScore, deepseekScore, feedback, showDetails
- Events: 无

#### PracticeDetailRefactored.vue
- 职责：答题详情页面容器，协调子组件
- Props: 无
- Events: 无

### 3. 代码练习组件 (components/code/)

#### CodeEditor.vue
- 职责：代码编辑器
- Props: code, language, readonly
- Events: update:code, change

#### TestCaseList.vue
- 职责：显示测试用例列表
- Props: testCases, showHidden
- Events: run-test

#### CodeSubmissionResult.vue
- 职责：显示代码提交结果
- Props: status, runtime, memory, passed, total
- Events: 无

### 4. 用户相关组件 (components/user/)

#### UserAvatar.vue
- 职责：用户头像
- Props: user, size
- Events: click

#### UserStats.vue
- 职责：用户统计信息
- Props: stats
- Events: 无

#### UserMenu.vue
- 职责：用户菜单
- Props: user
- Events: logout, profile

### 5. 布局组件 (components/layout/)

#### NavBar.vue
- 职责：导航栏
- Props: user
- Events: login, logout

#### Footer.vue
- 职责：页脚
- Props: 无
- Events: 无

#### Sidebar.vue
- 职责：侧边栏
- Props: menuItems, collapsed
- Events: select

### 6. 业务组件 (components/business/)

#### QuestionList.vue
- 职责：题目列表
- Props: questions, loading, filters
- Events: filter, select

#### RecommendationCard.vue
- 职责：推荐卡片
- Props: recommendation
- Events: view, answer

#### Leaderboard.vue
- 职责：排行榜
- Props: users, loading
- Events: 无

#### AnalyticsChart.vue
- 职责：数据可视化图表
- Props: chartData, chartType
- Events: 无

## 组件拆分原则

### 单一职责原则
每个组件只负责一个明确的功能，避免组件过于复杂。

### 可复用性
将通用的 UI 元素提取为独立组件，提高复用性。

### Props 向下，Events 向上
数据通过 props 向下传递，事件通过 events 向上冒泡。

### 组件通信
- 父子组件：props + events
- 跨层级组件：provide/inject
- 全局状态：Pinia stores
- 复杂场景：Event Bus 或 Pinia actions

### 组件生命周期
合理使用 onMounted, onUpdated, onUnmounted 等生命周期钩子。

### 性能优化
- 使用 v-show 替代 v-if（频繁切换）
- 使用 computed 缓存计算结果
- 使用 v-once 静态内容
- 合理使用 key 属性

## 迁移计划

### 阶段一：创建基础组件（已完成）
- [x] QuestionHeader.vue
- [x] QuestionContent.vue
- [x] AnswerInput.vue
- [x] ScoreResult.vue
- [x] PracticeDetailRefactored.vue

### 阶段二：拆分现有组件
- [ ] 拆分 Practice.vue
- [ ] 拆分 Dashboard.vue
- [ ] 拆分 Analytics.vue
- [ ] 拆分 CodePractice.vue
- [ ] 拆分 CodePracticeDetail.vue

### 阶段三：创建公共组件
- [ ] LoadingSpinner.vue
- [ ] EmptyState.vue
- [ ] ErrorState.vue
- [ ] UserAvatar.vue
- [ ] UserStats.vue

### 阶段四：优化和测试
- [ ] 组件单元测试
- [ ] 性能优化
- [ ] 文档完善
- [ ] 示例代码

## 使用示例

### QuestionHeader.vue
```vue
<QuestionHeader
  :title="question.title"
  :category="question.category"
  :difficulty="question.difficulty"
  @back="goBack"
/>
```

### AnswerInput.vue
```vue
<AnswerInput
  :answer="form.answer"
  :loading="submitting"
  @update:answer="form.answer = $event"
  @submit="handleSubmit"
/>
```

### ScoreResult.vue
```vue
<ScoreResult
  :score="form.score"
  :embedding-score="form.embeddingScore"
  :deepseek-score="form.deepseekScore"
  :feedback="interaction.feedback"
/>
```

## 注意事项

1. **组件命名**：使用 PascalCase，语义化命名
2. **Props 类型**：明确定义 props 类型
3. **Events 命名**：使用 kebab-case
4. **样式隔离**：使用 scoped 样式
5. **性能考虑**：避免不必要的重渲染
6. **错误处理**：合理的错误提示和边界处理
7. **可访问性**：考虑无障碍访问
