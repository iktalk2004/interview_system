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
  background: #fff;
  width: 500px;
  max-width: 90vw;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  border: 1px solid #e0e0e0;
}

.modal-content h3 {
  margin: 0;
  padding: 16px 24px;
  background: linear-gradient(135deg, #2c3e50, #3498db);
  color: white;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.modal-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #bbb #f1f1f1;
}

.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 10px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #bbb;
  border-radius: 10px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.checkbox-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.checkbox-item:hover {
  background-color: #eaf2f8;
}

.checkbox-item input[type="checkbox"] {
  margin-right: 12px;
  accent-color: #3498db;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #fafafa;
}

.preference-group {
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.preference-group h4 {
  margin-top: 0;
  color: #2c3e50;
  font-weight: 600;
  margin-bottom: 12px;
}

.save-btn {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.save-btn:hover {
  background: #27ae60;
}

.cancel-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.cancel-btn:hover {
  background: #7f8c8d;
}
</style>
