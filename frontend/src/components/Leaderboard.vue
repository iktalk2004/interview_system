<template>
  <div class="leaderboard-container">
    <div class="header">
      <h2>排行榜</h2>
      <el-radio-group v-model="leaderboardType" @change="fetchLeaderboard">
        <el-radio-button value="score">按分数排名</el-radio-button>
        <el-radio-button value="count">按答题数排名</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else class="leaderboard-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="12">
          <el-card class="leaderboard-card">
            <template #header>
              <div class="card-header">
                <el-icon><Trophy /></el-icon>
                <span>按平均分排名</span>
              </div>
            </template>

            <div v-if="topByScore.length === 0" class="empty-state">
              <el-empty description="暂无数据" />
            </div>

            <div v-else class="leaderboard-list">
              <div
                v-for="(user, index) in topByScore"
                :key="user.id"
                class="leaderboard-item"
                :class="{ 'is-current-user': user.user_details.id === currentUserId }"
              >
                <div class="rank" :class="getRankClass(index)">
                  {{ index + 1 }}
                </div>
                <div class="user-info">
                  <div class="username">{{ user.user_details.username }}</div>
                  <div class="user-bio">{{ user.user_details.bio || '暂无简介' }}</div>
                </div>
                <div class="score-info">
                  <div class="score">{{ user.average_score?.toFixed(1) }}</div>
                  <div class="label">平均分</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-card class="leaderboard-card">
            <template #header>
              <div class="card-header">
                <el-icon><Medal /></el-icon>
                <span>按答题数排名</span>
              </div>
            </template>

            <div v-if="topByCount.length === 0" class="empty-state">
              <el-empty description="暂无数据" />
            </div>

            <div v-else class="leaderboard-list">
              <div
                v-for="(user, index) in topByCount"
                :key="user.id"
                class="leaderboard-item"
                :class="{ 'is-current-user': user.user_details.id === currentUserId }"
              >
                <div class="rank" :class="getRankClass(index)">
                  {{ index + 1 }}
                </div>
                <div class="user-info">
                  <div class="username">{{ user.user_details.username }}</div>
                  <div class="user-bio">{{ user.user_details.bio || '暂无简介' }}</div>
                </div>
                <div class="score-info">
                  <div class="score">{{ user.total_questions_answered }}</div>
                  <div class="label">答题数</div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="my-rank-card" v-if="myRank">
        <template #header>
          <div class="card-header">
            <el-icon><User /></el-icon>
            <span>我的排名</span>
          </div>
        </template>

        <div class="my-rank-content">
          <div class="rank-item">
            <span class="rank-label">平均分排名：</span>
            <span class="rank-value" :class="getRankClass(myRank.scoreRank - 1)">
              第 {{ myRank.scoreRank }} 名
            </span>
          </div>
          <div class="rank-item">
            <span class="rank-label">答题数排名：</span>
            <span class="rank-value" :class="getRankClass(myRank.countRank - 1)">
              第 {{ myRank.countRank }} 名
            </span>
          </div>
          <div class="rank-item">
            <span class="rank-label">平均分：</span>
            <span class="rank-value score-high">{{ myRank.average_score?.toFixed(1) }}</span>
          </div>
          <div class="rank-item">
            <span class="rank-label">答题数：</span>
            <span class="rank-value">{{ myRank.total_questions_answered }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Trophy, Medal, User } from '@element-plus/icons-vue'
import api from '@/api'

const loading = ref(false)
const leaderboardType = ref('score')
const topByScore = ref([])
const topByCount = ref([])
const myRank = ref(null)

const currentUserId = computed(() => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr).id : null
})

const fetchLeaderboard = async () => {
  loading.value = true
  try {
    const response = await api.get('/analytics/dashboard/leaderboard/')
    topByScore.value = response.data.top_by_score
    topByCount.value = response.data.top_by_count

    findMyRank()
  } catch (error) {
    console.error('获取排行榜失败:', error)
    ElMessage.error('获取排行榜失败')
  } finally {
    loading.value = false
  }
}

const findMyRank = () => {
  if (!currentUserId.value) return

  const scoreRank = topByScore.value.findIndex(
    u => u.user_details.id === currentUserId.value
  )

  const countRank = topByCount.value.findIndex(
    u => u.user_details.id === currentUserId.value
  )

  if (scoreRank !== -1 || countRank !== -1) {
    myRank.value = {
      scoreRank: scoreRank + 1,
      countRank: countRank + 1,
      average_score: topByScore.value[scoreRank]?.average_score || 0,
      total_questions_answered: topByCount.value[countRank]?.total_questions_answered || 0
    }
  }
}

const getRankClass = (index) => {
  if (index === 0) return 'rank-1'
  if (index === 1) return 'rank-2'
  if (index === 2) return 'rank-3'
  return 'rank-other'
}

onMounted(() => {
  fetchLeaderboard()
})
</script>

<style scoped>
.leaderboard-container {
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

.leaderboard-content {
  margin-bottom: 30px;
}

.leaderboard-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: bold;
}

.empty-state {
  padding: 40px 0;
}

.leaderboard-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.leaderboard-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  background: #f5f7fa;
  transition: all 0.3s;
}

.leaderboard-item:hover {
  background: #e4e7ed;
  transform: translateX(5px);
}

.leaderboard-item.is-current-user {
  background: #ecf5ff;
  border: 2px solid #409eff;
}

.rank {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  margin-right: 15px;
  flex-shrink: 0;
}

.rank.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffec8b);
  color: #fff;
  box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3);
}

.rank.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
  color: #fff;
  box-shadow: 0 4px 8px rgba(192, 192, 192, 0.3);
}

.rank.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #e6a86c);
  color: #fff;
  box-shadow: 0 4px 8px rgba(205, 127, 50, 0.3);
}

.rank.rank-other {
  background: #dcdfe6;
  color: #606266;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.user-bio {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.score-info {
  text-align: center;
  min-width: 80px;
}

.score {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 4px;
}

.label {
  font-size: 12px;
  color: #909399;
}

.my-rank-card {
  margin-top: 20px;
}

.my-rank-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 20px 0;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rank-label {
  color: #606266;
  font-size: 14px;
}

.rank-value {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}

.rank-value.score-high {
  color: #67c23a;
}

.rank-value.rank-1 {
  color: #e6a23c;
}

.rank-value.rank-2 {
  color: #f56c6c;
}

.rank-value.rank-3 {
  color: #909399;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .my-rank-content {
    grid-template-columns: 1fr;
  }

  .leaderboard-item {
    padding: 10px;
  }

  .rank {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }

  .score {
    font-size: 20px;
  }
}
</style>
