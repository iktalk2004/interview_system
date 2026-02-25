import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || '')
  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    try {
      const response = await api.post('users/login/', { username, password })
      token.value = response.data.access
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      user.value = response.data.user
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function register(username, email, password) {
    try {
      const response = await api.post('users/register/', { username, email, password })
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function fetchProfile() {
    try {
      const response = await api.get('users/profile/')
      user.value = response.data
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function updateProfile(data) {
    try {
      const response = await api.put('users/profile/', data)
      user.value = response.data
      return response.data
    } catch (error) {
      throw error
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    fetchProfile,
    updateProfile,
    logout
  }
})
