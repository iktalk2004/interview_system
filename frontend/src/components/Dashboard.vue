<template>
  <div class="dashboard-container">
    <div class="sidebar">
      <div class="sidebar-header">
        <el-icon class="logo-icon"><Reading /></el-icon>
        <span class="logo-text">管理后台</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <el-menu-item index="overview">
          <el-icon><DataBoard /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        <el-menu-item index="users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="questions">
          <el-icon><Document /></el-icon>
          <span>题目管理</span>
        </el-menu-item>
        <el-menu-item index="categories">
          <el-icon><Folder /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="analytics">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
        <el-menu-item index="settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-button @click="goToHome" text>
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
      </div>
    </div>

    <div class="main-content">
      <div class="top-bar">
        <div class="page-title">
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="user-info">
          <el-dropdown trigger="click">
            <div class="user-dropdown">
              <el-avatar :size="36" :src="userAvatar">
                {{ userName?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ userName }}</span>
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <div class="content-area">
        <div v-if="activeMenu === 'overview'" class="overview-section">
          <el-row :gutter="20" class="stats-row">
            <el-col :xs="12" :sm="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon users">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ stats.totalUsers }}</div>
                    <div class="stat-label">总用户数</div>
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col :xs="12" :sm="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon questions">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ stats.totalQuestions }}</div>
                    <div class="stat-label">总题目数</div>
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col :xs="12" :sm="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon answers">
                    <el-icon><ChatDotRound /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ stats.totalAnswers }}</div>
                    <div class="stat-label">总答题数</div>
                  </div>
                </div>
              </el-card>
            </el-col>

            <el-col :xs="12" :sm="6">
              <el-card class="stat-card">
                <div class="stat-content">
                  <div class="stat-icon avg-score">
                    <el-icon><TrendCharts /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ stats.avgScore }}</div>
                    <div class="stat-label">平均分数</div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="20" class="charts-row">
            <el-col :xs="24" :md="12">
              <el-card class="chart-card">
                <template #header>
                  <div class="card-header">
                    <el-icon><TrendCharts /></el-icon>
                    <span>答题趋势</span>
                  </div>
                </template>
                <div class="chart-container" ref="trendChartRef"></div>
              </el-card>
            </el-col>

            <el-col :xs="24" :md="12">
              <el-card class="chart-card">
                <template #header>
                  <div class="card-header">
                    <el-icon><PieChart /></el-icon>
                    <span>题目分布</span>
                  </div>
                </template>
                <div class="chart-container" ref="pieChartRef"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-card class="recent-activity-card">
            <template #header>
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>最近活动</span>
              </div>
            </template>
            <el-table :data="recentActivities" stripe>
              <el-table-column prop="user" label="用户" width="120" />
              <el-table-column prop="action" label="操作" />
              <el-table-column prop="target" label="目标" />
              <el-table-column prop="time" label="时间" width="180" />
            </el-table>
          </el-card>
        </div>

        <div v-else-if="activeMenu === 'users'" class="users-section">
          <el-card class="table-card">
            <template #header>
              <div class="card-header-with-actions">
                <div class="card-header">
                  <el-icon><User /></el-icon>
                  <span>用户列表</span>
                </div>
                <el-button type="primary" @click="showAddUserDialog = true">
                  <el-icon><Plus /></el-icon>
                  添加用户
                </el-button>
              </div>
            </template>
            <el-table :data="users" v-loading="loading" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="username" label="用户名" width="150" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="date_joined" label="注册时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.date_joined) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="editUser(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteUser(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="usersPage"
                :page-size="usersPageSize"
                :total="usersTotal"
                background
                layout="prev, pager, next, total"
              />
            </div>
          </el-card>
        </div>

        <div v-else-if="activeMenu === 'questions'" class="questions-section">
          <el-card class="table-card">
            <template #header>
              <div class="card-header-with-actions">
                <div class="card-header">
                  <el-icon><Document /></el-icon>
                  <span>题目列表</span>
                </div>
                <el-button type="primary" @click="goToQuestionForm">
                  <el-icon><Plus /></el-icon>
                  添加题目
                </el-button>
              </div>
            </template>
            <el-table :data="questions" v-loading="loading" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="标题" show-overflow-tooltip />
              <el-table-column label="难度" width="100">
                <template #default="{ row }">
                  <el-tag :type="getDifficultyType(row.difficulty)" size="small">
                    {{ difficultyMap[row.difficulty] }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="category.name" label="分类" width="120" />
              <el-table-column prop="is_approved" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_approved ? 'success' : 'warning'" size="small">
                    {{ row.is_approved ? '已审核' : '待审核' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="viewQuestion(row)">查看</el-button>
                  <el-button size="small" type="danger" @click="deleteQuestion(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="questionsPage"
                :page-size="questionsPageSize"
                :total="questionsTotal"
                background
                layout="prev, pager, next, total"
              />
            </div>
          </el-card>
        </div>

        <div v-else-if="activeMenu === 'categories'" class="categories-section">
          <el-card class="table-card">
            <template #header>
              <div class="card-header-with-actions">
                <div class="card-header">
                  <el-icon><Folder /></el-icon>
                  <span>分类列表</span>
                </div>
                <el-button type="primary" @click="showAddCategoryDialog = true">
                  <el-icon><Plus /></el-icon>
                  添加分类
                </el-button>
              </div>
            </template>
            <el-table :data="categories" v-loading="loading" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="name" label="分类名称" />
              <el-table-column prop="parent" label="父分类" width="150">
                <template #default="{ row }">
                  {{ row.parent?.name || '无' }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="editCategory(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteCategory(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>

        <div v-else-if="activeMenu === 'analytics'" class="analytics-section">
          <el-row :gutter="20">
            <el-col :span="24">
              <el-card class="chart-card">
                <template #header>
                  <div class="card-header">
                    <el-icon><DataAnalysis /></el-icon>
                    <span>用户活跃度</span>
                  </div>
                </template>
                <div class="chart-container" ref="activityChartRef"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <div v-else-if="activeMenu === 'settings'" class="settings-section">
          <el-card class="settings-card">
            <template #header>
              <div class="card-header">
                <el-icon><Setting /></el-icon>
                <span>系统设置</span>
              </div>
            </template>
            <el-form :model="settings" label-width="120px" class="settings-form">
              <el-form-item label="系统名称">
                <el-input v-model="settings.systemName" />
              </el-form-item>
              <el-form-item label="系统描述">
                <el-input v-model="settings.systemDescription" type="textarea" :rows="3" />
              </el-form-item>
              <el-form-item label="允许注册">
                <el-switch v-model="settings.allowRegister" />
              </el-form-item>
              <el-form-item label="维护模式">
                <el-switch v-model="settings.maintenanceMode" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveSettings">保存设置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </div>
    </div>

    <el-dialog v-model="showAddUserDialog" title="添加用户" width="500px">
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="newUser.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="newUser.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newUser.password" type="password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddUserDialog = false">取消</el-button>
        <el-button type="primary" @click="addUser">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showAddCategoryDialog" title="添加分类" width="500px">
      <el-form :model="newCategory" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="newCategory.name" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="newCategory.parent" placeholder="选择父分类">
            <el-option label="无" :value="null" />
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="addCategory">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Reading,
  DataBoard,
  User,
  Document,
  Folder,
  DataAnalysis,
  Setting,
  HomeFilled,
  ArrowDown,
  SwitchButton,
  TrendCharts,
  PieChart,
  Clock,
  ChatDotRound,
  Plus
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const activeMenu = ref('overview')
const loading = ref(false)
const showAddUserDialog = ref(false)
const showAddCategoryDialog = ref(false)

const userName = ref('')
const userAvatar = ref('')

const stats = reactive({
  totalUsers: 0,
  totalQuestions: 0,
  totalAnswers: 0,
  avgScore: 0
})

const users = ref([])
const usersPage = ref(1)
const usersPageSize = ref(10)
const usersTotal = ref(0)

const questions = ref([])
const questionsPage = ref(1)
const questionsPageSize = ref(10)
const questionsTotal = ref(0)

const categories = ref([])

const recentActivities = ref([])

const newUser = reactive({
  username: '',
  email: '',
  password: ''
})

const newCategory = reactive({
  name: '',
  parent: null
})

const settings = reactive({
  systemName: '程序员八股文答题训练系统',
  systemDescription: '基于协同过滤的智能答题训练平台',
  allowRegister: true,
  maintenanceMode: false
})

const trendChartRef = ref(null)
const pieChartRef = ref(null)
const activityChartRef = ref(null)

const pageTitle = computed(() => {
  const titles = {
    overview: '数据概览',
    users: '用户管理',
    questions: '题目管理',
    categories: '分类管理',
    analytics: '数据分析',
    settings: '系统设置'
  }
  return titles[activeMenu.value] || '数据概览'
})

const difficultyMap = { 1: '易', 2: '中', 3: '难' }

const getDifficultyType = (difficulty) => {
  const map = { 1: 'success', 2: 'warning', 3: 'danger' }
  return map[difficulty] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  if (index === 'overview') {
    nextTick(() => {
      initCharts()
    })
  } else if (index === 'users') {
    fetchUsers()
  } else if (index === 'questions') {
    fetchQuestions()
  } else if (index === 'categories') {
    fetchCategories()
  } else if (index === 'analytics') {
    nextTick(() => {
      initActivityChart()
    })
  } else if (index === 'settings') {
    fetchSettings()
  }
}

const fetchStats = async () => {
  try {
    const response = await api.get('/admin/overview/')
    Object.assign(stats, response.data)
  } catch (err) {
    console.error('获取统计数据失败:', err)
  }
}

const fetchTrendData = async () => {
  try {
    const response = await api.get('/admin/trend_data/')
    return response.data
  } catch (err) {
    console.error('获取趋势数据失败:', err)
    return { dates: [], counts: [], scores: [] }
  }
}

const fetchCategoryDistribution = async () => {
  try {
    const response = await api.get('/admin/category_distribution/')
    return response.data
  } catch (err) {
    console.error('获取分类分布失败:', err)
    return []
  }
}

const fetchRecentActivities = async () => {
  try {
    const response = await api.get('/admin/recent_activities/')
    recentActivities.value = response.data
  } catch (err) {
    console.error('获取最近活动失败:', err)
  }
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/user_list/', {
      params: {
        page: usersPage.value,
        page_size: usersPageSize.value
      }
    })
    users.value = response.data.results || []
    usersTotal.value = response.data.count || 0
  } catch (err) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const fetchQuestions = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/question_list/', {
      params: {
        page: questionsPage.value,
        page_size: questionsPageSize.value
      }
    })
    questions.value = response.data.results || []
    questionsTotal.value = response.data.count || 0
  } catch (err) {
    ElMessage.error('获取题目列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/category_list/')
    categories.value = response.data || []
  } catch (err) {
    ElMessage.error('获取分类列表失败')
  } finally {
    loading.value = false
  }
}

const fetchSettings = async () => {
  try {
    const response = await api.get('/admin/settings/')
    Object.assign(settings, response.data)
  } catch (err) {
    console.error('获取系统设置失败:', err)
  }
}

const addUser = async () => {
  try {
    await api.post('/admin/create_user/', { ...newUser })
    ElMessage.success('用户添加成功')
    showAddUserDialog.value = false
    Object.assign(newUser, { username: '', email: '', password: '' })
    fetchUsers()
  } catch (err) {
    ElMessage.error('添加用户失败')
  }
}

const editUser = (user) => {
  ElMessage.info('编辑功能开发中...')
}

const deleteUser = async (user) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${user.username} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/admin/delete-user/${user.id}/`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewQuestion = (question) => {
  router.push(`/practice/${question.id}`)
}

const deleteQuestion = async (question) => {
  try {
    await ElMessageBox.confirm(`确定要删除题目 ${question.title} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/admin/delete-question/${question.id}/`)
    ElMessage.success('删除成功')
    fetchQuestions()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const goToQuestionForm = () => {
  router.push('/questions/new')
}

const editCategory = (category) => {
  ElMessage.info('编辑功能开发中...')
}

const deleteCategory = async (category) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类 ${category.name} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.delete(`/admin/delete-category/${category.id}/`)
    ElMessage.success('删除成功')
    fetchCategories()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const addCategory = async () => {
  try {
    await api.post('/admin/create_category/', { ...newCategory })
    ElMessage.success('分类添加成功')
    showAddCategoryDialog.value = false
    Object.assign(newCategory, { name: '', parent: null })
    fetchCategories()
  } catch (err) {
    ElMessage.error('添加分类失败')
  }
}

const saveSettings = async () => {
  try {
    await api.post('/admin/update_settings/', { ...settings })
    ElMessage.success('设置保存成功')
  } catch (err) {
    ElMessage.error('保存设置失败')
  }
}

const initCharts = async () => {
  await fetchStats()
  await fetchRecentActivities()

  const trendData = await fetchTrendData()
  const categoryData = await fetchCategoryDistribution()

  if (trendChartRef.value) {
    const trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['答题数', '平均分']
      },
      xAxis: {
        type: 'category',
        data: trendData.dates
      },
      yAxis: [
        {
          type: 'value',
          name: '答题数'
        },
        {
          type: 'value',
          name: '平均分'
        }
      ],
      series: [
        {
          name: '答题数',
          type: 'line',
          data: trendData.counts,
          smooth: true
        },
        {
          name: '平均分',
          type: 'line',
          yAxisIndex: 1,
          data: trendData.scores,
          smooth: true
        }
      ]
    })
  }

  if (pieChartRef.value) {
    const pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '题目分布',
          type: 'pie',
          radius: '50%',
          data: categoryData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    })
  }
}

const initActivityChart = async () => {
  try {
    const response = await api.get('/admin/user_activity/')
    const data = response.data

    if (activityChartRef.value) {
      const activityChart = echarts.init(activityChartRef.value)
      activityChart.setOption({
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: data.dates
        },
        yAxis: {
          type: 'value',
          name: '活跃用户数'
        },
        series: [
          {
            name: '活跃用户',
            type: 'line',
            data: data.counts,
            smooth: true,
            areaStyle: {}
          }
        ]
      })
    }
  } catch (err) {
    console.error('初始化活跃度图表失败:', err)
  }
}

const goToHome = () => {
  router.push('/')
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    userName.value = user.username
    userAvatar.value = user.avatar
  }

  initCharts()
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 240px;
  background: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
}

.sidebar-header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 28px;
  color: #1890ff;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.sidebar-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.65);
}

.sidebar-menu :deep(.el-menu-item:hover) {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.15);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-footer .el-button {
  color: rgba(255, 255, 255, 0.65);
  width: 100%;
}

.sidebar-footer .el-button:hover {
  color: #fff;
}

.main-content {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
}

.top-bar {
  background: #fff;
  padding: 16px 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #262626;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.3s;
}

.user-dropdown:hover {
  background: #f5f5f5;
}

.username {
  font-size: 14px;
  color: #595959;
}

.arrow-icon {
  font-size: 12px;
  color: #8c8c8c;
}

.content-area {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.stat-icon.questions {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.stat-icon.answers {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: #fff;
}

.stat-icon.avg-score {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #262626;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.charts-row {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.card-header-with-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 320px;
}

.recent-activity-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.settings-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  max-width: 800px;
}

.settings-form {
  padding: 20px 0;
}

@media (max-width: 768px) {
  .sidebar {
    width: 64px;
  }

  .sidebar-header {
    padding: 16px 12px;
    justify-content: center;
  }

  .logo-text {
    display: none;
  }

  .sidebar-menu :deep(.el-menu-item span) {
    display: none;
  }

  .sidebar-menu :deep(.el-menu-item) {
    padding: 0 20px;
  }

  .main-content {
    margin-left: 64px;
  }

  .content-area {
    padding: 16px;
  }

  .stat-value {
    font-size: 24px;
  }
}
</style>
