<template>
  <el-card class="question-card">
    <template #header>
      <div class="card-header">
        <el-icon class="header-icon"><Document /></el-icon>
        <span>题目描述</span>
      </div>
    </template>
    <div class="question-description">
      <p>{{ title }}</p>
      <div v-if="content" class="question-content" v-html="content"></div>
    </div>
  </el-card>
</template>

<script setup>
import { Document } from '@element-plus/icons-vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  content: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.question-card {
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

.question-description {
  line-height: 1.8;
  color: #e0e0e0;
}

.question-description p {
  margin: 0 0 10px 0;
}

.question-content {
  padding: 15px;
  background: #252525;
  border-radius: 4px;
  border-left: 3px solid #61dafb;
}
</style>
