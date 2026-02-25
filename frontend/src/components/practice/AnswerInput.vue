<template>
  <el-card class="answer-card">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><Edit /></el-icon>
        <span>你的答案</span>
      </div>
    </template>
    <el-form ref="formRef" :model="form" label-position="top">
      <el-form-item prop="answer">
        <el-input
          v-model="form.answer"
          type="textarea"
          :rows="10"
          placeholder="请输入你的答案..."
          class="answer-input"
          @input="$emit('update:answer', form.answer)"
        />
      </el-form-item>
      <el-form-item label="评分方式" prop="scoringMethod" v-if="showScoringMethod">
        <el-radio-group v-model="form.scoringMethod" class="scoring-method-group">
          <el-radio value="embedding" border>
            <el-icon><DataAnalysis /></el-icon>
            嵌入模型
          </el-radio>
          <el-radio value="deepseek" border>
            <el-icon><ChatDotRound /></el-icon>
            DeepSeek
          </el-radio>
          <el-radio value="both" border>
            <el-icon><TrendCharts /></el-icon>
            两者平均
          </el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="showSubmitButton">
        <el-button type="primary" @click="$emit('submit', form)" :loading="loading">
          <el-icon><Check /></el-icon>
          提交答案
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { Edit, DataAnalysis, ChatDotRound, TrendCharts, Check } from '@element-plus/icons-vue'

const props = defineProps({
  answer: {
    type: String,
    default: ''
  },
  showScoringMethod: {
    type: Boolean,
    default: true
  },
  showSubmitButton: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:answer', 'submit'])

const formRef = ref()
const form = reactive({
  answer: props.answer,
  scoringMethod: 'embedding'
})

defineExpose({
  validate: () => formRef.value?.validate(),
  reset: () => {
    form.answer = ''
    form.scoringMethod = 'embedding'
    formRef.value?.resetFields()
  }
})
</script>

<style scoped>
.answer-card {
  margin-bottom: 20px;
  background: #1e1e1e;
  border: 1px solid #3c3c3c;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 18px;
}

.answer-input {
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.answer-input :deep(.el-textarea__inner) {
  background: #252525;
  border-color: #3c3c3c;
  color: #e0e0e0;
}

.answer-input :deep(.el-textarea__inner):focus {
  border-color: #61dafb;
}

.scoring-method-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.scoring-method-group :deep(.el-radio.is-bordered) {
  background: #252525;
  border-color: #3c3c3c;
  color: #e0e0e0;
}

.scoring-method-group :deep(.el-radio.is-bordered:hover) {
  border-color: #61dafb;
}
</style>
