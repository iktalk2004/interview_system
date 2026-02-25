import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useQuestionStore = defineStore('question', () => {
  const questions = ref([])
  const currentQuestion = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchQuestions(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('questions/', { params })
      questions.value = response.data.results || response.data
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
      const response = await api.get(`questions/${id}/`)
      currentQuestion.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createQuestion(data) {
    try {
      const response = await api.post('questions/', data)
      questions.value.push(response.data)
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function updateQuestion(id, data) {
    try {
      const response = await api.put(`questions/${id}/`, data)
      const index = questions.value.findIndex(q => q.id === id)
      if (index !== -1) {
        questions.value[index] = response.data
      }
      if (currentQuestion.value?.id === id) {
        currentQuestion.value = response.data
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function deleteQuestion(id) {
    try {
      await api.delete(`questions/${id}/`)
      questions.value = questions.value.filter(q => q.id !== id)
      if (currentQuestion.value?.id === id) {
        currentQuestion.value = null
      }
    } catch (error) {
      throw error
    }
  }

  function clearCurrentQuestion() {
    currentQuestion.value = null
  }

  return {
    questions,
    currentQuestion,
    loading,
    error,
    fetchQuestions,
    fetchQuestion,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    clearCurrentQuestion
  }
})
