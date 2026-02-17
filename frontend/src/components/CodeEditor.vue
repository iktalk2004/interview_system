<template>
  <div class="code-editor-container">
    <div class="editor-header">
      <div class="language-selector">
        <el-select
          v-model="selectedLanguage"
          size="small"
          @change="handleLanguageChange"
          class="code-font"
        >
          <el-option
            v-for="lang in languages"
            :key="lang.value"
            :label="lang.label"
            :value="lang.value"
          />
        </el-select>
      </div>
      <div class="editor-actions">
        <el-button
          size="small"
          @click="resetCode"
          class="code-font"
        >
          &lt;Reset/&gt;
        </el-button>
        <el-button
          size="small"
          @click="formatCode"
          class="code-font"
        >
          &lt;Format/&gt;
        </el-button>
      </div>
    </div>
    <div class="editor-wrapper" ref="editorRef"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as monaco from 'monaco-editor'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'python'
  },
  readonly: {
    type: Boolean,
    default: false
  },
  height: {
    type: String,
    default: '500px'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const editorRef = ref(null)
const editor = ref(null)
const selectedLanguage = ref(props.language)

const languages = [
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'cpp', label: 'C++' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' }
]

const initEditor = () => {
  editor.value = monaco.editor.create(editorRef.value, {
    value: props.modelValue,
    language: props.language,
    theme: 'vs-dark',
    readOnly: props.readonly,
    minimap: { enabled: true },
    fontSize: 14,
    fontFamily: "'Fira Code', 'Consolas', 'Monaco', 'Courier New', monospace",
    lineNumbers: 'on',
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 4,
    wordWrap: 'on',
    formatOnPaste: true,
    formatOnType: true
  })

  editor.value.onDidChangeModelContent(() => {
    const value = editor.value.getValue()
    emit('update:modelValue', value)
    emit('change', value)
  })
}

const handleLanguageChange = (lang) => {
  monaco.editor.setModelLanguage(editor.value.getModel(), lang)
}

const resetCode = () => {
  editor.value.setValue(props.modelValue)
}

const formatCode = () => {
  editor.value.getAction('editor.action.formatDocument').run()
}

const updateEditorValue = (value) => {
  if (editor.value) {
    editor.value.setValue(value)
  }
}

watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getValue() !== newValue) {
    updateEditorValue(newValue)
  }
})

onMounted(() => {
  initEditor()
})

onBeforeUnmount(() => {
  if (editor.value) {
    editor.value.dispose()
  }
})

defineExpose({
  updateEditorValue,
  getValue: () => editor.value?.getValue(),
  getEditor: () => editor.value
})
</script>

<style scoped>
.code-editor-container {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--code-bg);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.language-selector {
  flex: 1;
  max-width: 200px;
}

.language-selector :deep(.el-input__wrapper) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.language-selector :deep(.el-input__inner) {
  color: var(--text-primary);
  font-family: var(--font-mono);
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
  transition: all 0.3s ease;
}

.editor-actions :deep(.el-button:hover) {
  background: var(--bg-hover);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.editor-wrapper {
  height: v-bind(height);
  min-height: 400px;
}

@media (max-width: 768px) {
  .editor-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .language-selector {
    max-width: none;
  }

  .editor-actions {
    justify-content: flex-end;
  }
}
</style>
