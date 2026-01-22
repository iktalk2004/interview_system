<template>
  <div class="auth-container">
    <h2>注册</h2>
    <form @submit.prevent="register">
      <input v-model="form.username" placeholder="用户名" required/>
      <input v-model="form.email" type="email" placeholder="邮箱" required/>
      <input v-model="form.password" type="password" placeholder="密码" required/>
      <button type="submit" :disabled="loading">注册</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import {reactive, ref} from 'vue';
import {useRouter} from 'vue-router'
import api from '@/api.js'

const router = useRouter();
const form = reactive({
  username: '',
  email: '',
  password: '',
});

const loading = ref(false);
const error = ref('');

const register = async () => {
  loading.value = true;  // 开始加载
  error.value = '';

  try {
    await api.post('users/register/', {...form});
    alert('注册成功,请登录')
    router.push('/login');
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败，请稍后再试'
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
</style>