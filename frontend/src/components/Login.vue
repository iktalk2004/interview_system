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
.auth-container {
  max-width: 400px;
  margin: 60px auto;
  padding: 30px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.error {
  color: #e74c3c;
  margin-top: 10px;
}

.register-link {
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
}

.register-link a {
  color: #3498db;
  text-decoration: none;
}

.register-link a:hover {
  text-decoration: underline;
}
</style>
