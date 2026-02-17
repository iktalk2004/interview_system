<template>
  <div class="register-container">
    <div class="matrix-bg"></div>
    
    <div class="register-wrapper">
      <div class="terminal-window">
        <div class="terminal-header">
          <div class="terminal-dots">
            <div class="dot red"></div>
            <div class="dot yellow"></div>
            <div class="dot green"></div>
          </div>
          <div class="terminal-title code-font">register.sh</div>
        </div>
        
        <div class="terminal-body">
          <div class="terminal-output">
            <div class="output-line">
              <span class="prompt-symbol">$</span>
              <span class="command">npm install interview_system</span>
            </div>
            <div class="output-line">
              <span class="prompt-symbol">$</span>
              <span class="command">waiting for credentials...</span>
            </div>
          </div>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="register-form"
            @submit.prevent="handleRegister"
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
              <label class="input-label code-font">email:</label>
              <el-form-item prop="email">
                <el-input
                  v-model="form.email"
                  placeholder="Enter email"
                  size="large"
                  clearable
                  class="code-input"
                >
                  <template #prefix>
                    <el-icon class="input-icon"><Message /></el-icon>
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
                class="register-button code-font"
                @click="handleRegister"
              >
                <span v-if="!loading">&gt; EXECUTE REGISTER</span>
                <span v-else>PROCESSING...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="register-footer">
            <span class="footer-text code-font">Already have an account?</span>
            <router-link to="/login" class="login-link code-font">
              &lt;Login/&gt;
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="code-decoration">
      <div class="code-line">
        <span class="code-keyword">import</span>
        <span class="code-variable">{</span>
        <span class="code-variable">User</span>
        <span class="code-variable">}</span>
        <span class="code-keyword">from</span>
        <span class="code-string">'@models'</span>
      </div>
      <div class="code-line">
        <span class="code-keyword">const</span>
        <span class="code-variable">newUser</span>
        <span class="code-operator">=</span>
        <span class="code-keyword">new</span>
        <span class="code-function">User</span>
        <span class="code-bracket">()</span>
      </div>
      <div class="code-line">
        <span class="code-keyword">await</span>
        <span class="code-variable">newUser</span>
        <span class="code-operator">.</span>
        <span class="code-function">save</span>
        <span class="code-bracket">()</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Lock } from '@element-plus/icons-vue'
import api from '@/api'

const router = useRouter()
const formRef = ref(null)

const form = reactive({
  username: '',
  email: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: 'Username required', trigger: 'blur' },
    { min: 3, max: 20, message: '3-20 characters', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Email required', trigger: 'blur' },
    { type: 'email', message: 'Invalid email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password required', trigger: 'blur' },
    { min: 6, message: 'At least 6 characters', trigger: 'blur' }
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
    await api.post('/users/register/', { ...form })
    ElMessage.success('Registration successful')
    router.push('/login')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || 'Registration failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
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

.register-wrapper {
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
  border-left: 3px solid var(--accent-primary);
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

.register-form {
  margin-bottom: 20px;
}

.register-form :deep(.el-form-item) {
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

.register-button {
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

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.register-button:active {
  transform: translateY(0);
}

.register-footer {
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

.login-link {
  font-size: 13px;
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.login-link:hover {
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
  .register-container {
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
