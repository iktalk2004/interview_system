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

      <!-- 显示现有技术偏好 -->
      <div class="form-group">
        <label>技术偏好</label>
        <div class="current-preferences">
          <span
              v-for="tag in selectedPreferences"
              :key="tag"
              class="tag-item"
          >
            {{ tag }}
          </span>
          <span v-if="selectedPreferences.length === 0" class="no-tags">暂无技术偏好</span>
        </div>
        <button
            type="button"
            @click="showPreferenceModal = true"
            class="edit-preferences-btn"
        >
          编辑技术偏好
        </button>
      </div>

      <button type="submit" :disabled="updating">保存修改</button>
      <p v-if="message" class="success">{{ message }}</p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>

    <button class="logout-btn" @click="logout" :disabled="loggingOut">
      {{ loggingOut ? '注销中...' : '退出登录' }}
    </button>
  </div>

  <!-- 技术偏好编辑弹窗 -->
  <div v-if="showPreferenceModal" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <h3>编辑技术偏好</h3>
      <div class="modal-body">
        <div class="checkbox-group">
          <label v-for="option in preferenceOptions" :key="option.value" class="checkbox-item">
            <input
                type="checkbox"
                :value="option.value"
                v-model="tempSelectedPreferences"
            />
            {{ option.label }}
          </label>
        </div>
      </div>
      <div class="modal-footer">
        <button @click="savePreferences" class="save-btn">保存</button>
        <button @click="closeModal" class="cancel-btn">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, onMounted, watch} from 'vue'
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

// 预设选项
const preferenceOptions = [
  {value: 'Java', label: 'Java'},
  {value: 'Python', label: 'Python'},
  {value: 'JavaScript', label: 'JavaScript'},
  {value: 'Spring', label: 'Spring'},
  {value: 'Django', label: 'Django'},
  {value: 'Vue', label: 'Vue'},
  {value: 'React', label: 'React'},
  {value: 'MySQL', label: 'MySQL'},
  {value: 'PostgreSQL', label: 'PostgreSQL'},
  {value: '算法', label: '算法'},
  {value: '数据结构', label: '数据结构'},
  {value: '微服务', label: '微服务'}
];

const selectedPreferences = ref([]);
const tempSelectedPreferences = ref([]); // 临时存储弹窗中的选择
const showPreferenceModal = ref(false);

// 监听选择变化，自动转换为JSON格式存储
watch(selectedPreferences, (newVal) => {
  form.preferences = JSON.stringify({tags: newVal});
}, {deep: true});

const loading = ref(true)
const updating = ref(false)
const loggingOut = ref(false)
const message = ref('')
const error = ref('')

// 获取用户信息
const fetchProfile = async () => {
  try {
    const response = await api.get('users/profile/')
    Object.assign(user, response.data)
    form.bio = response.data.bio || ''
    // 解析现有的偏好设置，更新选中的复选框
    const existingPrefs = response.data.preferences || {};
    selectedPreferences.value = existingPrefs.tags || [];
    form.preferences = JSON.stringify(existingPrefs);
  } catch (err) {
    console.error('获取用户信息失败：', err)

    if (err.response?.status === 401) {
      err.value = '登录已过期，请重新登录'

      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')

      // 延迟跳转，让用户看到错误提示
      setTimeout(() => {
        router.push('/login');
      }, 1500);
    } else {
      error.value = '获取用户信息失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

// 打开偏好编辑弹窗
const openPreferenceModal = () => {
  // 将当前选择复制到临时变量
  tempSelectedPreferences.value = [...selectedPreferences.value];
  showPreferenceModal.value = true;
}

// 保存偏好选择
const savePreferences = () => {
  // 更新主数组
  selectedPreferences.value = [...tempSelectedPreferences.value];
  showPreferenceModal.value = false;
}

// 关闭弹窗
const closeModal = () => {
  // 恢复临时选择到当前选择，避免意外更改
  tempSelectedPreferences.value = [...selectedPreferences.value];
  showPreferenceModal.value = false;
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

    await api.patch('users/profile/', {
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
    await api.post('users/logout/')
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
  // 此处可添加处理路由守卫漏掉的极端情况，避免卡死界面
  fetchProfile()
})

// 为模板提供方法访问
defineExpose({
  openPreferenceModal,
  savePreferences,
  closeModal
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

.current-preferences {
  min-height: 30px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
}

.tag-item {
  background: #3498db;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.no-tags {
  color: #999;
  font-style: italic;
}

.edit-preferences-btn {
  background: #9b59b6;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
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

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 500px;
  max-width: 90vw;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  margin: 0;
  padding: 15px 20px;
  background: #34495e;
  color: white;
  font-size: 18px;
}

.modal-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.checkbox-item input {
  margin-right: 8px;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.save-btn, .cancel-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background: #2ecc71;
  color: white;
}

.cancel-btn {
  background: #95a5a6;
  color: white;
}
</style>