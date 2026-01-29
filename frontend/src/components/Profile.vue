<template>
  <div class="profile-container">
    <h2>个人中心</h2>

    <div v-if="loading">加载中...</div>

    <div v-else class="profile-content">
      <!-- 用户基本信息卡片 -->
      <div class="info-card">
        <h3>基本信息</h3>
        <form @submit.prevent="updateProfile" class="info-form">
          <div class="form-group">
            <label>用户名</label>
            <input v-model="user.username" disabled class="disabled-input"/>
          </div>

          <div class="form-group">
            <label>邮箱</label>
            <input v-model="user.email" disabled class="disabled-input"/>
          </div>

          <div class="form-group">
            <label>个人简介</label>
            <textarea v-model="form.bio" placeholder="介绍一下自己吧" rows="4"></textarea>
          </div>

          <button type="submit" :disabled="updating" class="update-btn">
            {{ updating ? '更新中...' : '更新信息' }}
          </button>
        </form>
      </div>

      <!-- 技术偏好设置卡片 -->
      <div class="preference-card">
        <div class="card-header">
          <h3>技术偏好</h3>
          <button @click="openPreferenceModal" class="edit-preferences-btn">
            编辑偏好
          </button>
        </div>

        <div class="current-preferences">
          <div v-if="selectedPreferences && Object.keys(selectedPreferences).length > 0">
            <div v-for="[group, subs] in Object.entries(selectedPreferences)" :key="group" class="preference-group">
              <h4>{{ group }}</h4>
              <div class="tags-container">
                <span v-for="sub in subs" :key="sub" class="tag-item">{{ sub }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-preferences">
            <p>暂无技术偏好，请点击"编辑偏好"添加</p>
          </div>
        </div>
      </div>

      <!-- 操作区域 -->
      <div class="action-section">
        <button @click="logout" :disabled="loggingOut" class="logout-btn">
          {{ loggingOut ? '退出中...' : '退出登录' }}
        </button>
      </div>

      <!-- 提示信息 -->
      <div v-if="message" class="message success">{{ message }}</div>
      <div v-if="error" class="message error">{{ error }}</div>
    </div>

    <!-- 技术偏好编辑弹窗 -->
    <div v-if="showPreferenceModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>编辑技术偏好</h3>
        <div class="modal-body">
          <div
              v-for="group in preferenceOptions"
              :key="group.value"
              class="preference-group"
          >
            <h4>{{ group.label }}</h4>
            <div class="checkbox-grid">
              <label
                  v-for="child in group.children"
                  :key="child.value"
                  class="checkbox-item"
              >
                <input
                    type="checkbox"
                    :checked="isSelected(group.value, child.value)"
                    @change="togglePreference(group.value, child.value)"
                />
                {{ child.label }}
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="savePreferences" class="save-btn">保存</button>
          <button @click="closeModal" class="cancel-btn">取消</button>
        </div>
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
  email: '',
  bio: '',
  preferences: {}
})

const form = reactive({
  bio: '',
  preferences: ''
})

// 二级嵌套标签
const preferenceOptions = ref([
  {
    label: 'Python',
    value: 'Python',
    children: [
      {label: 'Python基础', value: 'Python基础'},
      {label: 'Python进阶', value: 'Python进阶'},
      {label: 'Flask专题', value: 'Flask专题'},
      {label: 'Django专题', value: 'Django专题'},
    ]
  },
  {
    label: '前端',
    value: '前端',
    children: [
      {label: 'Vue', value: 'Vue'},
      {label: 'React', value: 'React'},
      {label: 'JavaScript', value: 'JavaScript'},
    ]
  },
  {
    label: '后端',
    value: '后端',
    children: [
      {label: 'Node.js', value: 'Node.js'},
      {label: 'Java', value: 'Java'},
      {label: 'Spring Boot', value: 'Spring Boot'},
    ]
  },
  {
    label: '数据库',
    value: '数据库',
    children: [
      {label: 'MySQL', value: 'MySQL'},
      {label: 'PostgreSQL', value: 'PostgreSQL'},
      {label: 'MongoDB', value: 'MongoDB'},
    ]
  },
  {
    label: '算法与数据结构',
    value: '算法与数据结构',
    children: [
      {label: '排序算法', value: '排序算法'},
      {label: '树结构', value: '树结构'},
      {label: '图论', value: '图论'},
    ]
  }
]);

const selectedPreferences = ref({});
const tempSelectedPreferences = ref({}); // 临时存储弹窗中的选择
const showPreferenceModal = ref(false);

// 监听选择变化，自动转换为JSON格式存储
watch(selectedPreferences, (newVal) => {
  form.preferences = JSON.stringify(newVal);
}, {deep: true});

const loading = ref(true)
const updating = ref(false)
const loggingOut = ref(false)
const message = ref('')
const error = ref('')

// 检查选项是否被选中
const isSelected = (group, value) => {
  const current = tempSelectedPreferences.value[group] || [];
  return current.includes(value);
};

// 获取用户信息
const fetchProfile = async () => {
  try {
    const response = await api.get('users/profile/')
    Object.assign(user, response.data)
    form.bio = response.data.bio || ''
    // 解析现有的偏好设置，更新选中的复选框
    const existingPrefs = response.data.preferences || {};
    selectedPreferences.value = {...existingPrefs};
    form.preferences = JSON.stringify(selectedPreferences.value);
  } catch (err) {
    console.error('获取用户信息失败：', err)

    if (err.response?.status === 401) {
      error.value = '登录已过期，请重新登录'

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
  tempSelectedPreferences.value = JSON.parse(JSON.stringify(selectedPreferences.value || {}));
  showPreferenceModal.value = true;
};

// 保存偏好选择
const savePreferences = () => {
  selectedPreferences.value = JSON.parse(JSON.stringify(tempSelectedPreferences.value));
  showPreferenceModal.value = false;
};

// 关闭弹窗
const closeModal = () => {
  tempSelectedPreferences.value = JSON.parse(JSON.stringify(selectedPreferences.value || {}));
  showPreferenceModal.value = false;
};

// 切换单个偏好的选中状态
const togglePreference = (group, value) => {
  const current = tempSelectedPreferences.value[group] || [];
  if (current.includes(value)) {
    tempSelectedPreferences.value[group] = current.filter(v => v !== value);
  } else {
    tempSelectedPreferences.value[group] = [...current, value];
  }
};

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
/* 现代极简设计：sans-serif字体、充足空白、平坦无阴影、细边框 */
/* 蓝色调：主蓝 #409EFF，浅蓝 #E6F7FF，深灰文本 #303133 */

.profile-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.profile-content {
  display: grid;
  gap: 24px;
}

.info-card, .preference-card {
  background-color: #FFFFFF;
  border: 1px solid #DCDFE6;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

h2 {
  font-size: 24px;
  font-weight: normal;
  color: #303133;
  margin-bottom: 24px;
  text-align: center;
}

h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}

h4 {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin: 0 0 8px 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

input, textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  background-color: #FAFAFA;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

input:focus, textarea:focus {
  outline: none;
  border-color: #409EFF;
  background-color: #FFFFFF;
}

input:disabled, .disabled-input {
  background-color: #F5F7FA;
  cursor: not-allowed;
  color: #C0C4CC;
}

.update-btn, .edit-preferences-btn, .save-btn, .cancel-btn, .logout-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  box-sizing: border-box;
}

.update-btn, .edit-preferences-btn {
  background-color: #409EFF;
  color: #FFFFFF;
}

.update-btn:hover, .edit-preferences-btn:hover {
  background-color: #66B1FF;
}

.update-btn:disabled, .edit-preferences-btn:disabled {
  background-color: #A0A0A0;
  cursor: not-allowed;
}

.current-preferences {
  margin-top: 16px;
}

.no-preferences {
  color: #909399;
  font-style: italic;
  padding: 16px 0;
}

.preference-group {
  margin-bottom: 16px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  background-color: #ECF5FF;
  color: #409EFF;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  border: 1px solid #D9ECFF;
}

.action-section {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.logout-btn {
  padding: 12px 24px;
  background-color: #F56C6C;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.logout-btn:hover {
  background-color: #F78989;
}

.logout-btn:disabled {
  background-color: #F3B4B4;
  cursor: not-allowed;
}

.message {
  padding: 12px;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
  margin-top: 16px;
}

.message.success {
  background-color: #F0F9EB;
  color: #67C23A;
  border: 1px solid #E1F3D8;
}

.message.error {
  background-color: #FEF0F0;
  color: #F56C6C;
  border: 1px solid #FDE2E2;
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
  background: #FFFFFF;
  width: 600px;
  max-width: 90vw;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin: 0;
  padding: 16px 24px;
  background-color: #409EFF;
  color: #FFFFFF;
  font-size: 18px;
}

.modal-body {
  padding: 20px 24px;
  max-height: 500px;
  overflow-y: auto;
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: #F2F6FC;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #DCDFE6;
  border-radius: 3px;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
  margin-bottom: 16px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.checkbox-item:hover {
  background-color: #F2F6FC;
}

.checkbox-item input[type="checkbox"] {
  margin-right: 8px;
  accent-color: #409EFF;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #DCDFE6;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #F2F6FC;
}

.save-btn {
  background-color: #409EFF;
  color: #FFFFFF;
}

.save-btn:hover {
  background-color: #66B1FF;
}

.cancel-btn {
  background-color: #909399;
  color: #FFFFFF;
}

.cancel-btn:hover {
  background-color: #A0A0A0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .profile-container {
    margin: 20px auto;
    padding: 0 15px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .checkbox-grid {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 95vw;
  }
}
</style>
