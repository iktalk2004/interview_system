<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-logo">
        <router-link to="/">
          <el-icon><Reading /></el-icon>
          <span>面试系统</span>
        </router-link>
      </div>

      <div class="nav-menu">
        <router-link to="/" class="nav-link">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </router-link>
        <router-link to="/recommendations" class="nav-link">
          <el-icon><Star /></el-icon>
          <span>智能推荐</span>
        </router-link>
        <router-link to="/practice" class="nav-link">
          <el-icon><Edit /></el-icon>
          <span>答题练习</span>
        </router-link>
        <router-link to="/questions" class="nav-link">
          <el-icon><Document /></el-icon>
          <span>题库</span>
        </router-link>
        <router-link to="/analytics" class="nav-link">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据分析</span>
        </router-link>
        <router-link to="/leaderboard" class="nav-link">
          <el-icon><Trophy /></el-icon>
          <span>排行榜</span>
        </router-link>
        <router-link to="/scoring-history" class="nav-link">
          <el-icon><Clock /></el-icon>
          <span>评分历史</span>
        </router-link>
        <router-link v-if="isAdmin" to="/dashboard" class="nav-link admin-link">
          <el-icon><Setting /></el-icon>
          <span>管理后台</span>
        </router-link>
      </div>

      <div class="nav-actions">
        <template v-if="isAuthenticated">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-dropdown">
              <el-avatar :size="36" :src="userAvatar">
                {{ userName?.charAt(0).toUpperCase() }}
              </el-avatar>
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
        </template>
        <template v-else>
          <router-link to="/login" class="login-btn">
            登录
          </router-link>
          <router-link to="/register" class="register-btn">
            注册
          </router-link>
        </template>
      </div>

      <div class="nav-toggle" @click="toggleMobileMenu">
        <el-icon :size="24"><Menu /></el-icon>
      </div>
    </div>

    <el-drawer v-model="mobileMenuOpen" direction="rtl" :size="280" class="mobile-drawer">
      <div class="mobile-menu-content">
        <div class="mobile-user-info" v-if="isAuthenticated">
          <el-avatar :size="60" :src="userAvatar">
            {{ userName?.charAt(0).toUpperCase() }}
          </el-avatar>
          <div class="mobile-user-name">{{ userName }}</div>
        </div>

        <div class="mobile-menu-items">
          <router-link to="/" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </router-link>
          <router-link to="/recommendations" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Star /></el-icon>
            <span>智能推荐</span>
          </router-link>
          <router-link to="/practice" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Edit /></el-icon>
            <span>答题练习</span>
          </router-link>
          <router-link to="/questions" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Document /></el-icon>
            <span>题库</span>
          </router-link>
          <router-link to="/analytics" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据分析</span>
          </router-link>
          <router-link to="/leaderboard" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Trophy /></el-icon>
            <span>排行榜</span>
          </router-link>
          <router-link to="/scoring-history" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Clock /></el-icon>
            <span>评分历史</span>
          </router-link>
          <router-link v-if="isAdmin" to="/dashboard" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Setting /></el-icon>
            <span>管理后台</span>
          </router-link>
          <router-link v-if="isAuthenticated" to="/profile" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><User /></el-icon>
            <span>个人中心</span>
          </router-link>
        </div>

        <div class="mobile-actions" v-if="!isAuthenticated">
          <router-link to="/login" class="mobile-login-btn" @click="closeMobileMenu">
            登录
          </router-link>
          <router-link to="/register" class="mobile-register-btn" @click="closeMobileMenu">
            注册
          </router-link>
        </div>
      </div>
    </el-drawer>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Reading,
  HomeFilled,
  Star,
  Edit,
  Document,
  DataAnalysis,
  Trophy,
  Clock,
  User,
  SwitchButton,
  ArrowDown,
  Menu,
  Setting
} from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()

const mobileMenuOpen = ref(false)
const isAuthenticated = ref(false)
const userName = ref('')
const userAvatar = ref('')
const isAdmin = ref(false)

const checkAuthStatus = () => {
  const token = localStorage.getItem('access_token')
  isAuthenticated.value = !!token
  if (token) {
    const userData = localStorage.getItem('user_data')
    if (userData) {
      try {
        const data = JSON.parse(userData)
        userName.value = data.username || ''
        userAvatar.value = data.avatar || ''
        isAdmin.value = data.is_staff || false
      } catch (e) {
        console.error('解析用户数据失败:', e)
      }
    }
  }
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    await logout()
  }
}

const logout = async () => {
  try {
    await api.post('/users/logout/')
    ElMessage.success('退出登录成功')
  } catch (err) {
    console.warn('退出登录请求失败:', err)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
    isAuthenticated.value = false
    userName.value = ''
    userAvatar.value = ''
    router.push('/login')
  }
}

const handleResize = () => {
  if (window.innerWidth > 768) {
    mobileMenuOpen.value = false
  }
}

onMounted(() => {
  checkAuthStatus()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.navbar {
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.nav-logo a {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  text-decoration: none;
  transition: all 0.3s ease;
}

.nav-logo a:hover {
  color: #409eff;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  text-decoration: none;
  color: #4a4a4a;
  font-weight: 500;
  font-size: 14px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-link.router-link-active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

.nav-link.admin-link {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

.nav-link.admin-link:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  color: #ffffff;
}

.nav-link.admin-link.router-link-active {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  color: #ffffff;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-dropdown:hover {
  background: #f5f7fa;
}

.arrow-icon {
  font-size: 12px;
  color: #909399;
}

.login-btn,
.register-btn {
  padding: 8px 20px;
  border-radius: 20px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-btn {
  color: #409eff;
  border: 1px solid #409eff;
}

.login-btn:hover {
  background: #409eff;
  color: #ffffff;
}

.register-btn {
  background: #409eff;
  color: #ffffff;
}

.register-btn:hover {
  background: #66b1ff;
}

.nav-toggle {
  display: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-toggle:hover {
  background: #f5f7fa;
}

.mobile-drawer {
  --el-drawer-padding-primary: 24px;
}

.mobile-menu-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.mobile-user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0 24px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 16px;
}

.mobile-user-name {
  margin-top: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.mobile-menu-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  overflow-y: auto;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  text-decoration: none;
  color: #4a4a4a;
  font-size: 15px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.mobile-nav-link:hover {
  background: #f5f7fa;
  color: #409eff;
}

.mobile-nav-link.router-link-active {
  background: #ecf5ff;
  color: #409eff;
  font-weight: 600;
}

.mobile-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.mobile-login-btn,
.mobile-register-btn {
  flex: 1;
  padding: 12px;
  text-align: center;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.mobile-login-btn {
  color: #409eff;
  border: 1px solid #409eff;
}

.mobile-login-btn:hover {
  background: #409eff;
  color: #ffffff;
}

.mobile-register-btn {
  background: #409eff;
  color: #ffffff;
}

.mobile-register-btn:hover {
  background: #66b1ff;
}

@media (max-width: 1024px) {
  .nav-menu {
    display: none;
  }

  .nav-actions {
    display: none;
  }

  .nav-toggle {
    display: flex;
  }
}
</style>
