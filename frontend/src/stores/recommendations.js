import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useRecommendationsStore = defineStore('recommendations', () => {
  const recommendations = ref([])
  const loading = ref(false)
  const error = ref(null)
  const recommendationType = ref('hybrid')

  const stats = computed(() => {
    const total = recommendations.value.length
    const viewed = recommendations.value.filter(r => r.is_viewed).length
    const answered = recommendations.value.filter(r => r.is_answered).length
    const avgScore = total > 0
      ? recommendations.value.reduce((sum, r) => sum + r.score, 0) / total
      : 0

    return { total, viewed, answered, avg_score: avgScore }
  })

  async function fetchRecommendations(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/recommender/recommendations/generate_recommendations/', {
        params: {
          type: recommendationType.value,
          n: 10,
          min_similarity: 0.1,
          ...params
        }
      })
      recommendations.value = response.data.recommendations
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
      await api.post(`/recommender/recommendations/${id}/mark_viewed/`)
      const rec = recommendations.value.find(r => r.id === id)
      if (rec) {
        rec.is_viewed = true
      }
    } catch (error) {
      throw error
    }
  }

  async function markAllAsViewed() {
    try {
      await api.post('/recommender/recommendations/mark_all_viewed/')
      recommendations.value.forEach(r => {
        r.is_viewed = true
      })
    } catch (error) {
      throw error
    }
  }

  async function clearOldRecommendations(days = 7) {
    try {
      const response = await api.post('/recommender/recommendations/clear_old_recommendations/', {
        days
      })
      recommendations.value = []
      return response.data
    } catch (error) {
      throw error
    }
  }

  function setRecommendationType(type) {
    recommendationType.value = type
  }

  function clearRecommendations() {
    recommendations.value = []
  }

  return {
    recommendations,
    loading,
    error,
    recommendationType,
    stats,
    fetchRecommendations,
    markAsViewed,
    markAllAsViewed,
    clearOldRecommendations,
    setRecommendationType,
    clearRecommendations
  }
})
