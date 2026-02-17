<template>
  <div class="code-practice-container">
    <div class="practice-header">
      <div class="header-left">
        <h1 class="page-title code-font">&lt;CodePractice/&gt;</h1>
        <p class="page-subtitle">程序员代码练习平台</p>
      </div>
      <div class="header-actions">
        <el-button
          type="primary"
          @click="showBookmarks"
          class="code-font"
        >
          &lt;Bookmarks/&gt;
        </el-button>
      </div>
    </div>

    <div class="filters-section">
      <div class="filter-group">
        <el-input
          v-model="searchQuery"
          placeholder="Search questions..."
          clearable
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="filter-group">
        <el-select
          v-model="selectedLanguage"
          placeholder="Language"
          clearable
          class="filter-select"
        >
          <el-option label="All" value="" />
          <el-option label="Python" value="python" />
          <el-option label="Java" value="java" />
          <el-option label="JavaScript" value="javascript" />
          <el-option label="C++" value="cpp" />
          <el-option label="Go" value="go" />
          <el-option label="Rust" value="rust" />
        </el-select>
      </div>
      <div class="filter-group">
        <el-select
          v-model="selectedDifficulty"
          placeholder="Difficulty"
          clearable
          class="filter-select"
        >
          <el-option label="All" value="" />
          <el-option label="Easy" value="1" />
          <el-option label="Medium" value="2" />
          <el-option label="Hard" value="3" />
        </el-select>
      </div>
    </div>

    <div class="questions-list" v-loading="loading">
      <div
        v-for="question in questions"
        :key="question.id"
        class="question-card"
        @click="goToQuestion(question.id)"
      >
        <div class="question-header">
          <div class="question-title code-font">
            {{ question.title }}
          </div>
          <div class="question-badges">
            <el-tag
              :type="getDifficultyType(question.difficulty)"
              size="small"
              class="difficulty-badge"
            >
              {{ getDifficultyText(question.difficulty) }}
            </el-tag>
            <el-tag
              type="info"
              size="small"
              class="language-badge code-font"
            >
              {{ question.language_display }}
            </el-tag>
          </div>
        </div>
        <div class="question-meta">
          <span class="meta-item code-font">
            <el-icon><Clock /></el-icon>
            {{ question.time_limit }}ms
          </span>
          <span class="meta-item code-font">
            <el-icon><Cpu /></el-icon>
            {{ question.memory_limit }}MB
          </span>
          <span class="meta-item code-font" v-if="question.category_name">
            <el-icon><Folder /></el-icon>
            {{ question.category_name }}
          </span>
        </div>
      </div>

      <el-empty
        v-if="!loading && questions.length === 0"
        description="No questions found"
      />
    </div>

    <div class="pagination-section" v-if="total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Clock, Cpu, Folder } from '@element-plus/icons-vue'
import codeQuestionsApi from '@/api/codeQuestions'

const router = useRouter()

const loading = ref(false)
const questions = ref([])
const searchQuery = ref('')
const selectedLanguage = ref('')
const selectedDifficulty = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const fetchQuestions = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (selectedLanguage.value) {
      params.language = selectedLanguage.value
    }
    if (selectedDifficulty.value) {
      params.difficulty = selectedDifficulty.value
    }

    const response = await codeQuestionsApi.getQuestions(params)
    questions.value = response.data.results || response.data
    total.value = response.data.count || questions.value.length
  } catch (error) {
    ElMessage.error('Failed to load questions')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goToQuestion = (id) => {
  router.push(`/code-practice/${id}`)
}

const showBookmarks = () => {
  router.push('/code-practice/bookmarks')
}

const getDifficultyType = (difficulty) => {
  const types = { 1: 'success', 2: 'warning', 3: 'danger' }
  return types[difficulty] || 'info'
}

const getDifficultyText = (difficulty) => {
  const texts = { 1: 'Easy', 2: 'Medium', 3: 'Hard' }
  return texts[difficulty] || 'Unknown'
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchQuestions()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchQuestions()
}

watch([searchQuery, selectedLanguage, selectedDifficulty], () => {
  currentPage.value = 1
  fetchQuestions()
})

onMounted(() => {
  fetchQuestions()
})
</script>

<style scoped>
.code-practice-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.header-actions :deep(.el-button) {
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  border: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.header-actions :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.filters-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 200px;
}

.search-input :deep(.el-input__wrapper) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: var(--accent-primary);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 2px rgba(137, 180, 250, 0.2);
}

.filter-select :deep(.el-select__wrapper) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.questions-list {
  display: grid;
  gap: 16px;
}

.question-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.question-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.question-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  margin-right: 16px;
}

.question-badges {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.difficulty-badge,
.language-badge {
  font-weight: 600;
}

.question-meta {
  display: flex;
  gap: 16px;
  align-items: center;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .code-practice-container {
    padding: 16px;
  }

  .practice-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .filters-section {
    flex-direction: column;
  }

  .filter-group {
    min-width: 100%;
  }

  .question-header {
    flex-direction: column;
    gap: 12px;
  }

  .question-badges {
    flex-wrap: wrap;
  }
}
</style>
