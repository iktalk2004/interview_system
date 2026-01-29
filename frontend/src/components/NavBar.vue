<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-logo">
        <router-link to="/">面试系统</router-link>
      </div>

      <ul class="nav-menu">
        <li class="nav-item">
          <router-link to="/" class="nav-link">个人中心</router-link>
        </li>
        <li class="nav-item">
          <router-link to="/practice" class="nav-link">热门</router-link>
        </li>
        <li class="nav-item">
          <router-link to="/questions" class="nav-link">题库</router-link>
        </li>
        <li class="nav-item" v-if="isAuthenticated">
          <router-link to="/profile" class="nav-link">个人中心</router-link>
        </li>
        <li class="nav-item" v-if="!isAuthenticated">
          <router-link to="/login" class="nav-link">登录</router-link>
        </li>
        <li class="nav-item" v-if="isAuthenticated">
          <a href="#" @click="logout" class="nav-link">退出</a>
        </li>
      </ul>

      <div class="nav-toggle" @click="toggleMobileMenu">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </div>
    </div>

    <!-- Mobile menu overlay -->
    <div v-show="mobileMenuOpen" class="mobile-menu-overlay">
      <ul class="mobile-nav-menu">
        <li class="mobile-nav-item">
          <router-link to="/" class="mobile-nav-link" @click="closeMobileMenu">首页</router-link>
        </li>
        <li class="mobile-nav-item">
          <router-link to="/practice" class="mobile-nav-link" @click="closeMobileMenu">热门</router-link>
        </li>
        <li class="mobile-nav-item">
          <router-link to="/questions" class="mobile-nav-link" @click="closeMobileMenu">题库</router-link>
        </li>
        <li class="mobile-nav-item" v-if="isAuthenticated">
          <router-link to="/profile" class="mobile-nav-link" @click="closeMobileMenu">个人中心</router-link>
        </li>
        <li class="mobile-nav-item" v-if="!isAuthenticated">
          <router-link to="/login" class="mobile-nav-link" @click="closeMobileMenu">登录</router-link>
        </li>
        <li class="mobile-nav-item" v-if="isAuthenticated">
          <a href="#" @click="logoutAndClose" class="mobile-nav-link">退出</a>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import {useRouter} from 'vue-router';
import api from '@/api.js';

const router = useRouter();
const mobileMenuOpen = ref(false);
const isAuthenticated = ref(false);

// 检查用户是否已认证
const checkAuthStatus = () => {
  const token = localStorage.getItem('access_token');
  isAuthenticated.value = !!token;
};

// 切换移动菜单
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};

// 关闭移动菜单
const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
};

// 登出并关闭移动菜单
const logoutAndClose = () => {
  logout();
  closeMobileMenu();
};

// 登出功能
const logout = async () => {
  try {
    await api.post('users/logout/');
  } catch (err) {
    console.warn('登出请求失败，但已清除本地token', err);
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    isAuthenticated.value = false;
    router.push('/login');
  }
};

// 监听窗口大小变化，自动关闭移动端菜单
const handleResize = () => {
  if (window.innerWidth > 768) {
    mobileMenuOpen.value = false;
  }
};

onMounted(() => {
  checkAuthStatus();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.navbar {
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.nav-logo a {
  font-size: 1.5rem;
  font-weight: bold;
  color: #409EFF;
  text-decoration: none;
}

.nav-menu {
  display: flex;
  align-items: center;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-left: 2rem;
}

.nav-link {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 0.5rem 0;
  position: relative;
  transition: color 0.3s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #409EFF;
}

.nav-link.router-link-active::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #409EFF;
}

.nav-toggle {
  display: none;
  flex-direction: column;
  cursor: pointer;
}

.bar {
  width: 25px;
  height: 3px;
  background-color: #333;
  margin: 3px 0;
  transition: 0.3s;
}

.mobile-menu-overlay {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  z-index: 999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.mobile-nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  max-width: 300px;
}

.mobile-nav-item {
  margin: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.mobile-nav-link {
  display: block;
  padding: 1rem 0;
  text-align: center;
  color: white;
  text-decoration: none;
  font-size: 1.2rem;
  transition: color 0.3s ease;
}

.mobile-nav-link:hover,
.mobile-nav-link.router-link-active {
  color: #409EFF;
}

/* 响应式设计 */
@media screen and (max-width: 768px) {
  .nav-menu {
    display: none;
  }

  .nav-toggle {
    display: flex;
  }

  .mobile-menu-overlay {
    display: none;
  }

  .mobile-menu-overlay[style*="display: block"] {
    display: flex !important;
  }
}
</style>
