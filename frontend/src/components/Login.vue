<template>
  <div class="auth-container">
    <h2>登录</h2>
    <form @submit.prevent="login">
      <input v-model="form.username" placeholder="用户名" required/>
      <input v-model="form.password" type="password" placeholder="密码" required/>
      <button type="submit" :disabled="loading">登录</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <p class="register-link">
      没有账号？
      <router-link to="/register">去注册</router-link>
    </p>
  </div>
</template>

<script setup>
import {reactive, ref} from 'vue'
import {useRouter, useRoute} from 'vue-router'
import api from '@/api.js'

const router = useRouter();
const route = useRoute();  // 获取当前路由
const form = reactive({
  username: '',
  password: '',
});

const loading = ref(false);
const error = ref('');

const login = async () => {
  loading.value = true;
  error.value = '';

  try {
    const response = await api.post('users/login/', {...form})

    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);

    alert('登录成功')
    const redirectPath = route.query.redirect || '/profile';  // 跳转到登录前的页面路径或默认首页
    router.push(redirectPath)
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 现代极简设计：sans-serif字体、充足空白、平坦无阴影、细边框 */
/* 蓝色调：主蓝 #409EFF，浅蓝 #E6F7FF，深灰文本 #303133 */

.auth-container {
  max-width: 400px;
  margin: 100px auto 0; /* 增加顶部margin，创建垂直居中感 */
  padding: 40px;
  background-color: #FFFFFF; /* 白背景 */
  border: 1px solid #DCDFE6; /* 浅灰细边框 */
  border-radius: 4px; /* 小圆角 */
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; /* 现代字体 */
  text-align: center; /* 居中对齐 */
}

h2 {
  font-size: 24px;
  font-weight: normal; /* 非粗体，极简 */
  color: #303133; /* 深灰标题 */
  margin-bottom: 32px; /* 增加间距 */
}

form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

input {
  width: 100%;
  padding: 12px 16px;
  margin-bottom: 24px; /* 增加输入框间距 */
  border: 1px solid #DCDFE6; /* 浅灰边框 */
  border-radius: 4px;
  font-size: 14px;
  color: #606266; /* 常规文本色 */
  background-color: #F2F6FC; /* 浅蓝灰背景 */
  transition: border-color 0.3s ease;
}

input:focus {
  border-color: #409EFF; /* 焦点时蓝边框 */
  outline: none;
}

button {
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

button:hover {
  background-color: #66B1FF; /* 浅蓝hover */
}

button:disabled {
  background-color: #A0CFFF; /* 禁用浅蓝 */
  cursor: not-allowed;
}

.error {
  color: #F56C6C; /* 红色错误，但保持极简 */
  font-size: 12px;
  margin-top: 12px;
  text-align: left;
  width: 100%;
}

.register-link {
  margin-top: 24px;
  font-size: 14px;
  color: #909399; /* 次要灰文本 */
}

.register-link a {
  color: #409EFF; /* 蓝链接 */
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}

/* 响应式调整：移动端保持极简 */
@media (max-width: 768px) {
  .auth-container {
    margin: 60px auto 0;
    padding: 30px;
  }
}
</style>