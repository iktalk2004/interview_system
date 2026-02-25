<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-logo">
        <router-link to="/">
          <div class="logo-icon">
            <span class="code-bracket">&lt;</span>
            <el-icon><Reading /></el-icon>
            <span class="code-bracket">/&gt;</span>
          </div>
          <div class="logo-text">
            <span class="logo-main">Interview</span>
            <span class="logo-sub">System</span>
          </div>
        </router-link>
      </div>

      <div class="nav-menu">
        <router-link to="/" class="nav-link">
          <el-icon><HomeFilled /></el-icon>
          <span>Home</span>
        </router-link>
        <router-link to="/recommendations" class="nav-link">
          <el-icon><Star /></el-icon>
          <span>Recommend</span>
        </router-link>
        <router-link to="/practice" class="nav-link">
          <el-icon><Edit /></el-icon>
          <span>Practice</span>
        </router-link>
        <router-link to="/code-practice" class="nav-link">
          <el-icon><Monitor /></el-icon>
          <span>Code</span>
        </router-link>
        <router-link to="/questions" class="nav-link">
          <el-icon><Document /></el-icon>
          <span>Questions</span>
        </router-link>
        <router-link to="/analytics" class="nav-link">
          <el-icon><DataAnalysis /></el-icon>
          <span>Analytics</span>
        </router-link>
        <router-link to="/leaderboard" class="nav-link">
          <el-icon><Trophy /></el-icon>
          <span>Ranking</span>
        </router-link>
        <router-link to="/scoring-history" class="nav-link">
          <el-icon><Clock /></el-icon>
          <span>History</span>
        </router-link>
        <router-link v-if="isAdmin" to="/dashboard" class="nav-link admin-link">
          <el-icon><Setting /></el-icon>
          <span>Admin</span>
        </router-link>
      </div>

      <div class="nav-actions">
        <div class="theme-toggle" @click="toggleTheme">
          <el-icon><Moon v-if="isDarkMode" /><Sunny v-else /></el-icon>
        </div>
        <template v-if="isAuthenticated">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-dropdown">
              <UserAvatar
                :avatar-url="userAvatarUrl"
                :username="userName"
                size="medium"
                :clickable="false"
              />
              <div class="user-info">
                <span class="username code-font">{{ userName }}</span>
                <span class="user-role">{{ isAdmin ? 'admin' : 'user' }}</span>
              </div>
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  <span>Profile</span>
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  <span>Logout</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="auth-btn login-btn">
            <span class="code-font">Login</span>
          </router-link>
          <router-link to="/register" class="auth-btn register-btn">
            <span class="code-font">Register</span>
          </router-link>
        </template>
      </div>

      <div class="nav-toggle" @click="toggleMobileMenu">
        <el-icon :size="24"><Menu /></el-icon>
      </div>
    </div>

    <el-drawer v-model="mobileMenuOpen" direction="rtl" :size="300" class="mobile-drawer">
      <div class="mobile-menu-content">
        <div class="mobile-header">
          <div class="mobile-logo">
            <span class="code-bracket">&lt;</span>
            <span class="code-font">Interview</span>
            <span class="code-bracket">/&gt;</span>
          </div>
          <el-icon class="close-icon" @click="closeMobileMenu"><Close /></el-icon>
        </div>

        <div class="mobile-user-info" v-if="isAuthenticated">
          <UserAvatar
            :avatar-url="userAvatarUrl"
            :username="userName"
            size="large"
            :clickable="false"
          />
          <div class="mobile-user-name code-font">{{ userName }}</div>
          <div class="mobile-user-role">{{ isAdmin ? 'admin' : 'user' }}</div>
        </div>

        <div class="mobile-menu-items">
          <router-link to="/" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><HomeFilled /></el-icon>
            <span>Home</span>
          </router-link>
          <router-link to="/recommendations" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Star /></el-icon>
            <span>Recommend</span>
          </router-link>
          <router-link to="/practice" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Edit /></el-icon>
            <span>Practice</span>
          </router-link>
          <router-link to="/code-practice" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Monitor /></el-icon>
            <span>Code</span>
          </router-link>
          <router-link to="/questions" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Document /></el-icon>
            <span>Questions</span>
          </router-link>
          <router-link to="/analytics" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><DataAnalysis /></el-icon>
            <span>Analytics</span>
          </router-link>
          <router-link to="/leaderboard" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Trophy /></el-icon>
            <span>Ranking</span>
          </router-link>
          <router-link to="/scoring-history" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><Clock /></el-icon>
            <span>History</span>
          </router-link>
          <router-link v-if="isAdmin" to="/dashboard" class="mobile-nav-link admin-link" @click="closeMobileMenu">
            <el-icon><Setting /></el-icon>
            <span>Admin</span>
          </router-link>
          <router-link v-if="isAuthenticated" to="/profile" class="mobile-nav-link" @click="closeMobileMenu">
            <el-icon><User /></el-icon>
            <span>Profile</span>
          </router-link>
        </div>

        <div class="mobile-actions" v-if="!isAuthenticated">
          <router-link to="/login" class="mobile-auth-btn login-btn" @click="closeMobileMenu">
            <span class="code-font">Login</span>
          </router-link>
          <router-link to="/register" class="mobile-auth-btn register-btn" @click="closeMobileMenu">
            <span class="code-font">Register</span>
          </router-link>
        </div>

        <div class="mobile-footer">
          <div class="terminal-prompt code-font">
            <span class="prompt-symbol">$</span>
            <span class="blink-cursor">&nbsp;</span>
          </div>
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
  Monitor,
  Document,
  DataAnalysis,
  Trophy,
  Clock,
  User,
  SwitchButton,
  ArrowDown,
  Menu,
  Setting,
  Close,
  Moon,
  Sunny
} from '@element-plus/icons-vue'
import UserAvatar from './common/UserAvatar.vue'
import api from '@/api'

const router = useRouter()

const mobileMenuOpen = ref(false)
const isAuthenticated = ref(false)
const userName = ref('')
const userAvatar = ref('')
const isAdmin = ref(false)
const isDarkMode = ref(true)

const userAvatarUrl = computed(() => {
  return userAvatar.value || '/media/avatars/default/default-avatar.svg'
})

const checkAuthStatus = () => {
  const token = localStorage.getItem('access_token')
  isAuthenticated.value = !!token
  if (token) {
    const userData = localStorage.getItem('user_data')
    if (userData) {
      try {
        const data = JSON.parse(userData)
        userName.value = data.username || ''
        userAvatar.value = data.avatar_url || ''
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

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.setAttribute('data-theme', isDarkMode.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
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
  
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark'
    document.documentElement.setAttribute('data-theme', savedTheme)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.navbar {
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.nav-container {
  max-width: 1600px;
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
  gap: 12px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.logo-icon {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 24px;
  color: var(--accent-primary);
}

.code-bracket {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--accent-secondary);
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.logo-main {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.logo-sub {
  font-size: 10px;
  font-weight: 600;
  color: var(--accent-primary);
  letter-spacing: 2px;
  text-transform: uppercase;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  text-decoration: none;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 13px;
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  transition: all 0.3s ease;
  position: relative;
}

.nav-link::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 0;
  background: var(--accent-primary);
  border-radius: 2px;
  transition: height 0.3s ease;
}

.nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-link:hover::before {
  height: 16px;
}

.nav-link.router-link-active {
  background: rgba(137, 180, 250, 0.1);
  color: var(--accent-primary);
  font-weight: 600;
}

.nav-link.router-link-active::before {
  height: 16px;
}

.nav-link.admin-link {
  background: linear-gradient(135deg, rgba(137, 180, 250, 0.2) 0%, rgba(245, 194, 231, 0.2) 100%);
  color: var(--accent-secondary);
  border: 1px solid var(--accent-secondary);
}

.nav-link.admin-link:hover {
  background: linear-gradient(135deg, rgba(245, 194, 231, 0.3) 0%, rgba(137, 180, 250, 0.3) 100%);
  color: var(--accent-primary);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.user-dropdown:hover {
  background: var(--bg-hover);
  border-color: var(--border-color);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  color: var(--bg-primary);
}

.user-avatar.large {
  width: 60px;
  height: 60px;
  font-size: 24px;
}

.avatar-text {
  font-family: var(--font-mono);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-role {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--accent-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.arrow-icon {
  font-size: 12px;
  color: var(--text-muted);
}

.auth-btn {
  padding: 8px 20px;
  border-radius: var(--radius-sm);
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  transition: all 0.3s ease;
  font-family: var(--font-mono);
}

.login-btn {
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
}

.login-btn:hover {
  background: rgba(137, 180, 250, 0.1);
  color: var(--accent-primary);
}

.register-btn {
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  color: var(--bg-primary);
  border: none;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.nav-toggle {
  display: none;
  cursor: pointer;
  padding: 8px;
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
  color: var(--text-secondary);
}

.nav-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.mobile-drawer {
  --el-drawer-padding-primary: 0;
}

.mobile-menu-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-secondary);
}

.mobile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-tertiary);
}

.mobile-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 700;
  color: var(--accent-primary);
  font-family: var(--font-mono);
}

.close-icon {
  font-size: 24px;
  cursor: pointer;
  color: var(--text-muted);
  transition: color 0.3s ease;
}

.close-icon:hover {
  color: var(--text-primary);
}

.mobile-user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0 24px;
  border-bottom: 1px solid var(--border-color);
}

.mobile-user-name {
  margin-top: 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.mobile-user-role {
  margin-top: 4px;
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--accent-primary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.mobile-menu-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  overflow-y: auto;
  padding: 16px 12px;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 14px;
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
  font-family: var(--font-mono);
}

.mobile-nav-link:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.mobile-nav-link.router-link-active {
  background: rgba(137, 180, 250, 0.1);
  color: var(--accent-primary);
  font-weight: 600;
}

.mobile-nav-link.admin-link {
  background: linear-gradient(135deg, rgba(137, 180, 250, 0.2) 0%, rgba(245, 194, 231, 0.2) 100%);
  color: var(--accent-secondary);
  border: 1px solid var(--accent-secondary);
}

.mobile-actions {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
}

.mobile-auth-btn {
  flex: 1;
  padding: 12px;
  text-align: center;
  text-decoration: none;
  border-radius: var(--radius-sm);
  font-weight: 600;
  transition: all 0.3s ease;
  font-family: var(--font-mono);
  font-size: 13px;
}

.mobile-login-btn {
  color: var(--accent-primary);
  border: 1px solid var(--accent-primary);
}

.mobile-login-btn:hover {
  background: rgba(137, 180, 250, 0.1);
  color: var(--accent-primary);
}

.mobile-register-btn {
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  color: var(--bg-primary);
  border: none;
}

.mobile-footer {
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--code-bg);
}

.terminal-prompt {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: var(--code-text);
}

.prompt-symbol {
  color: var(--accent-success);
  margin-right: 8px;
}

@media (max-width: 1024px) {
  .nav-menu {
    display: none;
  }

  .nav-actions .theme-toggle {
    display: flex;
  }

  .nav-actions .user-dropdown,
  .nav-actions .auth-btn {
    display: none;
  }

  .nav-toggle {
    display: flex;
  }
}
</style>
