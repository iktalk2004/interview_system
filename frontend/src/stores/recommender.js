import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useRecommenderStore = defineStore('recommender', () => {
  const recommendations = ref([])
  const preferences = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const unreadCount = computed(() => 
    recommendations.value.filter(r => !r.is_viewed).length
  )

  const answeredCount = computed(() => 
    recommendations.value.filter(r => r.is_answered).length
  )

  async function fetchRecommendations(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('recommender/recommendations/', { params })
      recommendations.value = response.data.results || response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function generateRecommendations(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('recommender/recommendations/generate_recommendations/', { params })
      recommendations.value = response.data.recommendations || []
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function markAsViewed(id) {
    try {
      await api.post(`recommender/recommendations/${id}/viewed/`)
      const rec = recommendations.value.find(r => r.id === id)
      if (rec) {
        rec.is_viewed = true
      }
    } catch (error) {
      throw error
    }
  }

  async function markAsAnswered(id) {
    try {
      await api.post(`recommender/recommendations/${id}/answered/`)
      const rec = recommendations.value.find(r => r.id === id)
      if (rec) {
        rec.is_answered = true
      }
    } catch (error) {
      throw error
    }
  }

  async function markAllViewed() {
    try {
      await api.post('recommender/recommendations/mark_all_viewed/')
      recommendations.value.forEach(r => {
        r.is_viewed = true
      })
    } catch (error) {
      throw error
    }
  }

  async function fetchPreferences() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('recommender/preferences/')
      preferences.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updatePreferences() {
    loading.value = true
    error.value = null
    try {
      const response = await api.post('recommender/preferences/update/')
      preferences.value = response.data.preference
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function clearOldRecommendations(days = 7) {
    try {
      const response = await api.post('recommender/recommendations/clear_old_recommendations/', { days })
      recommendations.value = recommendations.value.filter(
        r => !response.data.deleted_ids.includes(r.id)
      )
      return response.data
    } catch (error) {
      throw error
    }
  }

  function clearRecommendations() {
    recommendations.value = []
  }

  return {
    recommendations,
    preferences,
    loading,
    error,
    unreadCount,
    answeredCount,
    fetchRecommendations,
    generateRecommendations,
    markAsViewed,
    markAsAnswered,
    markAllViewed,
    fetchPreferences,
    updatePreferences,
    clearOldRecommendations,
    clearRecommendations
  }
})
