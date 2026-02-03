<template>
  <div class="analytics-container">
    <div class="header">
      <h2>数据分析</h2>
      <el-button type="primary" @click="refreshData" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>加载数据中...</p>
    </div>

    <div v-else class="analytics-content">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userStats.total_questions_answered || 0 }}</div>
                <div class="stat-label">总答题数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon score">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userStats.average_score?.toFixed(1) || 0 }}</div>
                <div class="stat-label">平均分数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon time">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ formatTime(userStats.total_time_spent) }}</div>
                <div class="stat-label">总用时</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon favorite">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userStats.favorite_count || 0 }}</div>
                <div class="stat-label">收藏数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :xs="24" :md="16">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>每日答题趋势</span>
                <el-radio-group v-model="chartPeriod" size="small" @change="updateCharts">
                  <el-radio-button value="7">近7天</el-radio-button>
                  <el-radio-button value="30">近30天</el-radio-button>
                </el-radio-group>
              </div>
            </template>
            <div ref="dailyChartRef" style="height: 300px;"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :md="8">
          <el-card>
            <template #header>
              <span>本周统计</span>
            </template>
            <div class="week-stats">
              <div class="week-stat-item">
                <div class="week-stat-value">{{ weekStats.total_answered || 0 }}</div>
                <div class="week-stat-label">本周答题</div>
              </div>
              <div class="week-stat-item">
                <div class="week-stat-value">{{ weekStats.total_viewed || 0 }}</div>
                <div class="week-stat-label">本周浏览</div>
              </div>
              <div class="week-stat-item">
                <div class="week-stat-value">{{ weekStats.avg_score?.toFixed(1) || 0 }}</div>
                <div class="week-stat-label">本周均分</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :xs="24" :md="12">
          <el-card>
            <template #header>
              <span>性能趋势</span>
            </template>
            <div ref="trendChartRef" style="height: 300px;"></div>
          </el-card>
        </el-col>

        <el-col :xs="24" :md="12">
          <el-card>
            <template #header>
              <span>分数分布</span>
            </template>
            <div ref="scoreDistChartRef" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>最近答题记录</span>
                <el-button type="primary" size="small" @click="goToLeaderboard">
                  查看排行榜
                </el-button>
              </div>
            </template>
            <el-table :data="recentDailyStats" stripe>
              <el-table-column prop="date" label="日期" width="120">
                <template #default="{ row }">
                  {{ formatDate(row.date) }}
                </template>
              </el-table-column>
              <el-table-column prop="questions_answered" label="答题数" width="100"/>
              <el-table-column prop="questions_viewed" label="浏览数" width="100"/>
              <el-table-column prop="average_score" label="平均分" width="100">
                <template #default="{ row }">
                  <span :class="getScoreClass(row.average_score)">
                    {{ row.average_score?.toFixed(1) || 0 }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="time_spent" label="用时(分钟)">
                <template #default="{ row }">
                  {{ (row.time_spent / 60).toFixed(1) }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Loading, Document, TrendCharts, Clock, Star } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { analyticsAPI } from '@/api'

const router = useRouter()

const loading = ref(false)
const chartPeriod = ref('7')
const userStats = ref({})
const weekStats = ref({})
const recentDailyStats = ref([])

const dailyChartRef = ref(null)
const trendChartRef = ref(null)
const scoreDistChartRef = ref(null)

let dailyChart = null
let trendChart = null
let scoreDistChart = null

const fetchData = async () => {
  loading.value = true
  try {
    const response = await analyticsAPI.getDashboard()
    userStats.value = response.data.user_stats
    weekStats.value = response.data.week_stats
    recentDailyStats.value = response.data.recent_daily_stats

    await nextTick()
    updateCharts()
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const updateCharts = () => {
  initDailyChart()
  initTrendChart()
  initScoreDistChart()
}

const initDailyChart = () => {
  if (!dailyChartRef.value) return

  if (dailyChart) {
    dailyChart.dispose()
  }

  dailyChart = echarts.init(dailyChartRef.value)

  const dates = recentDailyStats.value.map(s => formatDate(s.date))
  const answered = recentDailyStats.value.map(s => s.questions_answered)
  const viewed = recentDailyStats.value.map(s => s.questions_viewed)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['答题数', '浏览数']
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '答题数',
        type: 'line',
        data: answered,
        smooth: true,
        itemStyle: { color: '#409eff' }
      },
      {
        name: '浏览数',
        type: 'line',
        data: viewed,
        smooth: true,
        itemStyle: { color: '#67c23a' }
      }
    ]
  }

  dailyChart.setOption(option)
}

const initTrendChart = () => {
  if (!trendChartRef.value) return

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)

  const dates = recentDailyStats.value.map(s => formatDate(s.date))
  const scores = recentDailyStats.value.map(s => s.average_score || 0)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [
      {
        name: '平均分',
        type: 'line',
        data: scores,
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        },
        itemStyle: { color: '#409eff' }
      }
    ]
  }

  trendChart.setOption(option)
}

const initScoreDistChart = () => {
  if (!scoreDistChartRef.value) return

  if (scoreDistChart) {
    scoreDistChart.dispose()
  }

  scoreDistChart = echarts.init(scoreDistChartRef.value)

  const scores = recentDailyStats.value.map(s => s.average_score || 0)
  const distribution = [0, 0, 0, 0, 0]

  scores.forEach(score => {
    if (score >= 90) distribution[4]++
    else if (score >= 70) distribution[3]++
    else if (score >= 50) distribution[2]++
    else if (score >= 30) distribution[1]++
    else distribution[0]++
  })

  const option = {
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        name: '分数分布',
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: distribution[0], name: '0-30分', itemStyle: { color: '#f56c6c' } },
          { value: distribution[1], name: '30-50分', itemStyle: { color: '#e6a23c' } },
          { value: distribution[2], name: '50-70分', itemStyle: { color: '#e6a23c' } },
          { value: distribution[3], name: '70-90分', itemStyle: { color: '#67c23a' } },
          { value: distribution[4], name: '90-100分', itemStyle: { color: '#409eff' } }
        ]
      }
    ]
  }

  scoreDistChart.setOption(option)
}

const refreshData = () => {
  fetchData()
}

const goToLeaderboard = () => {
  router.push('/leaderboard')
}

const formatTime = (seconds) => {
  if (!seconds) return '0分钟'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  }
  return `${minutes}分钟`
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

const handleResize = () => {
  dailyChart?.resize()
  trendChart?.resize()
  scoreDistChart?.resize()
}

onMounted(() => {
  fetchData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  dailyChart?.dispose()
  trendChart?.dispose()
  scoreDistChart?.dispose()
})
</script>

<style scoped>
.analytics-container {
  padding: 20px;
  max-width: 1400px;
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

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon.total {
  background: #ecf5ff;
  color: #409eff;
}

.stat-icon.score {
  background: #f0f9ff;
  color: #67c23a;
}

.stat-icon.time {
  background: #fdf6ec;
  color: #e6a23c;
}

.stat-icon.favorite {
  background: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
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

.week-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.week-stat-item {
  text-align: center;
}

.week-stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.week-stat-label {
  font-size: 14px;
  color: #909399;
}

.score-high {
  color: #67c23a;
  font-weight: bold;
}

.score-medium {
  color: #e6a23c;
  font-weight: bold;
}

.score-low {
  color: #f56c6c;
  font-weight: bold;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .week-stats {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
