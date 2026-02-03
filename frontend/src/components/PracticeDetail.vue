<template>
  <div class="practice-detail-container">
    <div class="page-header">
      <el-button @click="goBack" class="back-button" text>
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <div class="header-info">
        <h1>{{ question.title || '加载中...' }}</h1>
        <div class="meta-tags">
          <el-tag v-if="question.category" type="info" size="small">
            <el-icon><Folder /></el-icon>
            {{ question.category.name }}
          </el-tag>
          <el-tag :type="getDifficultyType(question.difficulty)" size="small">
            <el-icon><Star /></el-icon>
            {{ difficultyMap[question.difficulty] }}
          </el-tag>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading loading-icon"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="!question.id" class="empty-state">
      <el-empty description="题目不存在或加载失败" />
    </div>

    <div v-else class="content-wrapper">
      <div class="main-content">
        <el-card class="question-card">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Document /></el-icon>
              <span>题目描述</span>
            </div>
          </template>
          <div class="question-description">
            <p>{{ question.title }}</p>
          </div>
        </el-card>

        <el-card class="answer-card" v-if="interaction.score === null && !isSubmitted.value">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Edit /></el-icon>
              <span>你的答案</span>
            </div>
          </template>
          <el-form ref="answerFormRef" :model="form" label-position="top">
            <el-form-item prop="answer">
              <el-input
                v-model="form.answer"
                type="textarea"
                :rows="10"
                placeholder="请输入你的答案..."
                class="answer-input"
              />
            </el-form-item>
            <el-form-item label="评分方式" prop="scoringMethod">
              <el-radio-group v-model="form.scoringMethod" class="scoring-method-group">
                <el-radio value="embedding" border>
                  <el-icon><DataAnalysis /></el-icon>
                  嵌入模型
                </el-radio>
                <el-radio value="deepseek" border>
                  <el-icon><ChatDotRound /></el-icon>
                  DeepSeek
                </el-radio>
                <el-radio value="both" border>
                  <el-icon><TrendCharts /></el-icon>
                  两者平均
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="result-card" v-if="isSubmitted.value || interaction.score !== null">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><CircleCheck /></el-icon>
              <span>答题结果</span>
            </div>
          </template>

          <div v-if="interaction.score !== null" class="score-section">
            <div class="final-score">
              <div class="score-label">最终评分</div>
              <div class="score-value">{{ form.score }}</div>
              <el-rate v-model="form.score" disabled show-score text-color="#ff9900" score-template="{value}" />
            </div>

            <div class="detail-scores" v-if="form.scoringMethod === 'both' || form.scoringMethod === 'embedding'">
              <div class="detail-score-item">
                <div class="detail-label">嵌入模型评分</div>
                <div class="detail-value">{{ form.embeddingScore }}</div>
                <el-progress
                  :percentage="form.embeddingScore * 10"
                  :color="getScoreColor(form.embeddingScore)"
                  :stroke-width="8"
                />
              </div>
              <div class="detail-score-item" v-if="form.scoringMethod === 'both' || form.scoringMethod === 'deepseek'">
                <div class="detail-label">DeepSeek评分</div>
                <div class="detail-value">{{ form.deepseekScore }}</div>
                <el-progress
                  :percentage="form.deepseekScore * 10"
                  :color="getScoreColor(form.deepseekScore)"
                  :stroke-width="8"
                />
              </div>
            </div>
          </div>

          <div class="answer-section">
            <div class="section-title">
              <el-icon><ChatLineRound /></el-icon>
              你的答案
            </div>
            <div class="answer-content">{{ interaction.answer }}</div>
          </div>

          <div v-if="interaction.score !== null" class="correct-answer-section">
            <div class="section-title">
              <el-icon><Select /></el-icon>
              正确答案
            </div>
            <div class="answer-content correct">{{ question.answer }}</div>
          </div>
        </el-card>
      </div>

      <div class="sidebar">
        <el-card class="timer-card">
          <template #header>
            <div class="card-header">
              <el-icon class="header-icon"><Clock /></el-icon>
              <span>答题时长</span>
            </div>
          </template>
          <div class="timer-display">
            <div class="time-value">{{ formatTime(timeSpent) }}</div>
            <div class="time-label">已用时</div>
          </div>
        </el-card>

        <el-card class="action-card">
          <div class="action-buttons">
            <el-button
              v-if="interaction.score === null && !isSubmitted.value"
              type="primary"
              size="large"
              :loading="submitting"
              @click="submitAnswer"
              class="submit-button"
            >
              <el-icon><Check /></el-icon>
              提交答案
            </el-button>
            <el-button
              v-if="interaction.score !== null"
              type="warning"
              size="large"
              @click="resetAndRetry"
              class="retry-button"
            >
              <el-icon><RefreshRight /></el-icon>
              重新答题
            </el-button>
            <el-button
              :type="interaction.is_favorite ? 'danger' : 'default'"
              size="large"
              @click="toggleFavorite"
              class="favorite-button"
            >
              <el-icon><Star /></el-icon>
              {{ interaction.is_favorite ? '取消收藏' : '收藏题目' }}
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { debounce } from 'lodash'
import {
  ArrowLeft,
  Document,
  Edit,
  CircleCheck,
  Clock,
  Loading,
  Folder,
  Star,
  DataAnalysis,
  ChatDotRound,
  TrendCharts,
  ChatLineRound,
  Select,
  Check,
  RefreshRight
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const route = useRoute()

const questionId = route.params.id
const hasMeaningfulAction = ref(false)
const isSubmitted = ref(false)
const interactionIdQuery = route.query.interaction

const question = ref({})
const interaction = reactive({
  id: null,
  score: null,
  answer: '',
  is_favorite: false,
  time_spent: 0,
  is_submitted: false
})

const form = reactive({
  answer: '',
  score: null,
  embeddingScore: null,
  deepseekScore: null,
  scoringMethod: 'embedding'
})

const loading = ref(true)
const submitting = ref(false)
const timeSpent = ref(0)
let timerInterval = null

const difficultyMap = { 1: '易', 2: '中', 3: '难' }

const getDifficultyType = (difficulty) => {
  const map = { 1: 'success', 2: 'warning', 3: 'danger' }
  return map[difficulty] || 'info'
}

const getScoreColor = (score) => {
  if (score >= 8) return '#67c23a'
  if (score >= 6) return '#e6a23c'
  return '#f56c6c'
}

const formatTime = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }
  return `${minutes}:${String(secs).padStart(2, '0')}`
}

const loadData = async () => {
  if (!questionId) {
    ElMessage.error('题目ID不能为空')
    goBack()
    return
  }

  loading.value = true
  try {
    const qResponse = await api.get(`/questions/questions/${questionId}/`)
    question.value = qResponse.data.results || qResponse.data

    let iResponse
    if (interactionIdQuery) {
      iResponse = await api.get(`/practice/interactions/${interactionIdQuery}/`)
    } else {
      iResponse = await api.get('/practice/interactions/', { params: { question: questionId } })
      if (Array.isArray(iResponse.data) && iResponse.data.length > 0) {
        iResponse = { data: iResponse.data[0] }
      } else if (!Array.isArray(iResponse.data)) {
        iResponse = iResponse
      } else {
        iResponse = { data: { id: null, score: null, answer: '', time_spent: 0, is_favorite: false, is_submitted: false } }
      }
    }

    Object.assign(interaction, iResponse.data)
    form.answer = interaction.answer || ''
    form.score = interaction.score
    timeSpent.value = interaction.time_spent || 0
    isSubmitted.value = interaction.is_submitted || false

    interaction.status = iResponse.data.status || ''
    if (interaction.status === 'viewed') {
      timeSpent.value = 0
    }

    if (interaction.score === undefined) interaction.score = null

    if (interaction.score === null) startTimer()

    if (interaction.id) hasMeaningfulAction.value = true
  } catch (err) {
    console.error('加载失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '加载失败')
    goBack()
  } finally {
    loading.value = false
  }
}

const saveViewRecord = async () => {
  const data = {
    question: questionId,
    time_spent: timeSpent.value,
    is_submitted: false,
    status: 'viewed'
  }

  try {
    await api.post('/practice/interactions/', data)
  } catch (err) {
    console.error('保存浏览记录失败:', err)
  }
}

watch(() => form.answer, debounce(async (newVal) => {
  if (newVal && !isSubmitted.value) {
    hasMeaningfulAction.value = true
    await saveDraft()
  }
}, 3000))

const submitAnswer = async () => {
  if (!form.answer) {
    ElMessage.warning('请输入答案')
    return
  }
  if (!form.scoringMethod) {
    ElMessage.warning('请选择评分方式')
    return
  }

  submitting.value = true
  stopTimer()

  const data = {
    question: questionId,
    answer: form.answer,
    time_spent: timeSpent.value,
    is_submitted: true
  }

  try {
    let response
    if (interaction.id) {
      response = await api.patch(`/practice/interactions/${interaction.id}/`, data)
    } else {
      response = await api.post('/practice/interactions/', data)
      interaction.id = response.data.id
    }
    Object.assign(interaction, response.data)
    isSubmitted.value = true
    hasMeaningfulAction.value = true
    ElMessage.success('答案提交成功')

    await getScoreByMethod()
  } catch (err) {
    console.error('提交失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

const resetAndRetry = async () => {
  if (!interaction.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  try {
    const response = await api.post(`/practice/interactions/${interaction.id}/reset_interaction/`)
    ElMessage.success(response.data.message)

    form.answer = ''
    form.score = null
    form.embeddingScore = null
    form.deepseekScore = null
    interaction.score = null
    interaction.answer = ''
    interaction.is_submitted = false
    interaction.status = 'draft'
    isSubmitted.value = false

    startTimer()
    hasMeaningfulAction.value = true

  } catch (err) {
    console.error('重置失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '重置失败')
  }
}

const saveDraft = async () => {
  if (!form.answer) return

  const data = {
    question: questionId,
    answer: form.answer,
    time_spent: timeSpent.value,
    is_submitted: false,
    status: 'draft'
  }

  try {
    let response
    if (interaction.id) {
      response = await api.patch(`/practice/interactions/${interaction.id}/`, data)
    } else {
      response = await api.post('/practice/interactions/', data)
      interaction.id = response.data.id
    }
    Object.assign(interaction, response.data)
  } catch (err) {
    console.error('保存草稿失败:', err)
  }
}

const getScoreByMethod = async () => {
  if (!interaction.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  if (!interaction.answer) {
    ElMessage.warning('请先提交答案')
    return
  }

  try {
    form.embeddingScore = null
    form.deepseekScore = null
    form.score = null

    if (form.scoringMethod === 'embedding' || form.scoringMethod === 'both') {
      const embeddingResponse = await api.post(`/practice/interactions/${interaction.id}/embedding_score/`)
      form.embeddingScore = embeddingResponse.data.score
    }

    if (form.scoringMethod === 'deepseek' || form.scoringMethod === 'both') {
      const deepseekResponse = await api.post(`/practice/interactions/${interaction.id}/deepseek_score/`)
      form.deepseekScore = deepseekResponse.data.score
    }

    if (form.scoringMethod === 'both') {
      let finalScore = Math.round((form.embeddingScore + form.deepseekScore) / 2 * 10) / 10
      if (finalScore >= 95) {
        finalScore = 100
      }
      form.score = finalScore
      interaction.score = finalScore
    } else if (form.scoringMethod === 'embedding') {
      form.score = form.embeddingScore
      interaction.score = form.embeddingScore
    } else if (form.scoringMethod === 'deepseek') {
      form.score = form.deepseekScore
      interaction.score = form.deepseekScore
    }

    await api.patch(`/practice/interactions/${interaction.id}/`, { score: form.score })
  } catch (err) {
    console.error('评分失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '评分失败')
  }
}

const toggleFavorite = async () => {
  if (!interaction.id) {
    ElMessage.error('交互ID不存在')
    return
  }

  try {
    const response = await api.post(`/practice/interactions/${interaction.id}/favorite/`)
    interaction.is_favorite = response.data.is_favorite
    ElMessage.success(response.data.is_favorite ? '收藏成功' : '取消收藏')
  } catch (err) {
    console.error('操作失败:', err)
    ElMessage.error(err.response?.data?.message || err.message || '操作失败')
  }
}

const goBack = () => {
  stopTimer()
  router.push({ name: 'Practice' })
}

const startTimer = () => {
  timerInterval = setInterval(() => timeSpent.value++, 1000)
}

const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

onUnmounted(() => {
  stopTimer()
  if (hasMeaningfulAction.value) {
  } else if (timeSpent.value > 10 && !form.answer.trim() && !isSubmitted.value) {
    saveViewRecord()
  }
})

onMounted(loadData)
</script>

<style scoped>
.practice-detail-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 0;
}

.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px 32px;
  display: flex;
  align-items: center;
  gap: 24px;
  color: #ffffff;
}

.back-button {
  color: #ffffff;
  font-size: 16px;
  padding: 8px 16px;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.header-info {
  flex: 1;
}

.header-info h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.meta-tags {
  display: flex;
  gap: 12px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: #909399;
}

.loading-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state {
  padding: 80px 0;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  padding: 24px 32px;
  max-width: 1600px;
  margin: 0 auto;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-card,
.answer-card,
.result-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.header-icon {
  font-size: 20px;
  color: #667eea;
}

.question-description {
  line-height: 1.8;
  color: #303133;
  font-size: 16px;
}

.answer-input :deep(.el-textarea__inner) {
  font-size: 15px;
  line-height: 1.6;
  border-radius: 8px;
}

.scoring-method-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.scoring-method-group :deep(.el-radio) {
  margin-right: 0;
}

.score-section {
  margin-bottom: 24px;
}

.final-score {
  text-align: center;
  padding: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #ffffff;
  margin-bottom: 24px;
}

.score-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.score-value {
  font-size: 64px;
  font-weight: 700;
  margin-bottom: 16px;
}

.detail-scores {
  display: grid;
  gap: 16px;
}

.detail-score-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.detail-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.answer-section,
.correct-answer-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.answer-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}

.answer-content.correct {
  background: #f0f9ff;
  color: #67c23a;
  border-left: 4px solid #67c23a;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.timer-card,
.action-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.timer-display {
  text-align: center;
  padding: 24px 0;
}

.time-value {
  font-size: 48px;
  font-weight: 700;
  color: #667eea;
  font-family: 'Courier New', monospace;
  margin-bottom: 8px;
}

.time-label {
  font-size: 14px;
  color: #909399;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-buttons .el-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
}

.submit-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.submit-button:hover {
  background: linear-gradient(135deg, #5568d3 0%, #643a8f 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.retry-button {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: none;
  color: #ffffff;
}

.retry-button:hover {
  background: linear-gradient(135deg, #e082ea 0%, #e4465b 100%);
  transform: translateY(-2px);
}

.favorite-button {
  border: 2px solid #667eea;
  color: #667eea;
}

.favorite-button:hover {
  background: #667eea;
  color: #ffffff;
  transform: translateY(-2px);
}

@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    padding: 16px;
  }

  .sidebar {
    order: -1;
  }

  .timer-card,
  .action-card {
    display: none;
  }

  .page-header {
    padding: 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-info h1 {
    font-size: 20px;
  }
}
</style>
