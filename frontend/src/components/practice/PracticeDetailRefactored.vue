<template>
  <div class="practice-detail-container">
    <QuestionHeader
      :title="question.title"
      :category="question.category"
      :difficulty="question.difficulty"
      @back="goBack"
    />

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading loading-icon"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="!question.id" class="empty-state">
      <el-empty description="题目不存在或加载失败" />
    </div>

    <div v-else class="content-wrapper">
      <div class="main-content">
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
          v-if="isSubmitted || interaction.score !== null"
          :score="form.score"
          :embedding-score="form.embeddingScore"
          :deepseek-score="form.deepseekScore"
          :feedback="interaction.feedback"
        />
      </div>

      <div class="sidebar">
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>题目信息</span>
            </div>
          </template>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">创建者</span>
              <span class="info-value">{{ question.creator?.username || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDate(question.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">浏览次数</span>
              <span class="info-value">{{ question.view_count || 0 }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">答题次数</span>
              <span class="info-value">{{ question.answer_count || 0 }}</span>
            </div>
          </div>
        </el-card>

        <el-card class="actions-card">
          <template #header>
            <div class="card-header">
              <el-icon><Operation /></el-icon>
              <span>操作</span>
            </div>
          </template>
          <div class="action-buttons">
            <el-button
              type="primary"
              @click="toggleFavorite"
              :icon="interaction.is_favorite ? StarFilled : Star"
            >
              {{ interaction.is_favorite ? '已收藏' : '收藏' }}
            </el-button>
            <el-button
              v-if="isSubmitted"
              @click="resetAnswer"
              :icon="Refresh"
            >
              重新答题
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, InfoFilled, Operation, Star, StarFilled, Refresh } from '@element-plus/icons-vue'
import QuestionHeader from './QuestionHeader.vue'
import QuestionContent from './QuestionContent.vue'
import AnswerInput from './AnswerInput.vue'
import ScoreResult from './ScoreResult.vue'
import api from '../api'

const route = useRoute()
const router = useRouter()

const question = ref({})
const interaction = ref({})
const loading = ref(true)
const submitting = ref(false)

const form = ref({
  answer: '',
  scoringMethod: 'embedding',
  score: null,
  embeddingScore: null,
  deepseekScore: null
})

const isSubmitted = computed(() => interaction.value.is_submitted || interaction.value.score !== null)

onMounted(async () => {
  await loadQuestion()
  await loadInteraction()
})

async function loadQuestion() {
  try {
    const response = await api.get(`questions/${route.params.id}/`)
    question.value = response.data
  } catch (error) {
    ElMessage.error('加载题目失败')
  } finally {
    loading.value = false
  }
}

async function loadInteraction() {
  try {
    const response = await api.get(`practice/interactions/`, {
      params: { question: route.params.id }
    })
    if (response.data.results && response.data.results.length > 0) {
      interaction.value = response.data.results[0]
      form.value.answer = interaction.value.answer || ''
      form.value.score = interaction.value.score
    } else {
      interaction.value = {}
    }
  } catch (error) {
    console.error('加载答题记录失败:', error)
  }
}

async function handleSubmit(data) {
  submitting.value = true
  try {
    let score = 0
    let embeddingScore = null
    let deepseekScore = null

    if (data.scoringMethod === 'embedding' || data.scoringMethod === 'both') {
      const embeddingResponse = await api.post(`practice/interactions/${interaction.value.id}/embedding_score/`)
      embeddingScore = embeddingResponse.data.score
      score = embeddingScore
    }

    if (data.scoringMethod === 'deepseek' || data.scoringMethod === 'both') {
      const deepseekResponse = await api.post(`practice/interactions/${interaction.value.id}/deepseek_score/`)
      deepseekScore = deepseekResponse.data.score
      if (data.scoringMethod === 'deepseek') {
        score = deepseekScore
      } else if (data.scoringMethod === 'both') {
        score = (embeddingScore + deepseekScore) / 2
      }
    }

    form.value.score = score
    form.value.embeddingScore = embeddingScore
    form.value.deepseekScore = deepseekScore

    await api.put(`practice/interactions/${interaction.value.id}/`, {
      answer: data.answer,
      is_submitted: true,
      score: score
    })

    interaction.value.is_submitted = true
    interaction.value.score = score

    ElMessage.success('提交成功！')
  } catch (error) {
    ElMessage.error('提交失败：' + (error.response?.data?.error || error.message))
  } finally {
    submitting.value = false
  }
}

async function toggleFavorite() {
  try {
    await api.post(`practice/interactions/${interaction.value.id}/favorite/`)
    interaction.value.is_favorite = !interaction.value.is_favorite
    ElMessage.success(interaction.value.is_favorite ? '已收藏' : '已取消收藏')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function resetAnswer() {
  try {
    await api.post(`practice/interactions/${interaction.value.id}/reset_interaction/`)
    interaction.value.is_submitted = false
    interaction.value.score = null
    form.value.answer = ''
    form.value.score = null
    form.value.embeddingScore = null
    form.value.deepseekScore = null
    ElMessage.success('已重置')
  } catch (error) {
    ElMessage.error('重置失败')
  }
}

function goBack() {
  router.back()
}

function formatDate(dateString) {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.practice-detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  text-align: center;
  padding: 100px 0;
}

.loading-icon {
  font-size: 48px;
  color: #61dafb;
}

.empty-state {
  padding: 100px 0;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
}

.main-content {
  min-width: 0;
}

.sidebar {
  position: sticky;
  top: 20px;
  height: fit-content;
}

.info-card,
.actions-card {
  margin-bottom: 20px;
  background: #1e1e1e;
  border: 1px solid #3c3c3c;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #3c3c3c;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: #909399;
  font-size: 14px;
}

.info-value {
  color: #e0e0e0;
  font-size: 14px;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-buttons .el-button {
  width: 100%;
}

@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }
}
</style>
