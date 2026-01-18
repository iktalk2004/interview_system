<template>
  <div class="profile-container">
    <h2>个人信息</h2>

    <div v-if="loading">加载中...</div>

    <form v-else @submit.prevent="updateProfile">
      <div class="form-group">
        <label>用户名</label>
        <input v-model="user.username" disabled/>
      </div>

      <div class="form-group">
        <label>Bio</label>
        <textarea v-model="form.bio" placeholder="介绍一下自己吧"></textarea>
      </div>

      <div class="form-group">
        <label>偏好设置（JSON格式）</label>
        <textarea v-model="form.preferences" rows="4" placeholder='{"tags": ["Spring", "MySQL", "算法"]}'></textarea>
      </div>

      <button type="submit" :disabled="updating">保存修改</button>
      <p v-if="message" class="success">{{ message }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>

    <button class="logout-btn" @click="logout" :disabled="loggingOut">
      {{ loggingOut ? '注销中...' : '退出登录' }}
    </button>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted} from 'vue'
import {useRouter} from 'vue-router'
import api from '@/api.js'

const router = useRouter()

const user = reactive({
  username: '',
  bio: '',
  preferences: {}
})

const form = reactive({
  bio: '',
  preferences: ''
})

const loading = ref(true)
const updating = ref(false)
const loggingOut = ref(false)
const message = ref('')
const error = ref('')

// 获取用户信息
const fetchProfile = async () => {
  try {
    const response = await api.get('profile/')
    Object.assign(user, response.data)
    form.bio = response.data.bio || ''
    form.preferences = JSON.stringify(response.data.preferences || {}, null, 2)
  } catch (err) {
    error.value = '获取个人信息失败，请重新登录'
    router.push('/login')
  } finally {
    loading.value = false
  }
}

const updateProfile = async () => {
  updating.value = true
  message.value = ''
  error.value = ''

  try {
    let preferencesData
    try {
      preferencesData = JSON.parse(form.preferences)
    } catch {
      throw new Error('偏好格式错误，请输入有效的JSON')
    }

    await api.put('profile/', {
      bio: form.bio,
      preferences: preferencesData
    })

    message.value = '个人信息更新成功'
    user.bio = form.bio
    user.preferences = preferencesData
  } catch (err) {
    error.value = err.message || '更新失败，请稍后重试'
  } finally {
    updating.value = false
  }
}

const logout = async () => {
  loggingOut.value = true

  try {
    await api.post('logout/')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
  } catch (err) {
    console.warn('注销请求失败，但已清除本地token', err)
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/login')
  } finally {
    loggingOut.value = false
  }
}

// 组件挂载时获取信息
onMounted(() => {
  fetchProfile()
})
</script>

<style scoped>
.profile-container {
  max-width: 500px;
  margin: 40px auto;
  padding: 30px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
}

textarea, input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.logout-btn {
  margin-top: 30px;
  background: #e74c3c;
  color: white;
  width: 100%;
}

.success {
  color: #27ae60;
  margin-top: 10px;
}

.error {
  color: #e74c3c;
  margin-top: 10px;
}
</style>