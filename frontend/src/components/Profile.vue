<template>
  <div class="profile-container">
    <h2>个人信息</h2>

    <div v-if="loading">加载中...</div>

    <form v-else @submit.prevent="updateProfile">
      <!-- 显示用户名 -->
      <div class="form-group">
        <label>用户名</label>
        <input v-model="user.username" disabled/>
      </div>

      <!-- 填写bio -->
      <div class="form-group">
        <label>Bio</label>
        <textarea v-model="form.bio" placeholder="介绍一下自己吧"></textarea>
      </div>

      <!-- 显示现有技术偏好 -->
      <div class="form-group">
        <label>技术偏好</label>
        <div class="current-preferences">
          <div v-if="selectedPreferences && Object.keys(selectedPreferences).length > 0">
            <div v-for="[group, subs] in Object.entries(selectedPreferences)" :key="group">
              <span class="tag-group">{{ group }}：</span>
              <span v-for="sub in subs" :key="sub" class="tag-item">{{ sub }}</span>
            </div>
          </div>
          <span v-else class="no-tags">暂无技术偏好</span>
        </div>

        <!-- 编辑技术偏好按钮 -->
        <button
            type="button"
            @click="openPreferenceModal"
            class="edit-preferences-btn"
        >编辑技术偏好
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
        <div v-for="group in preferenceOptions" :key="group.value" class="preference-group">
          <h4>{{ group.label }}</h4>
          <div class="sub-checkboxes">
            <label v-for="child in group.children" :key="child.value" class="checkbox-item">
              <input
                  type="checkbox"
                  :checked="tempSelectedPreferences[group.value]?.includes(child.value) || false"
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
  // ... 其他组：算法与数据结构、数据库、Java、Spring 等
  // 可以后期从后端接口动态加载
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
  max-width: 500px;
  margin: 100px auto 0; /* 增加顶部margin，创建垂直居中感 */
  padding: 40px;
  background-color: #FFFFFF; /* 白背景 */
  border: 1px solid #DCDFE6; /* 浅灰细边框 */
  border-radius: 4px; /* 小圆角 */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; /* 现代字体 */
  text-align: left; /* 左对齐 */
}

h2 {
  font-size: 24px;
  font-weight: normal; /* 非粗体，极简 */
  color: #303133; /* 深灰标题 */
  margin-bottom: 32px; /* 增加间距 */
  text-align: center; /* 标题居中 */
}

.form-group {
  margin-bottom: 24px; /* 增加间距 */
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266; /* 常规文本色 */
}

input,
textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #DCDFE6; /* 浅灰边框 */
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  background-color: #F2F6FC; /* 浅蓝灰背景 */
  transition: border-color 0.3s ease;
}

input:disabled {
  background-color: #F5F7FA; /* 禁用灰背景 */
  color: #909399; /* 次要文本 */
}

input:focus,
textarea:focus {
  border-color: #409EFF; /* 焦点蓝边框 */
  outline: none;
}

textarea {
  min-height: 80px;
  resize: vertical;
}

.current-preferences {
  min-height: 40px;
  padding: 12px;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  background-color: #F2F6FC; /* 浅蓝灰背景 */
}

.tag-group {
  font-weight: normal;
  color: #909399; /* 次要灰 */
}

.tag-item {
  background-color: #409EFF; /* 蓝标签 */
  color: #FFFFFF;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  margin-right: 8px;
}

.no-tags {
  color: #909399;
  font-size: 14px;
  font-style: normal;
}

.edit-preferences-btn {
  width: 100%;
  padding: 12px;
  background-color: #409EFF; /* 主蓝按钮 */
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.edit-preferences-btn:hover {
  background-color: #66B1FF; /* 浅蓝hover */
}

.logout-btn {
  width: 100%;
  padding: 12px;
  background-color: #F56C6C; /* 红注销按钮，保持区分 */
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  margin-top: 32px;
  transition: background-color 0.3s ease;
}

.logout-btn:hover {
  background-color: #F78989; /* 浅红hover */
}

.success {
  color: #67C23A; /* 绿成功 */
  font-size: 12px;
  margin-top: 12px;
  text-align: center;
}

.error {
  color: #F56C6C; /* 红错误 */
  font-size: 12px;
  margin-top: 12px;
  text-align: center;
}

/* 弹窗样式 - 极简版 */
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
  width: 500px;
  max-width: 90vw;
  border-radius: 4px; /* 小圆角 */
  overflow: hidden;
  box-shadow: none; /* 无阴影，极简 */
  border: 1px solid #DCDFE6; /* 细边框 */
}

.modal-content h3 {
  margin: 0;
  padding: 16px 24px;
  background-color: #409EFF; /* 蓝头部 */
  color: #FFFFFF;
  font-size: 18px;
  font-weight: normal;
}

.modal-body {
  padding: 20px;
  max-height: 400px;
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
}

.checkbox-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.checkbox-item:hover {
  background-color: #E6F7FF; /* 浅蓝hover */
}

.checkbox-item input[type="checkbox"] {
  margin-right: 12px;
  accent-color: #409EFF; /* 蓝checkbox */
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #DCDFE6;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #F2F6FC; /* 浅蓝灰背景 */
}

.preference-group {
  margin-bottom: 20px;
  padding: 0;
  border: none; /* 移除边框，极简 */
}

.preference-group h4 {
  margin-top: 0;
  color: #303133;
  font-weight: normal;
  margin-bottom: 12px;
  font-size: 16px;
}

.save-btn {
  padding: 10px 20px;
  background-color: #409EFF; /* 主蓝 */
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.save-btn:hover {
  background-color: #66B1FF;
}

.cancel-btn {
  padding: 10px 20px;
  background-color: #909399; /* 灰取消 */
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.cancel-btn:hover {
  background-color: #A0A0A0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .profile-container {
    margin: 60px auto 0;
    padding: 30px;
  }

  .modal-content {
    width: 100%;
    max-width: none;
  }
}
</style>