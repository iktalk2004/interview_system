<template>
  <div class="scoring-history-container">
    <div class="header">
      <h2>评分历史</h2>
      <div class="controls">
        <el-select v-model="filterMethod" placeholder="评分方法" clearable @change="fetchHistory">
          <el-option label="全部" value=""/>
          <el-option label="基于嵌入" value="embedding"/>
          <el-option label="基于LLM" value="llm"/>
          <el-option label="人工评分" value="manual"/>
        </el-select>
        <el-button type="primary" @click="fetchHistory" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else-if="scoringHistory.length === 0" class="empty-container">
      <el-empty description="暂无评分记录">
        <el-button type="primary" @click="goToPractice">开始答题</el-button>
      </el-empty>
    </div>

    <div v-else class="history-content">
      <el-card>
        <div class="stats-summary">
          <div class="stat-item">
            <div class="stat-value">{{ totalScores }}</div>
            <div class="stat-label">总评分次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ averageScore?.toFixed(1) || 0 }}</div>
            <div class="stat-label">平均分</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ highestScore?.toFixed(1) || 0 }}</div>
            <div class="stat-label">最高分</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ lowestScore?.toFixed(1) || 0 }}</div>
            <div class="stat-label">最低分</div>
          </div>
        </div>
      </el-card>

      <el-card style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>评分记录</span>
            <el-tag type="info">共 {{ scoringHistory.length }} 条</el-tag>
          </div>
        </template>

        <div class="history-list">
          <div
            v-for="item in scoringHistory"
            :key="item.id"
            class="history-item"
          >
            <div class="item-header">
              <div class="question-info">
                <el-icon><Document /></el-icon>
                <span class="question-title">{{ item.interaction_details.question_details.title }}</span>
              </div>
              <div class="score-badge" :class="getScoreClass(item.score)">
                {{ item.score?.toFixed(1) }}
              </div>
            </div>

            <div class="item-body">
              <div class="meta-info">
                <el-tag :type="getMethodTagType(item.scoring_method)" size="small">
                  {{ getMethodText(item.scoring_method) }}
                </el-tag>
                <span class="time">
                  <el-icon><Clock /></el-icon>
                  {{ formatTime(item.created_at) }}
                </span>
              </div>

              <div v-if="item.details" class="details-section">
                <el-collapse>
                  <el-collapse-item title="评分详情">
                    <div class="detail-content">
                      <div v-for="(value, key) in item.details" :key="key" class="detail-item">
                        <span class="detail-key">{{ formatKey(key) }}:</span>
                        <span class="detail-value">{{ formatValue(value) }}</span>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>

              <div class="user-answer">
                <div class="answer-label">用户答案：</div>
                <div class="answer-content">{{ item.interaction_details.answer }}</div>
              </div>
            </div>

            <div class="item-footer">
              <el-button
                type="primary"
                size="small"
                @click="goToQuestion(item.interaction_details.question_details.id)"
              >
                查看题目
              </el-button>
              <el-button
                size="small"
                @click="reScore(item.interaction_details.id, item.scoring_method)"
              >
                重新评分
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Loading, Document, Clock } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const loading = ref(false)
const filterMethod = ref('')
const scoringHistory = ref([])

const totalScores = computed(() => scoringHistory.value.length)

const averageScore = computed(() => {
  if (totalScores.value === 0) return 0
  const sum = scoringHistory.value.reduce((acc, item) => acc + (item.score || 0), 0)
  return sum / totalScores.value
})

const highestScore = computed(() => {
  if (totalScores.value === 0) return 0
  return Math.max(...scoringHistory.value.map(item => item.score || 0))
})

const lowestScore = computed(() => {
  if (totalScores.value === 0) return 0
  return Math.min(...scoringHistory.value.map(item => item.score || 0))
})

const fetchHistory = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterMethod.value) {
      params.method = filterMethod.value
    }

    const response = await api.get('/scoring/scoring/get_latest_scores/', {
      params: { limit: 50 }
    })

    let history = response.data

    if (filterMethod.value) {
      history = history.filter(item => item.scoring_method === filterMethod.value)
    }

    scoringHistory.value = history
  } catch (error) {
    console.error('获取评分历史失败:', error)
    ElMessage.error('获取评分历史失败')
  } finally {
    loading.value = false
  }
}

const reScore = async (interactionId, method) => {
  try {
    await ElMessageBox.confirm(
      '确定要重新评分吗？这将覆盖之前的评分结果。',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.post('/scoring/scoring/score_interaction/', {
      interaction_id: interactionId,
      method: method
    })

    ElMessage.success('重新评分成功')
    await fetchHistory()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重新评分失败:', error)
      ElMessage.error('重新评分失败')
    }
  }
}

const goToQuestion = (questionId) => {
  router.push(`/practice/${questionId}`)
}

const goToPractice = () => {
  router.push('/practice')
}

const getScoreClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 60) return 'pass'
  return 'fail'
}

const getMethodTagType = (method) => {
  const typeMap = {
    embedding: 'primary',
    llm: 'success',
    manual: 'warning'
  }
  return typeMap[method] || 'info'
}

const getMethodText = (method) => {
  const textMap = {
    embedding: '基于嵌入',
    llm: '基于LLM',
    manual: '人工评分'
  }
  return textMap[method] || method
}

const formatTime = (timeStr) => {
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

const formatKey = (key) => {
  const keyMap = {
    cosine_similarity: '余弦相似度',
    length_penalty: '长度惩罚',
    adjusted_similarity: '调整后相似度',
    sigmoid_score: 'Sigmoid分数',
    llm_output: 'LLM输出',
    model: '模型'
  }
  return keyMap[key] || key
}

const formatValue = (value) => {
  if (typeof value === 'number') {
    return value.toFixed(4)
  }
  return value
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.scoring-history-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0;
  color: #303133;
}

.controls {
  display: flex;
  gap: 10px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.empty-container {
  padding: 60px 0;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.history-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 15px;
  background: #fff;
  transition: all 0.3s;
}

.history-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.question-info {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.question-title {
  font-weight: bold;
  color: #303133;
  line-height: 1.5;
}

.score-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 18px;
  min-width: 60px;
  text-align: center;
}

.score-badge.excellent {
  background: #f0f9ff;
  color: #67c23a;
}

.score-badge.good {
  background: #ecf5ff;
  color: #409eff;
}

.score-badge.pass {
  background: #fdf6ec;
  color: #e6a23c;
}

.score-badge.fail {
  background: #fef0f0;
  color: #f56c6c;
}

.item-body {
  margin-bottom: 15px;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.time {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.details-section {
  margin-bottom: 15px;
}

.detail-content {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid #ebeef5;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-key {
  font-weight: bold;
  color: #606266;
}

.detail-value {
  color: #303133;
}

.user-answer {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.answer-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.answer-content {
  color: #303133;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.item-footer {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .stats-summary {
    grid-template-columns: repeat(2, 1fr);
  }

  .item-header {
    flex-direction: column;
    gap: 10px;
  }

  .item-footer {
    flex-direction: column;
  }

  .item-footer .el-button {
    width: 100%;
  }
}
</style>
