<template>
  <div class="profile-container">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <div v-else class="profile-content">
      <!-- 用户信息头部 -->
      <el-card class="header-card">
        <div class="user-header">
          <div class="avatar-section">
            <AvatarUpload
              :avatar-url="user.avatar_url"
              :username="user.username"
              @upload-success="handleAvatarUploadSuccess"
              @delete-success="handleAvatarDeleteSuccess"
            />
          </div>
          <div class="user-info">
            <h2 class="username">{{ user.username }}</h2>
            <p class="email">{{ user.email }}</p>
            <p class="bio">{{ user.bio || '这个人很懒，什么都没写' }}</p>
          </div>
        </div>
      </el-card>

      <!-- 学习统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="12" :sm="6">
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

        <el-col :xs="12" :sm="6">
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

        <el-col :xs="12" :sm="6">
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

        <el-col :xs="12" :sm="6">
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

      <!-- 基本信息编辑 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-button type="primary" link @click="editInfoVisible = true">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户名">{{ user.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ user.email }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ formatDate(user.date_joined) }}</el-descriptions-item>
          <el-descriptions-item label="个人简介">
            {{ user.bio || '暂无简介' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 技术偏好 -->
      <el-card class="preference-card">
        <template #header>
          <div class="card-header">
            <span>技术偏好</span>
            <el-button type="primary" link @click="openPreferenceModal">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </div>
        </template>

        <div v-if="hasPreferences" class="preferences-content">
          <div v-for="[group, subs] in Object.entries(selectedPreferences)" :key="group" class="preference-group">
            <div class="group-label">{{ group }}</div>
            <div class="tags-container">
              <el-tag v-for="sub in subs" :key="sub" type="primary" size="small">
                {{ sub }}
              </el-tag>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无技术偏好" :image-size="100">
          <el-button type="primary" @click="openPreferenceModal">添加偏好</el-button>
        </el-empty>
      </el-card>

      <!-- 快捷操作 -->
      <el-card class="action-card">
        <template #header>
          <span>快捷操作</span>
        </template>

        <div class="action-buttons">
          <el-button type="primary" @click="goToAnalytics">
            <el-icon><DataAnalysis /></el-icon>
            数据分析
          </el-button>
          <el-button type="success" @click="goToLeaderboard">
            <el-icon><Trophy /></el-icon>
            排行榜
          </el-button>
          <el-button type="warning" @click="goToHistory">
            <el-icon><Clock /></el-icon>
            评分历史
          </el-button>
          <el-button type="danger" @click="confirmLogout" :loading="loggingOut">
            <el-icon><SwitchButton /></el-icon>
            退出登录
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 编辑信息弹窗 -->
    <el-dialog v-model="editInfoVisible" title="编辑基本信息" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" disabled />
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input
            v-model="editForm.bio"
            type="textarea"
            :rows="4"
            placeholder="介绍一下自己吧"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editInfoVisible = false">取消</el-button>
        <el-button type="primary" @click="updateProfile" :loading="updating">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 技术偏好编辑弹窗 -->
    <el-dialog v-model="showPreferenceModal" title="编辑技术偏好" width="700px">
      <div class="preference-modal">
        <div v-for="group in preferenceOptions" :key="group.value" class="preference-group">
          <div class="group-header">
            <el-checkbox
              v-model="group.checked"
              @change="toggleGroup(group)"
            >
              {{ group.label }}
            </el-checkbox>
          </div>
          <div v-if="group.checked" class="checkbox-grid">
            <el-checkbox
              v-for="child in group.children"
              :key="child.value"
              v-model="child.checked"
              @change="updateTempPreferences"
            >
              {{ child.label }}
            </el-checkbox>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeModal">取消</el-button>
        <el-button type="primary" @click="savePreferences">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Loading,
  Document,
  TrendCharts,
  Clock,
  Star,
  Edit,
  DataAnalysis,
  Trophy,
  SwitchButton
} from '@element-plus/icons-vue'
import AvatarUpload from './common/AvatarUpload.vue'
import api from '@/api'

const router = useRouter()

const user = reactive({
  username: '',
  email: '',
  bio: '',
  avatar: '',
  date_joined: '',
  preferences: {}
})

const userStats = reactive({
  total_questions_answered: 0,
  average_score: 0,
  total_time_spent: 0,
  favorite_count: 0
})

const editForm = reactive({
  username: '',
  email: '',
  bio: ''
})

const preferenceOptions = ref([
  {
    label: 'Python',
    value: 'Python',
    checked: false,
    children: [
      { label: 'Python基础', value: 'Python基础', checked: false },
      { label: 'Python进阶', value: 'Python进阶', checked: false },
      { label: 'Flask专题', value: 'Flask专题', checked: false },
      { label: 'Django专题', value: 'Django专题', checked: false }
    ]
  },
  {
    label: '前端',
    value: '前端',
    checked: false,
    children: [
      { label: 'Vue', value: 'Vue', checked: false },
      { label: 'React', value: 'React', checked: false },
      { label: 'JavaScript', value: 'JavaScript', checked: false }
    ]
  },
  {
    label: '后端',
    value: '后端',
    checked: false,
    children: [
      { label: 'Node.js', value: 'Node.js', checked: false },
      { label: 'Java', value: 'Java', checked: false },
      { label: 'Spring Boot', value: 'Spring Boot', checked: false }
    ]
  },
  {
    label: '数据库',
    value: '数据库',
    checked: false,
    children: [
      { label: 'MySQL', value: 'MySQL', checked: false },
      { label: 'PostgreSQL', value: 'PostgreSQL', checked: false },
      { label: 'MongoDB', value: 'MongoDB', checked: false }
    ]
  },
  {
    label: '算法与数据结构',
    value: '算法与数据结构',
    checked: false,
    children: [
      { label: '排序算法', value: '排序算法', checked: false },
      { label: '树结构', value: '树结构', checked: false },
      { label: '图论', value: '图论', checked: false }
    ]
  }
])

const selectedPreferences = ref({})
const tempSelectedPreferences = ref({})
const showPreferenceModal = ref(false)
const editInfoVisible = ref(false)
const loading = ref(true)
const updating = ref(false)
const loggingOut = ref(false)

const hasPreferences = computed(() => {
  return Object.keys(selectedPreferences.value).length > 0
})

const fetchProfile = async () => {
  loading.value = true
  try {
    const response = await api.get('/users/profile/')
    Object.assign(user, response.data)
    Object.assign(editForm, {
      username: response.data.username,
      email: response.data.email,
      bio: response.data.bio || ''
    })

    const existingPrefs = response.data.preferences || {}
    selectedPreferences.value = { ...existingPrefs }
    initPreferenceOptions()

    try {
      const statsResponse = await api.get('/analytics/user-stats/')
      if (statsResponse.data.results && statsResponse.data.results.length > 0) {
        Object.assign(userStats, statsResponse.data.results[0])
      }
    } catch (statsError) {
      console.warn('获取用户统计失败:', statsError)
    }
  } catch (err) {
    console.error('获取用户信息失败:', err)
    if (err.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } else {
      ElMessage.error('获取用户信息失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

const initPreferenceOptions = () => {
  preferenceOptions.value.forEach(group => {
    const subs = selectedPreferences.value[group.value] || []
    group.checked = subs.length > 0
    group.children.forEach(child => {
      child.checked = subs.includes(child.value)
    })
  })
}

const openPreferenceModal = () => {
  initPreferenceOptions()
  tempSelectedPreferences.value = JSON.parse(JSON.stringify(selectedPreferences.value || {}))
  showPreferenceModal.value = true
}

const toggleGroup = (group) => {
  if (group.checked) {
    group.children.forEach(child => {
      child.checked = true
    })
  } else {
    group.children.forEach(child => {
      child.checked = false
    })
  }
  updateTempPreferences()
}

const updateTempPreferences = () => {
  const prefs = {}
  preferenceOptions.value.forEach(group => {
    if (group.checked) {
      const subs = group.children.filter(child => child.checked).map(child => child.value)
      if (subs.length > 0) {
        prefs[group.value] = subs
      }
    }
  })
  tempSelectedPreferences.value = prefs
}

const savePreferences = async () => {
  try {
    await api.patch('/users/profile/', {
      preferences: tempSelectedPreferences.value
    })
    selectedPreferences.value = { ...tempSelectedPreferences.value }
    user.preferences = tempSelectedPreferences.value
    showPreferenceModal.value = false
    ElMessage.success('技术偏好更新成功')
  } catch (err) {
    ElMessage.error('更新失败，请稍后重试')
  }
}

const closeModal = () => {
  showPreferenceModal.value = false
}

const updateProfile = async () => {
  updating.value = true
  try {
    await api.patch('/users/profile/', {
      bio: editForm.bio
    })
    user.bio = editForm.bio
    editInfoVisible.value = false
    ElMessage.success('个人信息更新成功')
  } catch (err) {
    ElMessage.error('更新失败，请稍后重试')
  } finally {
    updating.value = false
  }
}

const handleAvatarUploadSuccess = (avatarUrl) => {
  user.avatar_url = avatarUrl
  ElMessage.success('头像更新成功')
}

const handleAvatarDeleteSuccess = () => {
  user.avatar_url = ''
  ElMessage.success('头像删除成功')
}

const confirmLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await logout()
  } catch {
  }
}

const logout = async () => {
  loggingOut.value = true
  try {
    await api.post('/users/logout/')
  } catch (err) {
    console.warn('注销请求失败:', err)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
    loggingOut.value = false
  }
}

const goToAnalytics = () => {
  router.push('/analytics')
}

const goToLeaderboard = () => {
  router.push('/leaderboard')
}

const goToHistory = () => {
  router.push('/scoring-history')
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
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  color: #909399;
}

.loading-container .el-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 30px;
  padding: 20px 0;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.avatar-btn {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.avatar-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.user-info {
  flex: 1;
  color: #fff;
}

.username {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: bold;
}

.email {
  margin: 0 0 10px 0;
  font-size: 14px;
  opacity: 0.9;
}

.bio {
  margin: 0;
  font-size: 14px;
  opacity: 0.85;
  line-height: 1.6;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
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
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-card,
.preference-card,
.action-card {
  margin-bottom: 20px;
}

.preferences-content {
  padding: 10px 0;
}

.preference-group {
  margin-bottom: 20px;
}

.group-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 10px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-left: 20px;
}

.preference-modal {
  max-height: 500px;
  overflow-y: auto;
}

.preference-modal::-webkit-scrollbar {
  width: 6px;
}

.preference-modal::-webkit-scrollbar-track {
  background: #f2f6fc;
}

.preference-modal::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.group-header {
  padding: 10px 0;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 10px;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  padding: 10px 0 20px 20px;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.action-buttons .el-button {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .user-header {
    flex-direction: column;
    text-align: center;
  }

  .user-info {
    text-align: center;
  }

  .stats-row {
    margin-bottom: 0;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }

  .checkbox-grid {
    grid-template-columns: 1fr;
  }
}
</style>
