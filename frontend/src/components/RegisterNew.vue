<template>
  <div class="register-page">
    <div class="left-panel">
      <div class="decoration-bg"></div>
      <div class="illustration">
        <svg viewBox="0 0 400 400" class="illustration-svg">
          <defs>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#94A3B8;stop-opacity:0.8" />
              <stop offset="100%" style="stop-color:#64748B;stop-opacity:0.4" />
            </linearGradient>
          </defs>
          <circle cx="200" cy="200" r="150" fill="none" stroke="#E2E8F0" stroke-width="1" />
          <circle cx="200" cy="200" r="100" fill="none" stroke="#E2E8F0" stroke-width="1" />
          <circle cx="200" cy="200" r="50" fill="none" stroke="#CBD5E1" stroke-width="1.5" />
          <line x1="200" y1="50" x2="200" y2="350" stroke="url(#lineGradient)" stroke-width="1" />
          <line x1="50" y1="200" x2="350" y2="200" stroke="url(#lineGradient)" stroke-width="1" />
          <line x1="93" y1="93" x2="307" y2="307" stroke="url(#lineGradient)" stroke-width="1" />
          <line x1="307" y1="93" x2="93" y2="307" stroke="url(#lineGradient)" stroke-width="1" />
          <circle cx="200" cy="200" r="8" fill="#64748B" />
          <circle cx="200" cy="50" r="4" fill="#94A3B8" />
          <circle cx="200" cy="350" r="4" fill="#94A3B8" />
          <circle cx="50" cy="200" r="4" fill="#94A3B8" />
          <circle cx="350" cy="200" r="4" fill="#94A3B8" />
          <circle cx="93" cy="93" r="3" fill="#CBD5E1" />
          <circle cx="307" cy="307" r="3" fill="#CBD5E1" />
          <circle cx="307" cy="93" r="3" fill="#CBD5E1" />
          <circle cx="93" cy="307" r="3" fill="#CBD5E1" />
          <text x="180" y="205" font-family="monospace" font-size="10" fill="#64748B">&lt;/&gt;</text>
          <text x="120" y="140" font-family="monospace" font-size="8" fill="#94A3B8">{ }</text>
          <text x="270" y="140" font-family="monospace" font-size="8" fill="#94A3B8">[ ]</text>
          <text x="120" y="270" font-family="monospace" font-size="8" fill="#94A3B8">func()</text>
          <text x="265" y="270" font-family="monospace" font-size="8" fill="#94A3B8">=&gt;</text>
        </svg>
      </div>
    </div>

    <div class="right-panel">
      <div class="register-container">
        <div class="logo-section">
          <h1 class="logo">八股炉</h1>
          <p class="subtitle">智能题目推荐 · 协同过滤驱动</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="register-form"
          @submit.prevent="handleRegister"
        >
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-input
                v-model="form.username"
                placeholder="用户名"
                class="custom-input"
                clearable
              />
              <div class="input-border"></div>
            </div>
          </el-form-item>

          <el-form-item prop="email">
            <div class="input-wrapper">
              <el-input
                v-model="form.email"
                placeholder="邮箱"
                class="custom-input"
                clearable
              />
              <div class="input-border"></div>
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="密码"
                class="custom-input"
                show-password
              />
              <div class="input-border"></div>
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <div class="input-wrapper">
              <el-input
                v-model="form.confirmPassword"
                type="password"
                placeholder="确认密码"
                class="custom-input"
                show-password
                @keyup.enter="handleRegister"
              />
              <div class="input-border"></div>
            </div>
          </el-form-item>

          <el-form-item class="button-item">
            <el-button
              type="primary"
              :loading="loading"
              class="register-button"
              @click="handleRegister"
            >
              注册
            </el-button>
          </el-form-item>

          <div class="divider">
            <span class="divider-text">或</span>
          </div>

          <el-form-item class="button-item">
            <el-button class="github-button">
              <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              GitHub 注册
            </el-button>
          </el-form-item>
        </el-form>

        <div class="footer">
          <span class="footer-text">已有账号？</span>
          <router-link to="/login" class="login-link">立即登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const formRef = ref(null)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const loading = ref(false)

const handleRegister = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await api.post('/users/register/', {
      username: form.username,
      email: form.email,
      password: form.password
    })
    ElMessage.success('注册成功')
    router.push('/login')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  display: flex;
  min-height: 100vh;
  background: #FFFFFF;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'HarmonyOS Sans', 'Microsoft YaHei', sans-serif;
}

.left-panel {
  width: 33.333%;
  position: relative;
  background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.decoration-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 30% 30%, rgba(148, 163, 184, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 70% 70%, rgba(100, 116, 139, 0.05) 0%, transparent 50%);
}

.illustration {
  position: relative;
  z-index: 1;
  width: 320px;
  height: 320px;
}

.illustration-svg {
  width: 100%;
  height: 100%;
}

.right-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.register-container {
  width: 100%;
  max-width: 420px;
}

.logo-section {
  margin-bottom: 48px;
  text-align: center;
}

.logo {
  font-size: 32px;
  font-weight: 700;
  color: #0F172A;
  margin: 0 0 12px 0;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 14px;
  color: #64748B;
  margin: 0;
  font-weight: 400;
}

.register-form {
  margin-bottom: 32px;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.register-form :deep(.el-form-item.button-item) {
  margin-bottom: 20px;
}

.input-wrapper {
  position: relative;
}

.custom-input :deep(.el-input__wrapper) {
  padding: 12px 16px;
  background: transparent;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  box-shadow: none;
  transition: border-color 0.2s ease;
}

.custom-input :deep(.el-input__wrapper:hover) {
  border-color: #CBD5E1;
}

.custom-input :deep(.el-input__wrapper.is-focus) {
  border-color: #3B82F6;
}

.custom-input :deep(.el-input__inner) {
  color: #0F172A;
  font-size: 15px;
  line-height: 1.5;
  background: transparent;
}

.custom-input :deep(.el-input__inner::placeholder) {
  color: #94A3B8;
}

.input-border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #3B82F6;
  transform: scaleX(0);
  transition: transform 0.2s ease;
}

.input-wrapper:focus-within .input-border {
  transform: scaleX(1);
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  background: #1E293B;
  border: none;
  border-radius: 8px;
  color: #FFFFFF;
  transition: all 0.2s ease;
}

.register-button:hover {
  background: #334155;
  transform: translateY(-1px);
}

.register-button:active {
  transform: translateY(0);
}

.register-button.is-loading {
  opacity: 0.7;
}

.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: #94A3B8;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #E2E8F0;
}

.divider-text {
  padding: 0 16px;
  font-size: 13px;
  color: #94A3B8;
}

.github-button {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 500;
  background: transparent;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.github-button:hover {
  background: #F8FAFC;
  border-color: #CBD5E1;
  color: #0F172A;
}

.github-icon {
  width: 20px;
  height: 20px;
}

.footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #E2E8F0;
}

.footer-text {
  font-size: 14px;
  color: #64748B;
  margin-right: 4px;
}

.login-link {
  font-size: 14px;
  color: #3B82F6;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.login-link:hover {
  color: #2563EB;
  text-decoration: underline;
}

@media (max-width: 1024px) {
  .left-panel {
    display: none;
  }

  .right-panel {
    padding: 24px;
  }

  .register-container {
    max-width: 400px;
  }
}

@media (max-width: 640px) {
  .right-panel {
    padding: 20px;
  }

  .logo {
    font-size: 28px;
  }

  .subtitle {
    font-size: 13px;
  }
}
</style>
