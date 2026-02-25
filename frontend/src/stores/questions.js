import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useQuestionsStore = defineStore('questions', () => {
  const questions = ref([])
  const categories = ref([])
  const loading = ref(false)
  const error = ref(null)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(12)

  const filters = ref({
    search: '',
    category: null,
    difficulty: null
  })

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  async function fetchQuestions(page = 1, params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/questions/questions/', {
        params: {
          ...filters.value,
          page,
          page_size: pageSize.value,
          ...params
        }
      })
      questions.value = response.data.results || response.data
      total.value = response.data.count || questions.value.length
      currentPage.value = page
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchQuestion(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/questions/questions/${id}/`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchCategories() {
    try {
      const response = await api.get('/questions/categories/')
      categories.value = response.data.results || response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  async function createQuestion(data) {
    try {
      const response = await api.post('/questions/questions/', data)
      questions.value.unshift(response.data)
      total.value += 1
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function updateQuestion(id, data) {
    try {
      const response = await api.put(`/questions/questions/${id}/`, data)
      const index = questions.value.findIndex(q => q.id === id)
      if (index !== -1) {
        questions.value[index] = response.data
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function deleteQuestion(id) {
    try {
      await api.delete(`/questions/questions/${id}/`)
      questions.value = questions.value.filter(q => q.id !== id)
      total.value -= 1
    } catch (error) {
      throw error
    }
  }

  function setFilters(newFilters) {
    Object.assign(filters.value, newFilters)
  }

  function resetFilters() {
    filters.value = {
      search: '',
      category: null,
      difficulty: null
    }
  }

  return {
    questions,
    categories,
    loading,
    error,
    total,
    currentPage,
    pageSize,
    filters,
    totalPages,
    fetchQuestions,
    fetchQuestion,
    fetchCategories,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    setFilters,
    resetFilters
  }
})
