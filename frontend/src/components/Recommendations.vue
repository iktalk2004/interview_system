<template>
  <div class="recommendations-container">
    <div class="header">
      <h2>智能推荐</h2>
      <div class="controls">
        <el-select v-model="recommendationType" placeholder="推荐类型" @change="fetchRecommendations">
          <el-option label="混合推荐" value="hybrid"/>
          <el-option label="基于用户" value="user_based"/>
          <el-option label="基于物品" value="item_based"/>
        </el-select>
        <el-button type="primary" @click="fetchRecommendations" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新推荐
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>正在生成个性化推荐...</p>
    </div>

    <div v-else-if="recommendations.length === 0" class="empty-container">
      <el-empty description="暂无推荐题目">
        <el-button type="primary" @click="fetchRecommendations">生成推荐</el-button>
      </el-empty>
    </div>

    <div v-else class="recommendations-list">
      <div
        v-for="rec in recommendations"
        :key="rec.id"
        class="recommendation-card"
        :class="{ viewed: rec.is_viewed, answered: rec.is_answered }"
      >
        <div class="card-header">
          <div class="score-badge" :class="getScoreClass(rec.score)">
            {{ (rec.score * 100).toFixed(0) }}%
          </div>
          <el-tag :type="getTypeTagType(rec.recommendation_type)" size="small">
            {{ getTypeText(rec.recommendation_type) }}
          </el-tag>
        </div>

        <div class="card-body">
          <h3 class="question-title">{{ rec.question_details.title }}</h3>
          <div class="question-meta">
            <span class="meta-item">
              <el-icon><Document /></el-icon>
              {{ rec.question_details.category?.name || '未分类' }}
            </span>
            <span class="meta-item">
              <el-icon><Star /></el-icon>
              难度: {{ getDifficultyText(rec.question_details.difficulty) }}
            </span>
          </div>
          <div class="recommendation-reason">
            <el-icon><InfoFilled /></el-icon>
            <span>{{ rec.reason }}</span>
          </div>
        </div>

        <div class="card-footer">
          <el-button
            type="primary"
            @click="goToQuestion(rec.question_details.id)"
            :disabled="rec.is_answered"
          >
            {{ rec.is_answered ? '已答题' : '开始答题' }}
          </el-button>
          <el-button
            v-if="!rec.is_viewed"
            type="info"
            size="small"
            @click="markAsViewed(rec.id)"
          >
            标记已查看
          </el-button>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <el-card>
        <template #header>
          <span>推荐统计</span>
        </template>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总推荐数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.viewed }}</div>
            <div class="stat-label">已查看</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.answered }}</div>
            <div class="stat-label">已答题</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ stats.avg_score?.toFixed(1) || 0 }}</div>
            <div class="stat-label">平均推荐分数</div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Loading, Document, Star, InfoFilled } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const loading = ref(false)
const recommendationType = ref('hybrid')
const recommendations = ref([])

const stats = computed(() => {
  const total = recommendations.value.length
  const viewed = recommendations.value.filter(r => r.is_viewed).length
  const answered = recommendations.value.filter(r => r.is_answered).length
  const avgScore = total > 0
    ? recommendations.value.reduce((sum, r) => sum + r.score, 0) / total
    : 0

  return { total, viewed, answered, avg_score: avgScore }
})

const fetchRecommendations = async () => {
  loading.value = true
  try {
    const response = await api.get('/recommender/recommendations/generate_recommendations/', {
      params: {
        type: recommendationType.value,
        n: 10,
        min_similarity: 0.1
      }
    })

    recommendations.value = response.data.recommendations
    ElMessage.success(`成功生成 ${response.data.count} 条推荐`)
  } catch (error) {
    console.error('获取推荐失败:', error)
    ElMessage.error('获取推荐失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const markAsViewed = async (id) => {
  try {
    await api.post(`/recommender/recommendations/${id}/mark_viewed/`)
    const rec = recommendations.value.find(r => r.id === id)
    if (rec) {
      rec.is_viewed = true
    }
    ElMessage.success('已标记为查看')
  } catch (error) {
    console.error('标记失败:', error)
    ElMessage.error('标记失败')
  }
}

const goToQuestion = (questionId) => {
  router.push(`/practice/${questionId}`)
}

const getScoreClass = (score) => {
  if (score >= 0.8) return 'high'
  if (score >= 0.6) return 'medium'
  return 'low'
}

const getTypeTagType = (type) => {
  const typeMap = {
    hybrid: 'success',
    user_based: 'primary',
    item_based: 'warning'
  }
  return typeMap[type] || 'info'
}

const getTypeText = (type) => {
  const typeMap = {
    hybrid: '混合推荐',
    user_based: '基于用户',
    item_based: '基于物品'
  }
  return typeMap[type] || type
}

const getDifficultyText = (difficulty) => {
  const difficultyMap = { 1: '简单', 2: '中等', 3: '困难' }
  return difficultyMap[difficulty] || '未知'
}

onMounted(() => {
  fetchRecommendations()
})
</script>

<style scoped>
.recommendations-container {
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

.recommendations-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.recommendation-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
  transition: all 0.3s;
  position: relative;
}

.recommendation-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.recommendation-card.viewed {
  border-color: #c0c4cc;
  opacity: 0.8;
}

.recommendation-card.answered {
  border-color: #67c23a;
  background: #f0f9ff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.score-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 14px;
}

.score-badge.high {
  background: #f0f9ff;
  color: #67c23a;
}

.score-badge.medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.score-badge.low {
  background: #fef0f0;
  color: #f56c6c;
}

.card-body {
  margin-bottom: 15px;
}

.question-title {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #303133;
  line-height: 1.5;
}

.question-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  color: #909399;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.recommendation-reason {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  gap: 10px;
}

.stats-section {
  margin-top: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .recommendations-list {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
