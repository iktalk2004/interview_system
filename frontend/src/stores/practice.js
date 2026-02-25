import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const usePracticeStore = defineStore('practice', () => {
  const interactions = ref([])
  const currentInteraction = ref(null)
  const history = ref([])
  const loading = ref(false)
  const error = ref(null)

  const completedCount = computed(() => 
    interactions.value.filter(i => i.is_submitted).length
  )

  const favoriteCount = computed(() => 
    interactions.value.filter(i => i.is_favorite).length
  )

  async function fetchInteractions(params = {}) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('practice/interactions/', { params })
      interactions.value = response.data.results || response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchInteraction(id) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`practice/interactions/${id}/`)
      currentInteraction.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createInteraction(data) {
    try {
      const response = await api.post('practice/interactions/', data)
      interactions.value.push(response.data)
      currentInteraction.value = response.data
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function updateInteraction(id, data) {
    try {
      const response = await api.put(`practice/interactions/${id}/`, data)
      const index = interactions.value.findIndex(i => i.id === id)
      if (index !== -1) {
        interactions.value[index] = response.data
      }
      if (currentInteraction.value?.id === id) {
        currentInteraction.value = response.data
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function submitInteraction(id, data) {
    try {
      const response = await api.put(`practice/interactions/${id}/`, {
        ...data,
        is_submitted: true
      })
      const index = interactions.value.findIndex(i => i.id === id)
      if (index !== -1) {
        interactions.value[index] = response.data
      }
      if (currentInteraction.value?.id === id) {
        currentInteraction.value = response.data
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function toggleFavorite(id) {
    try {
      await api.post(`practice/interactions/${id}/favorite/`)
      const interaction = interactions.value.find(i => i.id === id)
      if (interaction) {
        interaction.is_favorite = !interaction.is_favorite
      }
      if (currentInteraction.value?.id === id) {
        currentInteraction.value.is_favorite = !currentInteraction.value.is_favorite
      }
    } catch (error) {
      throw error
    }
  }

  async function resetInteraction(id) {
    try {
      await api.post(`practice/interactions/${id}/reset_interaction/`)
      const index = interactions.value.findIndex(i => i.id === id)
      if (index !== -1) {
        interactions.value[index].answer = ''
        interactions.value[index].is_submitted = false
        interactions.value[index].score = null
      }
      if (currentInteraction.value?.id === id) {
        currentInteraction.value.answer = ''
        currentInteraction.value.is_submitted = false
        currentInteraction.value.score = null
      }
    } catch (error) {
      throw error
    }
  }

  async function fetchHistory() {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('practice/interactions/history/')
      history.value = response.data.results || response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  async function scoreByEmbedding(id) {
    try {
      const response = await api.post(`practice/interactions/${id}/embedding_score/`)
      const index = interactions.value.findIndex(i => i.id === id)
      if (index !== -1) {
        interactions.value[index].score = response.data.score
      }
      if (currentInteraction.value?.id === id) {
        currentInteraction.value.score = response.data.score
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  async function scoreByDeepSeek(id) {
    try {
      const response = await api.post(`practice/interactions/${id}/deepseek_score/`)
      const index = interactions.value.findIndex(i => i.id === id)
      if (index !== -1) {
        interactions.value[index].score = response.data.score
      }
      if (currentInteraction.value?.id === id) {
        currentInteraction.value.score = response.data.score
      }
      return response.data
    } catch (error) {
      throw error
    }
  }

  function clearCurrentInteraction() {
    currentInteraction.value = null
  }

  return {
    interactions,
    currentInteraction,
    history,
    loading,
    error,
    completedCount,
    favoriteCount,
    fetchInteractions,
    fetchInteraction,
    createInteraction,
    updateInteraction,
    submitInteraction,
    toggleFavorite,
    resetInteraction,
    fetchHistory,
    scoreByEmbedding,
    scoreByDeepSeek,
    clearCurrentInteraction
  }
})
