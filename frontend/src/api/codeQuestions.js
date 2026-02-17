import api from '@/api'

export default {
  getQuestions(params = {}) {
    return api({
      url: 'code-questions/questions/',
      method: 'get',
      params
    })
  },

  getQuestion(id) {
    return api({
      url: `code-questions/questions/${id}/`,
      method: 'get'
    })
  },

  createQuestion(data) {
    return api({
      url: 'code-questions/questions/',
      method: 'post',
      data
    })
  },

  updateQuestion(id, data) {
    return api({
      url: `code-questions/questions/${id}/`,
      method: 'put',
      data
    })
  },

  deleteQuestion(id) {
    return api({
      url: `code-questions/questions/${id}/`,
      method: 'delete'
    })
  },

  bookmarkQuestion(id) {
    return api({
      url: `code-questions/questions/${id}/bookmark/`,
      method: 'post'
    })
  },

  getQuestionNote(id) {
    return api({
      url: `code-questions/questions/${id}/note/`,
      method: 'get'
    })
  },

  createQuestionNote(id, content) {
    return api({
      url: `code-questions/questions/${id}/note/`,
      method: 'post',
      data: { content }
    })
  },

  updateQuestionNote(id, content) {
    return api({
      url: `code-questions/questions/${id}/note/`,
      method: 'put',
      data: { content }
    })
  },

  submitCode(id, code, language) {
    return api({
      url: `code-questions/questions/${id}/submit/`,
      method: 'post',
      data: { code, language }
    })
  },

  getBookmarks(params = {}) {
    return api({
      url: 'code-questions/questions/bookmarks/',
      method: 'get',
      params
    })
  },

  getStatistics() {
    return api({
      url: 'code-questions/questions/statistics/',
      method: 'get'
    })
  },

  getSubmissions(params = {}) {
    return api({
      url: 'code-questions/submissions/',
      method: 'get',
      params
    })
  },

  getLatestSubmissions(params = {}) {
    return api({
      url: 'code-questions/submissions/latest/',
      method: 'get',
      params
    })
  }
}
