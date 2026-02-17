<template>
  <div class="code-detail-container">
    <div class="detail-header">
      <el-button
        @click="goBack"
        class="back-button code-font"
      >
        &lt;Back/&gt;
      </el-button>
      <div class="header-info">
        <h1 class="page-title code-font">{{ question?.title }}</h1>
        <div class="header-badges">
          <el-tag
            :type="getDifficultyType(question?.difficulty)"
            size="small"
            class="difficulty-badge"
          >
            {{ getDifficultyText(question?.difficulty) }}
          </el-tag>
          <el-tag
            type="info"
            size="small"
            class="language-badge code-font"
          >
            {{ question?.language_display }}
          </el-tag>
          <el-tag
            size="small"
            class="limit-badge code-font"
          >
            {{ question?.time_limit }}ms / {{ question?.memory_limit }}MB
          </el-tag>
        </div>
      </div>
      <div class="header-actions">
        <el-button
          @click="toggleBookmark"
          :type="isBookmarked ? 'warning' : 'default'"
          class="bookmark-button"
        >
          <el-icon><Star /></el-icon>
          {{ isBookmarked ? 'Bookmarked' : 'Bookmark' }}
        </el-button>
        <el-button
          @click="showNoteDialog = true"
          class="note-button"
        >
          <el-icon><Document /></el-icon>
          Note
        </el-button>
      </div>
    </div>

    <div class="detail-content">
      <div class="left-panel">
        <div class="section">
          <h3 class="section-title code-font">&lt;Description/&gt;</h3>
          <div class="description-content">
            <p>{{ question?.question?.title }}</p>
            <p v-if="question?.question?.explanation" class="explanation">
              {{ question?.question?.explanation }}
            </p>
          </div>
        </div>

        <div class="section">
          <h3 class="section-title code-font">&lt;FunctionSignature/&gt;</h3>
          <div class="function-signature code-font">
            <code>{{ question?.function_signature }}</code>
          </div>
        </div>

        <div class="section">
          <h3 class="section-title code-font">&lt;Examples/&gt;</h3>
          <div class="examples-section">
            <div
              v-for="(testCase, index) in sampleTestCases"
              :key="index"
              class="example-card"
            >
              <div class="example-header">
                <span class="example-label code-font">Example {{ index + 1 }}</span>
              </div>
              <div class="example-content">
                <div class="example-item">
                  <span class="example-label code-font">Input:</span>
                  <pre class="code-block">{{ formatJSON(testCase.input_data) }}</pre>
                </div>
                <div class="example-item">
                  <span class="example-label code-font">Output:</span>
                  <pre class="code-block">{{ formatJSON(testCase.expected_output) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="section">
          <h3 class="section-title code-font">&lt;Constraints/&gt;</h3>
          <ul class="constraints-list">
            <li class="constraint-item code-font">
              Time Limit: {{ question?.time_limit }}ms
            </li>
            <li class="constraint-item code-font">
              Memory Limit: {{ question?.memory_limit }}MB
            </li>
            <li class="constraint-item code-font">
              Total Test Cases: {{ question?.total_test_cases }}
            </li>
          </ul>
        </div>
      </div>

      <div class="right-panel">
        <div class="editor-section">
          <div class="editor-header">
            <h3 class="section-title code-font">&lt;Solution/&gt;</h3>
            <div class="editor-actions">
              <el-button
                size="small"
                @click="resetCode"
                class="code-font"
              >
                &lt;Reset/&gt;
              </el-button>
            </div>
          </div>
          <CodeEditor
            v-model="code"
            :language="question?.language"
            :height="'500px'"
            @change="handleCodeChange"
          />
        </div>

        <div class="submit-section">
          <el-button
            type="primary"
            size="large"
            :loading="submitting"
            @click="submitCode"
            class="submit-button code-font"
          >
            <span v-if="!submitting">&gt; Submit Code</span>
            <span v-else>Running...</span>
          </el-button>
        </div>

        <div class="result-section" v-if="submissionResult">
          <h3 class="section-title code-font">&lt;Result/&gt;</h3>
          <div class="result-card" :class="resultClass">
            <div class="result-header">
              <el-icon class="result-icon">
                <component :is="resultIcon" />
              </el-icon>
              <span class="result-status">{{ submissionResult.status_display }}</span>
            </div>
            <div class="result-stats">
              <div class="stat-item">
                <span class="stat-label code-font">Runtime:</span>
                <span class="stat-value code-font">{{ submissionResult.runtime }}ms</span>
              </div>
              <div class="stat-item">
                <span class="stat-label code-font">Memory:</span>
                <span class="stat-value code-font">{{ submissionResult.memory }}KB</span>
              </div>
              <div class="stat-item">
                <span class="stat-label code-font">Test Cases:</span>
                <span class="stat-value code-font">
                  {{ submissionResult.passed_test_cases }}/{{ submissionResult.total_test_cases }}
                </span>
              </div>
            </div>
            <div class="test-case-results" v-if="showTestResults">
              <div
                v-for="(result, index) in testCaseResults"
                :key="index"
                class="test-case-item"
                :class="{ 'failed': !result.passed }"
              >
                <div class="test-case-header">
                  <span class="test-case-label code-font">Test Case {{ index + 1 }}</span>
                  <el-icon v-if="result.passed" class="success-icon"><CircleCheck /></el-icon>
                  <el-icon v-else class="error-icon"><CircleClose /></el-icon>
                </div>
                <div v-if="result.error" class="error-message code-font">
                  {{ result.error }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="showNoteDialog"
      title="Note"
      width="600px"
      class="note-dialog"
    >
      <el-input
        v-model="noteContent"
        type="textarea"
        :rows="10"
        placeholder="Write your notes here..."
        class="note-input"
      />
      <template #footer>
        <el-button @click="showNoteDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveNote">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Star, Document, CircleCheck, CircleClose, Check, Close, Warning
} from '@element-plus/icons-vue'
import CodeEditor from '@/components/CodeEditor.vue'
import codeQuestionsApi from '@/api/codeQuestions'

const route = useRoute()
const router = useRouter()

const question = ref(null)
const code = ref('')
const submitting = ref(false)
const submissionResult = ref(null)
const isBookmarked = ref(false)
const showNoteDialog = ref(false)
const noteContent = ref('')
const sampleTestCases = ref([])

const resultClass = computed(() => {
  if (!submissionResult.value) return ''
  const status = submissionResult.value.status
  const classMap = {
    'accepted': 'success',
    'wrong_answer': 'error',
    'time_limit_exceeded': 'warning',
    'memory_limit_exceeded': 'warning',
    'runtime_error': 'error',
    'compile_error': 'error',
    'system_error': 'error'
  }
  return classMap[status] || 'info'
})

const resultIcon = computed(() => {
  if (!submissionResult.value) return null
  const status = submissionResult.value.status
  const iconMap = {
    'accepted': Check,
    'wrong_answer': Close,
    'time_limit_exceeded': Warning,
    'memory_limit_exceeded': Warning,
    'runtime_error': Close,
    'compile_error': Close,
    'system_error': Close
  }
  return iconMap[status] || Close
})

const testCaseResults = computed(() => {
  if (!submissionResult.value?.test_case_results) return []
  return Object.values(submissionResult.value.test_case_results)
})

const showTestResults = computed(() => {
  return submissionResult.value?.test_case_results &&
         Object.keys(submissionResult.value.test_case_results).length > 0
})

const fetchQuestion = async () => {
  try {
    const response = await codeQuestionsApi.getQuestion(route.params.id)
    question.value = response.data
    code.value = response.data.starter_code || response.data.template_code
    isBookmarked.value = response.data.user_bookmarked
    sampleTestCases.value = response.data.sample_test_cases || []
    
    if (response.data.user_note) {
      noteContent.value = response.data.user_note.content
    }
  } catch (error) {
    ElMessage.error('Failed to load question')
    console.error(error)
  }
}

const submitCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('Please write your code first')
    return
  }

  submitting.value = true
  submissionResult.value = null

  try {
    const response = await codeQuestionsApi.submitCode(
      route.params.id,
      code.value,
      question.value.language
    )
    submissionResult.value = response.data

    if (response.data.status === 'accepted') {
      ElMessage.success('Congratulations! Your code passed all test cases!')
    } else {
      ElMessage.warning(`Submission failed: ${response.data.status_display}`)
    }
  } catch (error) {
    ElMessage.error('Failed to submit code')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const toggleBookmark = async () => {
  try {
    const response = await codeQuestionsApi.bookmarkQuestion(route.params.id)
    isBookmarked.value = response.data.bookmarked
    ElMessage.success(response.data.message)
  } catch (error) {
    ElMessage.error('Failed to toggle bookmark')
    console.error(error)
  }
}

const saveNote = async () => {
  try {
    if (noteContent.value) {
      await codeQuestionsApi.updateQuestionNote(route.params.id, noteContent.value)
    } else {
      await codeQuestionsApi.createQuestionNote(route.params.id, noteContent.value)
    }
    showNoteDialog.value = false
    ElMessage.success('Note saved successfully')
  } catch (error) {
    ElMessage.error('Failed to save note')
    console.error(error)
  }
}

const resetCode = () => {
  code.value = question.value?.starter_code || question.value?.template_code || ''
}

const handleCodeChange = (value) => {
  code.value = value
}

const formatJSON = (jsonString) => {
  try {
    return JSON.stringify(JSON.parse(jsonString), null, 2)
  } catch {
    return jsonString
  }
}

const getDifficultyType = (difficulty) => {
  const types = { 1: 'success', 2: 'warning', 3: 'danger' }
  return types[difficulty] || 'info'
}

const getDifficultyText = (difficulty) => {
  const texts = { 1: 'Easy', 2: 'Medium', 3: 'Hard' }
  return texts[difficulty] || 'Unknown'
}

const goBack = () => {
  router.push('/code-practice')
}

onMounted(() => {
  fetchQuestion()
})
</script>

<style scoped>
.code-detail-container {
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
  gap: 16px;
}

.back-button {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.back-button:hover {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.header-info {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.header-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.difficulty-badge,
.language-badge,
.limit-badge {
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.detail-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.description-content {
  color: var(--text-secondary);
  line-height: 1.8;
}

.explanation {
  margin-top: 16px;
  padding: 16px;
  background: var(--bg-tertiary);
  border-left: 3px solid var(--accent-primary);
  border-radius: var(--radius-sm);
}

.function-signature {
  background: var(--code-bg);
  padding: 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  color: var(--code-text);
  font-size: 14px;
  overflow-x: auto;
}

.examples-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.example-card {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.example-header {
  padding: 12px 16px;
  background: var(--bg-hover);
  border-bottom: 1px solid var(--border-color);
}

.example-label {
  font-weight: 600;
  color: var(--text-secondary);
}

.example-content {
  padding: 16px;
}

.example-item {
  margin-bottom: 12px;
}

.example-item:last-child {
  margin-bottom: 0;
}

.code-block {
  background: var(--code-bg);
  padding: 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  color: var(--code-text);
  font-size: 13px;
  overflow-x: auto;
  margin-top: 8px;
}

.constraints-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.constraint-item {
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.constraint-item:last-child {
  margin-bottom: 0;
}

.editor-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.editor-actions {
  display: flex;
  gap: 8px;
}

.editor-actions :deep(.el-button) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
}

.editor-actions :deep(.el-button:hover) {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.submit-section {
  display: flex;
  justify-content: flex-end;
}

.submit-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
  border: none;
  transition: all 0.3s ease;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.result-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
}

.result-card {
  padding: 16px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.result-card.success {
  background: rgba(166, 227, 161, 0.1);
  border-color: var(--accent-success);
}

.result-card.error {
  background: rgba(243, 139, 168, 0.1);
  border-color: var(--accent-error);
}

.result-card.warning {
  background: rgba(249, 226, 175, 0.1);
  border-color: var(--accent-warning);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.result-icon {
  font-size: 24px;
}

.result-card.success .result-icon {
  color: var(--accent-success);
}

.result-card.error .result-icon {
  color: var(--accent-error);
}

.result-card.warning .result-icon {
  color: var(--accent-warning);
}

.result-status {
  font-size: 18px;
  font-weight: 600;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-muted);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.test-case-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.test-case-item {
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.test-case-item.failed {
  border-color: var(--accent-error);
  background: rgba(243, 139, 168, 0.1);
}

.test-case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.test-case-label {
  font-weight: 600;
  color: var(--text-secondary);
}

.success-icon {
  color: var(--accent-success);
}

.error-icon {
  color: var(--accent-error);
}

.error-message {
  color: var(--accent-error);
  font-size: 13px;
  padding: 8px;
  background: rgba(243, 139, 168, 0.1);
  border-radius: var(--radius-sm);
}

.note-input :deep(.el-textarea__inner) {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-family: var(--font-mono);
}

@media (max-width: 1200px) {
  .detail-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .code-detail-container {
    padding: 16px;
  }

  .detail-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
  }

  .result-stats {
    grid-template-columns: 1fr;
  }
}
</style>
