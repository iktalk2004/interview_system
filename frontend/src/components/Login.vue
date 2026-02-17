<template>
  <div class="login-container">
    <div class="matrix-bg"></div>
    
    <div class="login-wrapper">
      <div class="terminal-window">
        <div class="terminal-header">
          <div class="terminal-dots">
            <div class="dot red"></div>
            <div class="dot yellow"></div>
            <div class="dot green"></div>
          </div>
          <div class="terminal-title code-font">login.sh</div>
        </div>
        
        <div class="terminal-body">
          <div class="terminal-output">
            <div class="output-line">
              <span class="prompt-symbol">$</span>
              <span class="command">init interview_system</span>
            </div>
            <div class="output-line success">
              <span class="success-symbol">✓</span>
              <span>System initialized successfully</span>
            </div>
            <div class="output-line">
              <span class="prompt-symbol">$</span>
              <span class="command">waiting for user input...</span>
            </div>
          </div>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <div class="input-group">
              <label class="input-label code-font">username:</label>
              <el-form-item prop="username">
                <el-input
                  v-model="form.username"
                  placeholder="Enter username"
                  size="large"
                  clearable
                  class="code-input"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <div class="input-group">
              <label class="input-label code-font">password:</label>
              <el-form-item prop="password">
                <el-input
                  v-model="form.password"
                  type="password"
                  placeholder="Enter password"
                  size="large"
                  show-password
                  class="code-input"
                  @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="login-button code-font"
                @click="handleLogin"
              >
                <span v-if="!loading">&gt; EXECUTE LOGIN</span>
                <span v-else>PROCESSING...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="login-footer">
            <span class="footer-text code-font">New user?</span>
            <router-link to="/register" class="register-link code-font">
              &lt;Register/&gt;
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="code-decoration">
      <div class="code-line">
        <span class="code-keyword">const</span>
        <span class="code-variable">user</span>
        <span class="code-operator">=</span>
        <span class="code-string">'{{ form.username || 'developer' }}'</span>
      </div>
      <div class="code-line">
        <span class="code-keyword">const</span>
        <span class="code-variable">status</span>
        <span class="code-operator">=</span>
        <span class="code-string">'waiting'</span>
      </div>
      <div class="code-line">
        <span class="code-keyword">await</span>
        <span class="code-function">login</span>
        <span class="code-bracket">(</span>
        <span class="code-variable">user</span>
        <span class="code-bracket">)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const route = useRoute()
const formRef = ref(null)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: 'Username required', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password required', trigger: 'blur' }
  ]
}

const loading = ref(false)

const handleLogin = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const response = await api.post('/users/login/', { ...form })
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    
    const userData = {
      username: form.username
    }
    localStorage.setItem('user_data', JSON.stringify(userData))

    ElMessage.success('Login successful')
    const redirectPath = route.query.redirect || '/'
    router.push(redirectPath)
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Login failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
  padding: 20px;
}

.matrix-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(ellipse at top, rgba(137, 180, 250, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at bottom, rgba(245, 194, 231, 0.05) 0%, transparent 50%),
    linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  z-index: 0;
}

.login-wrapper {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 500px;
}

.terminal-window {
  background: var(--code-bg);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.terminal-dots {
  display: flex;
  gap: 8px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.red {
  background: var(--accent-error);
}

.dot.yellow {
  background: var(--accent-warning);
}

.dot.green {
  background: var(--accent-success);
}

.terminal-title {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 600;
}

.terminal-body {
  padding: 24px;
}

.terminal-output {
  margin-bottom: 24px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--accent-success);
}

.output-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-family: var(--font-mono);
  font-size: 13px;
  color: var(--code-text);
}

.output-line:last-child {
  margin-bottom: 0;
}

.prompt-symbol {
  color: var(--accent-success);
  font-weight: 600;
}

.command {
  color: var(--accent-primary);
}

.output-line.success {
  color: var(--accent-success);
}

.success-symbol {
  color: var(--accent-success);
  font-weight: 600;
}

.login-form {
  margin-bottom: 20px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.input-group {
  margin-bottom: 8px;
}

.input-label {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 600;
  letter-spacing: 0.5px;
}

.code-input :deep(.el-input__wrapper) {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
}

.code-input :deep(.el-input__wrapper:hover) {
  border-color: var(--accent-primary);
}

.code-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px rgba(137, 180, 250, 0.2);
}

.code-input :deep(.el-input__inner) {
  color: var(--text-primary);
  background: transparent;
  font-family: var(--font-mono);
}

.code-input :deep(.el-input__inner::placeholder) {
  color: var(--text-muted);
}

.input-icon {
  color: var(--text-muted);
  font-size: 18px;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  border: none;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.login-button:active {
  transform: translateY(0);
}

.login-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.footer-text {
  font-size: 13px;
  color: var(--text-muted);
}

.register-link {
  font-size: 13px;
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.register-link:hover {
  color: var(--accent-secondary);
  text-decoration: underline;
}

.code-decoration {
  position: absolute;
  top: 50%;
  right: 5%;
  transform: translateY(-50%);
  z-index: 5;
  opacity: 0.3;
  font-family: var(--font-mono);
  font-size: 14px;
  line-height: 2;
}

.code-line {
  margin-bottom: 4px;
}

.code-keyword {
  color: var(--code-keyword);
}

.code-variable {
  color: var(--accent-primary);
}

.code-operator {
  color: var(--text-muted);
}

.code-string {
  color: var(--code-string);
}

.code-function {
  color: var(--accent-secondary);
}

.code-bracket {
  color: var(--text-muted);
}

@media (max-width: 1200px) {
  .code-decoration {
    display: none;
  }
}

@media (max-width: 768px) {
  .login-container {
    padding: 16px;
  }

  .terminal-body {
    padding: 20px;
  }

  .terminal-output {
    padding: 12px;
  }
}
</style>
