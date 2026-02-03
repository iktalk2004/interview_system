<template>
  <div class="practice-container">
    <div class="page-header">
      <div class="header-content">
        <h1>答题练习</h1>
        <p>选择题目开始练习，提升你的技能</p>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <el-icon class="stat-icon"><Document /></el-icon>
          <span>{{ total }} 道题目</span>
        </div>
        <div class="stat-item">
          <el-icon class="stat-icon"><Check /></el-icon>
          <span>{{ completedCount }} 已完成</span>
        </div>
      </div>
    </div>

    <el-card class="filter-card">
      <el-form :model="filters" inline class="filter-form">
        <el-form-item>
          <el-input
            v-model="filters.search"
            placeholder="搜索题目..."
            clearable
            style="width: 240px"
            @clear="fetchQuestions"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-select
            v-model="filters.category"
            placeholder="选择分类"
            clearable
            style="width: 160px"
          >
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select
            v-model="filters.difficulty"
            placeholder="难度"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="(value, key) in difficultyMap"
              :key="key"
              :label="value"
              :value="key"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchQuestions">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetFilters">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="questions-card" v-loading="loading">
      <div v-if="questions.length === 0" class="empty-state">
        <el-empty description="暂无题目" />
      </div>
      <div v-else class="questions-grid">
        <div
          v-for="question in questions"
          :key="question.id"
          class="question-card"
          @click="goToPractice(question.id, null)"
        >
          <div class="question-header">
            <el-tag :type="getDifficultyType(question.difficulty)" size="small">
              {{ difficultyMap[question.difficulty] }}
            </el-tag>
            <el-tag v-if="question.category" type="info" size="small">
              {{ question.category.name }}
            </el-tag>
          </div>
          <div class="question-title">{{ question.title }}</div>
          <div class="question-footer">
            <div class="status-badge" :class="getStatusClass(question.id)">
              <el-icon><CircleCheck /></el-icon>
              <span>{{ getStatusText(question.id) }}</span>
            </div>
            <el-button
              v-if="getInteractionStatus(question.id)?.canRetry"
              size="small"
              type="warning"
              @click.stop="retryQuestion(question.id)"
            >
              <el-icon><RefreshRight /></el-icon>
              重新答题
            </el-button>
          </div>
        </div>
      </div>

      <div v-if="total > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          background
          layout="prev, pager, next, total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Document,
  Check,
  Search,
  Refresh,
  CircleCheck,
  RefreshRight
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const questions = ref([])
const categories = ref([])
const loading = ref(false)
const total = ref(0)
const pageSize = 12
const currentPage = ref(1)

const filters = reactive({
  search: '',
  category: null,
  difficulty: null
})

const difficultyMap = { 1: '易', 2: '中', 3: '难' }
const interactionStatusCache = ref({})

const completedCount = computed(() => {
  return Object.values(interactionStatusCache.value).filter(
    status => status.type === 'success'
  ).length
})

const filteredCategories = computed(() => {
  return categories.value.filter(cat => cat && cat.id && cat.name)
})

const fetchQuestions = async (page = 1) => {
  const pageNum = typeof page === 'number' ? page : parseInt(page) || 1
  loading.value = true
  try {
    const params = {
      search: filters.search,
      category: filters.category,
      difficulty: filters.difficulty,
      page: pageNum,
      page_size: pageSize
    }
    const response = await api.get('/questions/questions/', { params })
    questions.value = response.data.results || response.data
    total.value = response.data.count || questions.value.length
    currentPage.value = pageNum
    await updateInteractionStatus()
  } catch (err) {
    ElMessage.error('获取题目失败')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await api.get('/questions/categories/')
    categories.value = response.data.results || response.data
  } catch (err) {
    ElMessage.error('获取分类失败')
  }
}

const updateInteractionStatus = async () => {
  try {
    const questionIds = questions.value.map(q => q.id).join(',')
    const response = await api.get('/practice/interactions/', { params: { question__in: questionIds } })
    interactionStatusCache.value = {}
    response.data.forEach(int => {
      interactionStatusCache.value[int.question] = {
        type: int.score !== null ? 'success' : 'info',
        text: int.score !== null ? `已完成 (${int.score}分)` : '已开始',
        canRetry: int.score !== null
      }
    })
  } catch (err) {
    console.warn('状态更新失败')
  }
}

const getInteractionStatus = (questionId) => {
  return interactionStatusCache.value[questionId] || { type: 'primary', text: '未练习' }
}

const getStatusText = (questionId) => {
  return getInteractionStatus(questionId).text
}

const getStatusClass = (questionId) => {
  const status = getInteractionStatus(questionId)
  return `status-${status.type}`
}

const getDifficultyType = (difficulty) => {
  const map = { 1: 'success', 2: 'warning', 3: 'danger' }
  return map[difficulty] || 'info'
}

const goToPractice = (questionId, interactionId) => {
  router.push({
    name: 'PracticeDetail',
    params: { id: questionId },
    query: { interaction: interactionId }
  })
}

const retryQuestion = async (questionId) => {
  try {
    const response = await api.get('/practice/interactions/', { params: { question: questionId } })
    const interactions = Array.isArray(response.data) ? response.data : []
    if (interactions.length > 0) {
      const interaction = interactions[0]
      if (interaction.id) {
        const resetResponse = await api.post(`/practice/interactions/${interaction.id}/reset_interaction/`)
        ElMessage.success(resetResponse.data.message)
        goToPractice(questionId, interaction.id)
      }
    } else {
      ElMessage.error('找不到答题记录')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '重新答题失败')
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.category = null
  filters.difficulty = null
  fetchQuestions(1)
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchQuestions(page)
}

onMounted(() => {
  fetchQuestions()
  fetchCategories()
})
</script>

<style scoped>
.practice-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: #ffffff;
}

.header-content h1 {
  font-size: 32px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.header-content p {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
}

.header-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  opacity: 0.95;
}

.stat-icon {
  font-size: 20px;
}

.filter-card {
  margin-bottom: 20px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.filter-form {
  margin: 0;
}

.questions-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.empty-state {
  padding: 60px 0;
}

.questions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.question-card {
  background: #ffffff;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.question-card:hover {
  border-color: #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  transform: translateY(-4px);
}

.question-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.question-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.question-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 12px;
}

.status-success {
  background: #f0f9ff;
  color: #67c23a;
}

.status-info {
  background: #f4f4f5;
  color: #909399;
}

.status-primary {
  background: #ecf5ff;
  color: #409eff;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
    padding: 24px;
  }

  .header-stats {
    justify-content: center;
  }

  .questions-grid {
    grid-template-columns: 1fr;
  }

  .filter-form {
    flex-direction: column;
  }

  .filter-form :deep(.el-form-item) {
    width: 100%;
    margin-right: 0;
  }
}
</style>
